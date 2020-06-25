import boto3
from boto3.dynamodb.conditions import Key, Attr
import csv, sys, argparse
from datetime import datetime
import json
import os
import urllib3
import glob

LOGTYPE_ERROR = 'ERROR'
LOGTYPE_INFO = 'INFO'
LOGTYPE_DEBUG = 'DEBUG'

# sdb logging parameters
domain_name = "serratus-batch"
# other parameters
nb_threads = str(4)

# from serratus-batch-dl
def fastp(accession,folder,sdb,extra_args=""):
    # Separate fastq files into paired- and single-end reads
    #based on https://github.com/hawkjo/sequencetools/blob/master/clean_fastqs_in_subdirs.py
    fastq_files = glob.glob(folder+"/"+accession+"*.fastq")
    pe_fastq_files = []
    se_fastq_files = []
    for fname in fastq_files:
        if fname[-8:] == '_1.fastq':
            # If first of pair is found, add both
            fname2 = fname[:-8] + '_2.fastq'
            if fname2 not in fastq_files:
                print('Unpaired _1 file: ' + fname)
                sdb_log(sdb,accession,'read_unpaired1','True')
                se_fastq_files.append(fname)
            else:
                pe_fastq_files.append((fname, fname2))
        elif fname[-8:] == '_2.fastq':
            # If second of pair is found, test for presence of first, but do nothing
            fname1 = fname[:-8] + '_1.fastq'
            if fname1 not in fastq_files:
                print('Unpaired _2 file: ' + fname)
                sdb_log(sdb,accession,'read_unpaired2','True')
                se_fastq_files.append(fname)
        else:
            se_fastq_files.append(fname)

    os.system('rm -f ' + accession + '.fastq') # should be unnecessary
    for f1, f2 in pe_fastq_files:
        os.system(' '.join(["/fastp", "--thread", "4", "--trim_poly_x", "-i", f1, "-I", f2, "--stdout", extra_args, ">>", accession + ".fastq"]))
    for f in se_fastq_files:
        os.system(' '.join(["/fastp", "--thread", "4", "--trim_poly_x", "-i", f,            "--stdout", extra_args, ">>", accession + ".fastq"]))
 
def process_file(accession, region, assembler, already_on_s3):
    global domain_name

    urllib3.disable_warnings()
    s3 = boto3.client('s3')
    sdb = boto3.client('sdb', region_name=region)
    outputBucket = "serratus-public"
    s3_folder          = "assemblies/other/" + accession + "." + assembler + "/"
    s3_assembly_folder = "assemblies/contigs/"        

    def checkv(input_file, suffix=""):
        checkv_prefix = accession + "." + assembler  + suffix + ".checkv"

        # run checkV on contigs
        start_time = datetime.now()
        os.system(' '.join(["checkv","end_to_end", input_file, checkv_prefix, "-t", nb_threads,"-d","/mnt/serratus-data/checkv-db-v0.6"]))
        checkv_time = datetime.now() - start_time
        sdb_log(sdb,accession,assembler+suffix+'_checkv_time',checkv_time.seconds)

        # extract contigs using CheckV results
        contigs_filtered_filename = accession + "." + assembler + suffix + ".checkv_filtered.fa" 
        os.system(' '.join(["samtools","faidx",input_file]))
        os.system(' '.join(["grep","-f","/checkv_corona_entries.txt",checkv_prefix + "/completeness.tsv","|","python","/extract_contigs.py",input_file,contigs_filtered_filename]))

        # compress result (maybe it doesn't exist, e.g. if checkv didn't find anything)
        os.system(' '.join(["touch",checkv_prefix + "/completeness.tsv"]))
        os.system(' '.join(["touch",checkv_prefix + "/contamination.tsv"]))
        os.system(' '.join(["touch",checkv_prefix + "/quality_summary.tsv"]))
        os.system(' '.join(["gzip -f",checkv_prefix + "/completeness.tsv"]))
        os.system(' '.join(["gzip -f",checkv_prefix + "/contamination.tsv"]))
        os.system(' '.join(["gzip -f",checkv_prefix + "/quality_summary.tsv"]))

        os.system("sed -i 's/>/>" + accession + "." + assembler + "." + "/g' " + contigs_filtered_filename)
        s3.upload_file(contigs_filtered_filename, outputBucket, s3_assembly_folder + contigs_filtered_filename, ExtraArgs={'ACL': 'public-read'})
        try:
            # these files might not exist if checkv failed (sometimes when contigs file is too small)
            s3.upload_file(checkv_prefix + "/completeness.tsv.gz", outputBucket, s3_folder + checkv_prefix +".completeness.tsv.gz", ExtraArgs={'ACL': 'public-read'})
            s3.upload_file(checkv_prefix + "/contamination.tsv.gz", outputBucket, s3_folder + checkv_prefix +".contamination.tsv.gz", ExtraArgs={'ACL': 'public-read'})
            s3.upload_file(checkv_prefix + "/quality_summary.tsv.gz", outputBucket, s3_folder + checkv_prefix + ".quality_summary.tsv.gz", ExtraArgs={'ACL': 'public-read'})
        except:
            print("can't upload completeness.tsv.gz/quality_summary.tsv.gz to s3")

    print("region - " + region, flush=True)
    startBatchTime = datetime.now()

    # go to /tmp (important, that's where local storage / nvme is)
    os.chdir("/mnt/serratus-data")
    os.system(' '.join(["pwd"]))
    
    # check free space
    os.system(' '.join(["df", "-h", "."]))

    local_file = accession + ".fastq"
    if not already_on_s3:
        print("downloading reads from SRA to EBS..")
        startTime = datetime.now()
        
        os.system('mkdir -p out/')
        
        prefetch_start = datetime.now()
        os.system('prefetch --max-size 35G '+accession)
        prefetch_time = datetime.now() - prefetch_start 
        sdb_log(sdb,accession,'prefetch_time',int(prefetch_time.seconds))

        os.system('mkdir -p tmp/')
        pfqdump_start = datetime.now()
        os.system('/parallel-fastq-dump --skip-technical --split-e --outdir out/ --tmpdir tmp/ --threads 4 --sra-id '+accession)
        pfqdump_time = datetime.now() - pfqdump_start
        sdb_log(sdb,accession,'pfqdump_time',int(pfqdump_time.seconds))

        files = os.listdir(os.getcwd() + "/out/")
        print("after fastq-dump, dir listing of out/", files)
        inputDataFn = accession+".inputdata.txt"
        g = open(inputDataFn,"w")
        for f in files:
            print("file: " + f + " size: " + str(os.stat("out/"+f).st_size), flush=True)
            g.write(f + " " + str(os.stat("out/"+f).st_size)+"\n")
        g.close()

        # potential todo: there is opportunity to use mkfifo and speed-up parallel-fastq-dump -> bbduk step
        # as per https://github.com/ababaian/serratus/blob/master/containers/serratus-dl/run_dl-sra.sh#L26

        # run fastp
        fastp_start = datetime.now()
        fastp(accession,"out/", sdb)

        if os.stat(accession+".fastq").st_size == 0:
            # fastp output is empty, most likely those reads have dummy quality values. retry.
            print("retrying fastp without quality filtering", flush=True)
            sdb_log(sdb,accession,'fastp_noqual','True')
            fastp(accession,"out/",sdb,"--disable_quality_filtering")
 
        if os.stat(accession+".fastq").st_size == 0:
            # fastp output is STILL empty. could be that read1 or read2 are too short. consider both unpaired
            print("retrying fastp unpaired mode", flush=True)
            os.system('mv out/' + accession + '_1.fastq out/' + accession + '_a.fastq')
            os.system('mv out/' + accession + '_2.fastq out/' + accession + '_b.fastq')
            sdb_log(sdb,accession,'fastp_unpaired','True')
            fastp(accession,"out/",sdb,"--disable_quality_filtering")
           
        if os.stat(accession+".fastq").st_size == 0:
            print("fastp produced empty output even without quality filtering", flush=True)
            sdb_log(sdb,accession,'fastp_empty','True')
            exit(1)

        print("fastp done, now uploading to S3")
        fastp_time = datetime.now() - fastp_start 
        sdb_log(sdb,accession,'fastp_time',int(fastp_time.seconds))

        # upload filtered reads to s3
        upload_to_s3 = False
        if upload_to_s3:
            outputBucketDl = "serratus-rayan"
            upload_start = datetime.now()
            s3.upload_file(accession+".fastq", outputBucketDl, "reads/"+accession+".fastq")
            upload_time = datetime.now() - upload_start
            sdb_log(sdb,accession,'upload_time',int(upload_time.seconds))
 
        # cleanup. #(important when using a local drive)
        os.system(' '.join(["rm","-f","out/"+accession+"*.fastq"]))
        os.system(' '.join(["rm","-f","public/sra/"+accession+".sra"]))
        os.system('rm -Rf ' + accession) # seems to be the right path

        endTime = datetime.now()
        diffTime = endTime - startTime
        sdb_log(sdb,accession,'batch_assembly_dl_time',int(diffTime.seconds))
        sdb_log(sdb,accession,'batch_assembly_dl_date',str(datetime.now()))
        logMessage(accession, "Serratus-batch-dl processing time - " + str(diffTime.seconds), LOGTYPE_INFO) 

    else:
        inputBucket = "serratus-rayan"
        s3.download_file(inputBucket, "reads/" + accession + ".fastq", local_file)
        print("downloaded file from", "s3://" + inputBucket + "/reads/" + accession + ".fastq", "to",local_file, flush=True)

        inputDataFn = accession+".inputdata.txt"
        g = open(inputDataFn,"w")
        g.write(accession + ".fastq is " + str(os.stat(local_file).st_size)+" bytes \n")
        g.close()
        
        # compute number of lines and add it to the log file
        os.system(' '.join(["wc", "-l", local_file,"| cut -d' ' -f1 |","tee",accession+".number_lines.txt"]))
        os.system(' '.join(["echo", "-n", "nbreads: ", "|", "cat", "-", accession + ".number_lines.txt", ">>", inputDataFn]))
        
        # log number of reads
        with open(accession+".number_lines.txt") as f:
            nb_reads = str(int(f.read())/4)
            file_size = str(os.stat(local_file).st_size)
            sdb_log(sdb,accession,'nb_reads',nb_reads)
            sdb_log(sdb,accession,'file_size',file_size)

    # run minia
    if assembler == "minia":
        os.system('mkdir -p /mnt/serratus-data/' + accession + '_minia')
        os.chdir("/mnt/serratus-data/" + accession + "_minia")

        statsFn = accession + ".minia.txt"
        min_abundance = 2 if os.stat("../"+local_file).st_size > 100000000 else 1 # small min-abundance for small samples (<100MB)
        start_time = datetime.now()
        os.system(' '.join(["/minia", "-kmer-size", "31", "-abundance-min", str(min_abundance), "-in", "../" + local_file,"|","tee", statsFn]))
        minia_time = datetime.now() - start_time
        sdb_log(sdb,accession,'minia_time',minia_time.seconds)

        os.system('mv ' + accession + '.contigs.fa ' + accession + '.minia.contigs.fa')
        contigs_filename = accession+ ".minia.contigs.fa"

        os.system('mv ' + contigs_filename + ' /mnt/serratus-data/')
        os.system('mv ' + statsFn          + ' /mnt/serratus-data/')
        os.system('rm -Rf /mnt/serratus-data/' + accession + '_minia') # proper cleanup
        os.chdir("/mnt/serratus-data/")

    elif assembler == "coronaspades":
        statsFn = accession + ".coronaspades.txt"
        
        # determine if paired-end
        os.system(' '.join(['testformat.sh',accession+'.fastq','>>',inputDataFn]))
        with open(inputDataFn) as f:
            paired_end = "paired" in str(f.read())
        input_type = "--12" if paired_end else "-s"

        k_values = "auto"

        start_time = datetime.now()
        os.system(' '.join(["/SPAdes-3.15.0-corona-2020-06-18/bin/coronaspades.py", input_type, local_file,"-k",k_values,"-o",accession+"_coronaspades"]))
        coronaspades_time = datetime.now() - start_time
        sdb_log(sdb,accession,'coronaspades_time',coronaspades_time.seconds)
        
        #scaffolds_filename = accession+ ".coronaspades.scaffolds.fa"
        contigs_filename = accession+ ".coronaspades.contigs.fa"

        os.system(' '.join(['cp',accession+"_coronaspades/spades.log",statsFn]))
        os.system(' '.join(['cp',accession+"_coronaspades/scaffolds.fasta",contigs_filename]))
            
        gene_clusters_filename = accession+ "_coronaspades/gene_clusters.fasta"
        os.system('touch ' + gene_clusters_filename)
        s3.upload_file(gene_clusters_filename, outputBucket, s3_folder + accession + ".coronaspades.gene_clusters.fa", ExtraArgs={'ACL': 'public-read'})
        
        domain_graph_filename = accession+ "_coronaspades/domain_graph.dot"
        os.system('touch ' + domain_graph_filename)
        s3.upload_file(domain_graph_filename, outputBucket, s3_folder + accession + ".coronaspades.domain_graph.dot", ExtraArgs={'ACL': 'public-read'})
        
        bgc_statistics_filename = accession+ "_coronaspades/bgc_statistics.txt"
        os.system('touch ' + bgc_statistics_filename)
        s3.upload_file(bgc_statistics_filename, outputBucket, s3_folder + accession + ".coronaspades.bgc_statistics.txt", ExtraArgs={'ACL': 'public-read'})
        
        os.system('gzip -f ' +  accession + "_coronaspades/assembly_graph_with_scaffolds.gfa")
        assembly_graph_with_scaffolds_filename = accession+ "_coronaspades/assembly_graph_with_scaffolds.gfa.gz"
        s3.upload_file(assembly_graph_with_scaffolds_filename, outputBucket, s3_folder + accession + ".coronaspades.assembly_graph_with_scaffolds.gfa.gz", ExtraArgs={'ACL': 'public-read'})

        # run CheckV on gene_clusters
        checkv(gene_clusters_filename, ".gene_clusters") 
   
    elif assembler == "bcalm":
        domain_name = "unitigs-batch"

    else:
        print("unknown assembler:",assembler)

    # run mfc 
    os.system(' '.join(["/MFCompressC",contigs_filename]))
    
    compressed_contigs_filename = contigs_filename + ".mfc"

    # upload compressed contigs and stats to S3
    # as per https://github.com/ababaian/serratus/issues/162
    s3.upload_file(compressed_contigs_filename, outputBucket, s3_folder + os.path.basename(compressed_contigs_filename), ExtraArgs={'ACL': 'public-read'})

    if assembler != "bcalm":
        s3.upload_file(inputDataFn, outputBucket, s3_folder + inputDataFn, ExtraArgs={'ACL': 'public-read'})
        s3.upload_file(statsFn, outputBucket, s3_folder + statsFn, ExtraArgs={'ACL': 'public-read'})

        # run checkv (which also uploads)
        checkv(contigs_filename) 
    
    #cleanup
    print("cleaning up, checking free space")
    os.chdir("/mnt/serratus-data")
    os.system(' '.join(["rm","-Rf",accession+"*"]))
    os.system(' '.join(["df", "-h", "."]))

    # finishing up
    endBatchTime = datetime.now()
    diffTime = endBatchTime - startBatchTime
    sdb_log(sdb,accession, assembler + '_total_batch_time',diffTime.seconds)
    sdb_log(sdb,accession, assembler + '_date',str(datetime.now()))
    logMessage(accession, "File processing time - " + str(diffTime.seconds), LOGTYPE_INFO) 


def main():
    accession = ""
    region = "us-east-1"
    assembler = "minia"
    already_on_s3 = False
   
    if "Accession" in os.environ:
        accession = os.environ.get("Accession")
    if "Region" in os.environ:
        region = os.environ.get("Region")
    if "Assembler" in os.environ:
        assembler = os.environ.get("Assembler")
    if "AlreadyOnS3" in os.environ:
        already_on_s3 = os.environ.get("AlreadyOnS3") == 'True'

    if len(accession) == 0:
        exit("This script needs an environment variable Accession set to something")

    logMessage(accession, 'accession: ' + accession+  "  region: " + region + "   assembler: " + assembler + "   already on s3? " + str(already_on_s3), LOGTYPE_INFO)

    process_file(accession, region, assembler, already_on_s3)


def logMessage(fileName, message, logType):
    try:
        logMessageDetails = constructMessageFormat(fileName, message, "", logType)
        
        if logType == "INFO" or logType == "ERROR":
            print(logMessageDetails, flush=True)
        elif logType == "DEBUG":
            try:
                if os.environ.get('DEBUG') == "LOGTYPE":
                   print(logMessageDetails, flush=True) 
            except KeyError:
                pass
    except Exception as ex:
        logMessageDetails = constructMessageFormat(fileName, message, "Error occurred at Batch_processor.logMessage" + str(ex), logType)
        print(logMessageDetails)


def constructMessageFormat(fileName, message, additionalErrorDetails, logType):
    if additionalErrorDetails != "":
        return "fileName: " + fileName + " " + logType + ": " + message + " Additional Details -  " + additionalErrorDetails
    else:
        return "fileName: " + fileName + " " + logType + ": " + message

def sdb_log(
        sdb, item_name, name, value,
        region='us-east-1',
    ):
        """
        Insert a single record to simpledb domain.
        PARAMS:
        @item_name: unique string for this record.
        @attributes = [
            {'Name': 'duration', 'Value': str(duration), 'Replace': True},
            {'Name': 'date', 'Value': str(date), 'Replace': True},
        ]
        """
        try:
            status = sdb.put_attributes(
                DomainName=domain_name,
                ItemName=str(item_name),
                Attributes=[{'Name':str(name), 'Value':str(value), 'Replace': True}]
            )
        except Exception as e:
            print("SDB put_attribute error:",str(e),'domain_name',domain_name,'item_name',item_name)
            status = False
        try:
            if status['ResponseMetadata']['HTTPStatusCode'] == 200:
                return True
            else:
                print("SDB log error:",status['ResponseMetadata']['HTTPStatusCode'])
                return False
        except:
            print("SDB status structure error, status:",str(status))
            return False

if __name__ == '__main__':
   main()

import boto3
from boto3.dynamodb.conditions import Key, Attr
import csv, sys, argparse
from datetime import datetime
import json
import os
import urllib3

LOGTYPE_ERROR = 'ERROR'
LOGTYPE_INFO = 'INFO'
LOGTYPE_DEBUG = 'DEBUG'

def process_file(accession, region, assembler, already_on_s3):
    #try:
    if True:
        urllib3.disable_warnings()
        s3 = boto3.client('s3')
        sdb = boto3.client('sdb')
        
        print("region - " + region)
        startTime = datetime.now()

        # go to /tmp (important, that's where local storage / nvme is)
        os.chdir("/mnt/serratus-data")
        os.system(' '.join(["pwd"]))
        
        # check free space
        os.system(' '.join(["df", "-h", "."]))

        local_file = accession + ".fastq"
        if not already_on_s3:
            # download reads from accession
            os.system('mkdir -p out/')
            os.system('prefetch '+accession)
            os.system('/parallel-fastq-dump --split-files --outdir out/ --threads 4 --sra-id '+accession)

            files = os.listdir(os.getcwd() + "/out/")
            print("after fastq-dump, dir listing", files)
            inputDataFn = accession+".inputdata.txt"
            g = open(inputDataFn,"w")
            for f in files:
                g.write(f + " " + str(os.stat("out/"+f).st_size)+"\n")
            g.close()

            # potential todo: there is opportunity to use mkfifo and speed-up parallel-fastq-dump -> bbduk step
            # as per https://github.com/ababaian/serratus/blob/master/containers/serratus-dl/run_dl-sra.sh#L26

            # run fastp
            #os.system(' '.join(["cat","out/*.fastq","|","/fastp", "--trim_poly_x", "--stdin", "-o", accession + ".fastq"]))
            # run bbduk
            # https://www.protocols.io/view/illumina-fastq-filtering-gydbxs6
            # https://github.com/ababaian/serratus/issues/102
            # bbduk.sh trimpolya=15 qtrim=rl trimq=10 in=<left> in2=<right> out=<out-left> out2=<out-right> threads=<N>
            os.system(' '.join(["cat","out/*.fastq","|","bbduk.sh", "in=stdin.fq","int=f","trimpolya=15","qtrim=rl","trimq=10","threads=4", "-out="+ local_file]))

            # remove orig reads to free up space
            os.system(' '.join(["rm", "out/*"]))
        else:
            inputBucket = "serratus-rayan"
            s3.download_file(inputBucket, "reads/" + accession + ".fastq", local_file)
            print("downloaded file from", "s3://" + inputBucket + "/reads/" + accession + ".fastq", "to",local_file)

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
            statsFn = accession + ".minia.txt"
            min_abundance = 2 if os.stat(local_file).st_size > 100000000 else 1 # small min-abundance for small samples (<100MB)
            start_time = datetime.now()
            os.system(' '.join(["/minia", "-kmer-size", "31", "-abundance-min", str(min_abundance), "-in", local_file,"|","tee", statsFn]))
            minia_time = datetime.now() - start_time
            sdb_log(sdb,accession,'minia_time',minia_time.seconds)
                
            contigs_filename = accession+ ".contigs.fa"
            compressed_contigs_suffix = ".minia.contigs.fa.mfc"

        # run mfc 
        os.system(' '.join(["/MFCompressC",contigs_filename]))
        
        compressed_contigs_filename = contigs_filename + ".mfc"
    
        # run checkV on contigs
        checkv_prefix = accession + "." + assembler + ".checkv"
        start_time = datetime.now()
        os.system(' '.join(["checkv","end_to_end", contigs_filename, checkv_prefix, "-t","4","-d","/mnt/serratus-data/checkv-db-v0.6"]))
        checkv_time = datetime.now() - start_time
        sdb_log(sdb,accession,'checkv_time',checkv_time.seconds)
 

        # extract contigs using CheckV results
        contigs_filtered_filename = accession + ".minia.checkv_filtered.fa" 
        os.system(' '.join(["samtools","faidx",contigs_filename]))
        os.system(' '.join(["grep","-f","/checkv_corona_entries.txt",checkv_prefix + "/completeness.tsv","|","python","/extract_contigs.py",contigs_filename,contigs_filtered_filename]))

        # compress result (maybe it doesn't exist, e.g. if checkv didn't find anything)
        os.system(' '.join(["touch",checkv_prefix + "/completeness.tsv"]))
        os.system(' '.join(["touch",checkv_prefix + "/contamination.tsv"]))
        os.system(' '.join(["touch",checkv_prefix + "/quality_summary.tsv"]))
        os.system(' '.join(["gzip",checkv_prefix + "/completeness.tsv"]))
        os.system(' '.join(["gzip",checkv_prefix + "/contamination.tsv"]))
        os.system(' '.join(["gzip",checkv_prefix + "/quality_summary.tsv"]))


        # upload contigs and other stuff to s3
        # as per https://github.com/ababaian/serratus/issues/162
        outputBucket = "serratus-public"
        s3_folder          = "assemblies/other/" + accession + "." + assembler + "/"
        s3_assembly_folder = "assemblies/contigs/" 
        s3.upload_file(compressed_contigs_filename, outputBucket, s3_folder + os.path.basename(compressed_contigs_filename), ExtraArgs={'ACL': 'public-read'})
        s3.upload_file(contigs_filtered_filename, outputBucket, s3_assembly_folder + contigs_filtered_filename, ExtraArgs={'ACL': 'public-read'})
        s3.upload_file(inputDataFn, outputBucket, s3_folder + inputDataFn, ExtraArgs={'ACL': 'public-read'})
        s3.upload_file(statsFn, outputBucket, s3_folder + statsFn, ExtraArgs={'ACL': 'public-read'})
        try:
            # these files might not exist if checkv failed (sometimes when contigs file is too small)
            s3.upload_file(checkv_prefix + "/completeness.tsv.gz", outputBucket, s3_folder + checkv_prefix +".completeness.tsv.gz", ExtraArgs={'ACL': 'public-read'})
            s3.upload_file(checkv_prefix + "/contamination.tsv.gz", outputBucket, s3_folder + checkv_prefix +".contamination.tsv.gz", ExtraArgs={'ACL': 'public-read'})
            s3.upload_file(checkv_prefix + "/quality_summary.tsv.gz", outputBucket, s3_folder + checkv_prefix + ".quality_summary.tsv.gz", ExtraArgs={'ACL': 'public-read'})
        except:
            print("can't upload completeness.tsv.gz/quality_summary.tsv.gz to s3")
 

        endTime = datetime.now()
        diffTime = endTime - startTime
        sdb_log(sdb,accession,'minia_total_batch_time',diffTime.seconds)
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
        already_on_s3 = bool(os.environ.get("AlreadyOnS3"))

    if len(accession) == 0:
        exit("This script needs an environment variable Accession set to something")

    logMessage(accession, 'accession: ' + accession+  "  region: " + region + "   assembler: " + assembler + "   already on s3? " + str(already_on_s3), LOGTYPE_INFO)

    process_file(accession, region, assembler, already_on_s3)


def logMessage(fileName, message, logType):
    try:
        logMessageDetails = constructMessageFormat(fileName, message, "", logType)
        
        if logType == "INFO" or logType == "ERROR":
            print(logMessageDetails)
        elif logType == "DEBUG":
            try:
                if os.environ.get('DEBUG') == "LOGTYPE":
                   print(logMessageDetails) 
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
        region='us-east-1', domain_name='serratus-batch',
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
        except:
            status = False
        try:
            if status['ResponseMetadata']['HTTPStatusCode'] == 200:
                return True
            else:
                print("SDB log error:",status['ResponseMetadata']['HTTPStatusCode'])
                return False
        except:
            print("SDB log error")
            return False

if __name__ == '__main__':
   main()

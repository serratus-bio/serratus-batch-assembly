import boto3
from boto3.dynamodb.conditions import Key, Attr
import csv, sys, argparse
from datetime import datetime
import json
import os
import urllib3
import glob
from utils import sdb_log

import darth
import reads
import utils
import serra

LOGTYPE_ERROR = 'ERROR'
LOGTYPE_INFO = 'INFO'
LOGTYPE_DEBUG = 'DEBUG'

# other parameters
nb_threads = str(8)

def download_coronaspades_assembly(accession,outputBucket,s3_folder,s3_assembly_folder, s3, sdb):
    # grab assemblies from S3
    checkv_filtered_contigs = accession + ".coronaspades.gene_clusters.checkv_filtered.fa" 
    serratax_contigs_input = checkv_filtered_contigs
    try:
        s3.download_file(outputBucket, s3_assembly_folder + serratax_contigs_input, serratax_contigs_input)
        gene_clusters_file = accession + ".coronaspades.gene_clusters.fa"
        s3.download_file(outputBucket, s3_folder + gene_clusters_file, gene_clusters_file)
    except:
        print("couldn't download coronaspades assembly from S3, stopping",flush=True)
        exit(1)
    return checkv_filtered_contigs, gene_clusters_file


def coronaspades(accession, inputDataFn, local_file, assembler, outputBucket, s3_folder, s3_assembly_folder, s3, sdb):
    global nb_threads
    version = "SPAdes-3.15.0-corona-2020-07-15-mi"

    statsFn = accession + ".coronaspades.txt"
    contigs_filename = accession+ ".coronaspades.contigs.fa"
   
    # first, determine if we need to run coronaspades _at all_. maybe it was already assembled (or failed to assemble) with latest eersion
    has_logfile = s3_file_exists(s3, outputBucket, s3_folder + statsFn)
    exit_reason = None
    last_k_value = None
    older_version = False
    assembly_already_made = False
    spades_version = ""
    if has_logfile:
        s3.download_file(outputBucket, s3_folder + statsFn, statsFn)
        coronaspades_log = open(statsFn).readlines()
        for line in coronaspades_log:
            if "Cannot allocate memory" in line:
                print("log memory error:",line,flush=True)
                exit_reason = "memory error"
                break
            if "Thank you for using SPAdes!" in line:
                exit_reason = "thankyou"
            if "Domain graph construction constructed, total vertices: 0, edges: 0" in line:
                exit_reason = "nodomain"
                break
            if "SPAdes version:" in line:
                spades_version = line.strip()
            if line.startswith("Command line:"):
                print("log command line:",line,flush=True)
                if version not in line:
                    older_version = True
                    # break # don't break until we get the last k value
            if line.startswith("K values to be used:"):
                last_k_value = int(line.split()[-1].replace('[','').replace(']',''))

        print("spades log available, most notable finishing message:",exit_reason,flush=True)

    if exit_reason is not None and older_version == False:
        print("spades was already run,",spades_version,flush=True)
        print("downloading raw and checkv_filtered gene_clusters.fa",flush=True)
        checkv_filtered_contigs, gene_clusters_file = download_coronaspades_assembly(accession,outputBucket,s3_folder,s3_assembly_folder, s3, sdb)
        os.system('ls -l ' + accession + '*.fa')
        assembly_already_made = True
        return checkv_filtered_contigs, assembly_already_made

    # determine if paired-end
    os.system(' '.join(['testformat.sh',accession+'.fastq','>>',inputDataFn]))
    with open(inputDataFn) as f:
        paired_end = "paired" in str(f.read())
    input_type = "--12" if paired_end else "-s"

    k_values = "auto"
    extra_args = []

    if older_version:

        # special treatment for an older version: get asm graph and rerun from last k value, as per Anton instructions
        print("older run detected, with",spades_version,flush=True)
        print("rerunning with old assembly graph",flush=True)
        k_values = str(last_k_value)
        assembly_graph = accession + ".coronaspades.assembly_graph_with_scaffolds.gfa"
        s3.download_file(outputBucket, s3_folder + assembly_graph + ".gz",  assembly_graph + ".gz" )
        os.system("gunzip " + assembly_graph + ".gz")
        
        # corner case: need to make sure GFA file has a L line
        has_L = False
        with open(assembly_graph) as assembly_graph_file:
            for line in assembly_graph_file:
                if line.startswith('L'):
                    has_L = True
                    break

        if has_L:
            extra_args = ['--assembly-graph',assembly_graph]

    start_time = datetime.now()
    os.system(' '.join(["/%s/bin/coronaspades.py" % version, input_type, local_file,"-k",k_values,"-t",nb_threads,"-o",accession+"_coronaspades"] + extra_args))
    coronaspades_time = datetime.now() - start_time
    sdb_log(sdb,accession,'coronaspades_time',coronaspades_time.seconds)
    

    os.system(' '.join(['cp',accession+"_coronaspades/spades.log",statsFn]))
    os.system(' '.join(['cp',accession+"_coronaspades/scaffolds.fasta",contigs_filename]))
        
    gene_clusters_filename = accession+ "_coronaspades/gene_clusters.fasta"
    s3.upload_file(gene_clusters_filename, outputBucket, s3_folder + accession + ".coronaspades.gene_clusters.fa", ExtraArgs={'ACL': 'public-read'})
    
    domain_graph_filename = accession+ "_coronaspades/domain_graph.dot"
    s3.upload_file(domain_graph_filename, outputBucket, s3_folder + accession + ".coronaspades.domain_graph.dot", ExtraArgs={'ACL': 'public-read'})
    
    bgc_statistics_filename = accession+ "_coronaspades/bgc_statistics.txt"
    s3.upload_file(bgc_statistics_filename, outputBucket, s3_folder + accession + ".coronaspades.bgc_statistics.txt", ExtraArgs={'ACL': 'public-read'})
    
    os.system('gzip -f ' +  accession + "_coronaspades/assembly_graph_with_scaffolds.gfa")
    assembly_graph_with_scaffolds_filename = accession+ "_coronaspades/assembly_graph_with_scaffolds.gfa.gz"
    s3.upload_file(assembly_graph_with_scaffolds_filename, outputBucket, s3_folder + accession + ".coronaspades.assembly_graph_with_scaffolds.gfa.gz", ExtraArgs={'ACL': 'public-read'})

    # run CheckV on gene_clusters
    checkv_filtered_contigs = checkv(gene_clusters_filename, accession, assembler, outputBucket, s3_folder, s3_assembly_folder, s3, sdb, ".gene_clusters")
    return checkv_filtered_contigs, assembly_already_made


def checkv(input_file, accession, assembler, outputBucket, s3_folder, s3_assembly_folder, s3, sdb, suffix=""):
    global nb_threads
    checkv_prefix = accession + "." + assembler  + suffix + ".checkv"
    contigs_filtered_filename = accession + "." + assembler + suffix + ".checkv_filtered.fa" 

    if (not os.path.exists(input_file)) or \
           os.stat(input_file).st_size == 0:
            print("empty input for checkv",input_file,flush=True)
            return contigs_filtered_filename

    print("running checkv on",input_file,"(non-empty input)",flush=True)

    # run checkV on contigs
    start_time = datetime.now()
    os.system(' '.join(["checkv","end_to_end", input_file, checkv_prefix, "-t", nb_threads,"-d","/serratus-data/checkv-db-v0.6"]))
    checkv_time = datetime.now() - start_time
    sdb_log(sdb,accession,assembler+suffix+'_checkv_time',checkv_time.seconds)

    # extract contigs using CheckV results
    os.system(' '.join(["samtools","faidx",input_file]))
    os.system(' '.join(["grep","-f","/checkv_corona_entries.txt",checkv_prefix + "/completeness.tsv","|","python","/extract_contigs.py",input_file,contigs_filtered_filename]))

    # compress result (maybe it doesn't exist, e.g. if checkv didn't find anything)
    os.system(' '.join(["touch",checkv_prefix + "/completeness.tsv"]))
    os.system(' '.join(["touch",checkv_prefix + "/contamination.tsv"]))
    os.system(' '.join(["touch",checkv_prefix + "/quality_summary.tsv"]))
    os.system(' '.join(["gzip -f",checkv_prefix + "/completeness.tsv"]))
    os.system(' '.join(["gzip -f",checkv_prefix + "/contamination.tsv"]))
    os.system(' '.join(["gzip -f",checkv_prefix + "/quality_summary.tsv"]))

    #light cleanup
    os.system(' '.join(["rm -Rf",checkv_prefix + "/tmp"]))

    os.system("sed -i 's/>/>" + accession + "." + assembler + "." + "/g' " + contigs_filtered_filename)
    s3.upload_file(contigs_filtered_filename, outputBucket, s3_assembly_folder + contigs_filtered_filename, ExtraArgs={'ACL': 'public-read'})
    try:
        # these files might not exist if checkv failed (sometimes when contigs file is too small)
        s3.upload_file(checkv_prefix + "/completeness.tsv.gz", outputBucket, s3_folder + checkv_prefix +".completeness.tsv.gz", ExtraArgs={'ACL': 'public-read'})
        s3.upload_file(checkv_prefix + "/contamination.tsv.gz", outputBucket, s3_folder + checkv_prefix +".contamination.tsv.gz", ExtraArgs={'ACL': 'public-read'})
        s3.upload_file(checkv_prefix + "/quality_summary.tsv.gz", outputBucket, s3_folder + checkv_prefix + ".quality_summary.tsv.gz", ExtraArgs={'ACL': 'public-read'})
    except:
        print("can't upload completeness.tsv.gz/quality_summary.tsv.gz to s3",flush=True)

    return contigs_filtered_filename


def process_file(accession, region, assembler, force_redownload, with_darth, with_serra):

    urllib3.disable_warnings()
    s3 = boto3.client('s3')
    sdb = boto3.client('sdb', region_name=region)
    outputBucket = "serratus-public"
    s3_folder          = "assemblies/other/" + accession + "." + assembler + "/"
    s3_assembly_folder = "assemblies/contigs/"        
    inputDataFn = accession+".inputdata.txt"

    print("region - " + region, flush=True)
    startBatchTime = datetime.now()

    # go to workdir
    os.chdir("/serratus-data")
    os.system(' '.join(["pwd"]))
    
    # check free space
    os.system(' '.join(["df", "-h", "."]))
    
    # check if reads were already available
    reads.get_reads(accession, s3, force_redownload, sdb, nb_threads, inputDataFn)

    local_file = accession + ".fastq"
    # run minia
    if assembler == "minia":
        os.system('mkdir -p /serratus-data/' + accession + '_minia')
        os.chdir("/serratus-data/" + accession + "_minia")

        statsFn = accession + ".minia.txt"
        min_abundance = 2 if os.stat("../"+local_file).st_size > 100000000 else 1 # small min-abundance for small samples (<100MB)
        start_time = datetime.now()
        os.system(' '.join(["/minia", "-kmer-size", "31", "-abundance-min", str(min_abundance), "-in", "../" + local_file,"|","tee", statsFn]))
        minia_time = datetime.now() - start_time
        sdb_log(sdb,accession,'minia_time',minia_time.seconds)

        os.system('mv ' + accession + '.contigs.fa ' + accession + '.minia.contigs.fa')
        contigs_filename = accession+ ".minia.contigs.fa"

        os.system('mv ' + contigs_filename + ' /serratus-data/')
        os.system('mv ' + statsFn          + ' /serratus-data/')
        os.system('rm -Rf /serratus-data/' + accession + '_minia') # proper cleanup
        os.chdir("/serratus-data/")
        
        serratax_contigs_input = None # minia didn't get piped to the rest

    elif assembler == "coronaspades":
        checkv_filtered_contigs, assembly_already_made = coronaspades(accession,inputDataFn, local_file, assembler, outputBucket, s3_folder, s3_assembly_folder, s3, sdb)

        # sets some filenames
        statsFn = accession + ".coronaspades.txt"
        contigs_filename = accession+ ".coronaspades.contigs.fa"
        serratax_contigs_input = checkv_filtered_contigs
   
    elif assembler == "bcalm":
        pass

    else:
        print("unknown assembler:",assembler,flush=True)

    if not assembly_already_made:
        # run mfc 
        os.system(' '.join(["/MFCompressC",contigs_filename]))
        
        compressed_contigs_filename = contigs_filename + ".mfc"

        # upload compressed contigs and stats to S3
        # as per https://github.com/ababaian/serratus/issues/162
        s3.upload_file(compressed_contigs_filename, outputBucket, s3_folder + os.path.basename(compressed_contigs_filename), ExtraArgs={'ACL': 'public-read'})

        # for all assemblers (except in unitigs mode)
        if assembler != "bcalm":
            s3.upload_file(inputDataFn, outputBucket, s3_folder + inputDataFn, ExtraArgs={'ACL': 'public-read'})
            s3.upload_file(statsFn, outputBucket, s3_folder + statsFn, ExtraArgs={'ACL': 'public-read'})

            # run checkv on contigs (which also uploads)
            #checkv(contigs_filename, accession, assembler, outputBucket, s3_folder, s3_assembly_folder, s3, sdb, "")
            # I decided against running it, because, it took lots of time on some larger contigs file, and also, never used the result.

    if (not os.path.exists(serratax_contigs_input)) or \
           os.stat(serratax_contigs_input).st_size == 0:
            print("empty input for annotation, skipping",serratax_contigs_input,flush=True)
            with_serra = False
            with_darth = False

    if with_serra:
        # Serratax and Serraplace 
        serra.serra(accession, serratax_contigs_input, s3, s3_folder, outputBucket)

    if with_darth:
        # Darth
        darth.darth(accession, serratax_contigs_input, s3, s3_folder, outputBucket, has_reads=True)

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
    force_redownload = False
    with_darth = True
    with_serra = True
   
    if "Accession" in os.environ:
        accession = os.environ.get("Accession")
    if "Region" in os.environ:
        region = os.environ.get("Region")
    if "Assembler" in os.environ:
        assembler = os.environ.get("Assembler")
    if "ForceRedownload" in os.environ:
        force_redownload = os.environ.get("ForceRedownload") == 'True'
    if "Darth" in os.environ:
        with_darth = os.environ.get("Darth") == 'True'
    if "Serra" in os.environ:
        with_serra = os.environ.get("Serra") == 'True'

    if len(accession) == 0:
        exit("This script needs an environment variable Accession set to something")

    logMessage(accession, 'accession: ' + accession+  "  region: " + region + "   assembler: " + assembler + "   force_redownload? " + str(force_redownload)  + "  with_darth? " + str(with_darth) + "   with_serra? " + str(with_serra), LOGTYPE_INFO)

    try:
        process_file(accession, region, assembler, force_redownload, with_darth, with_serra)
    except Exception as ex:
        print("Exception occurred during process_file() with arguments", accession, region, assembler, force_redownload, with_darth, with_serra,flush=True) 
        print(ex,flush=True)
        import traceback
        traceback.print_exc()

    #cleanup
    # it is important that this code isn't in process_file() as that function may stop for any reason
    print("cleaning up, checking free space",flush=True)
    os.chdir("/serratus-data")
    os.system(' '.join(["ls","-Rl",accession+"*"])) 
    os.system(' '.join(["rm","-Rf",accession+"*"])) 
    os.system(' '.join(["df", "-h", "."]))



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
        print(logMessageDetails,flush=True)


def constructMessageFormat(fileName, message, additionalErrorDetails, logType):
    if additionalErrorDetails != "":
        return "fileName: " + fileName + " " + logType + ": " + message + " Additional Details -  " + additionalErrorDetails
    else:
        return "fileName: " + fileName + " " + logType + ": " + message

if __name__ == '__main__':
   main()

import boto3
from boto3.dynamodb.conditions import Key, Attr
import csv, sys, time, argparse
from datetime import datetime
import json
import os
import sys
from operator import itemgetter, attrgetter
from time import sleep
import urllib3
import json

LOGTYPE_ERROR = 'ERROR'
LOGTYPE_INFO = 'INFO'
LOGTYPE_DEBUG = 'DEBUG'

def process_file(accession, region):
    #try:
    if True:
        urllib3.disable_warnings()
        s3 = boto3.client('s3')
        
        print("region - " + region)
        startTime = datetime.now()

        # go to /tmp (important, that's where local storage / nvme is)
        os.chdir("/tmp")
        os.system(' '.join(["pwd"]))
        
        # check free space
        os.system(' '.join(["df", "-h", "."]))

        # download reads from accession
        os.system('mkdir -p out/')
        os.system('prefetch '+accession)
        os.system('../parallel-fastq-dump --split-files --outdir out/ --threads 4 --sra-id '+accession)

        files = os.listdir(os.getcwd() + "/out/")
        print("after fastq-dump, dir listing", files)
        inputDataFn = accession+".inputdata.txt"
        g = open(inputDataFn,"w")
        for f in files:
            g.write(f + " " + str(os.stat(f).st_size)+"\n")
        g.close()

        # potential todo: there is opportunity to use mkfifo and speed-up parallel-fastq-dump -> bbduk step
        # as per https://github.com/ababaian/serratus/blob/master/containers/serratus-dl/run_dl-sra.sh#L26

        # TODO replace with bbduk
        # https://www.protocols.io/view/illumina-fastq-filtering-gydbxs6
        # https://github.com/ababaian/serratus/issues/102
        # run fastp
        os.system(' '.join(["cat","out/*.fastq","|","../fastp", "--trim_poly_x", "--stdin", "-o", accession + ".fastq"]))
        
        # remove orig reads to free up space
        os.system(' '.join(["rm", "out/*"]))

        # run minia
        miniaStatsFn = accession + ".minia.txt"
        min_abundance = 2 if os.stat(accession+".fastq").st_size > 100000000 else 1 # small min-abundance for small samples (<100MB)
        os.system(' '.join(["../minia", "-kmer-size", "31", "-abundance-min", str(min_abundance), "-in", accession + ".fastq","|","tee", miniaStatsFn]))
        
        contigs_filename = accession+ ".contigs.fa"

        # run mfc 
        os.system(' '.join(["../MFCompressC",contigs_filename]))
        
        compressed_contigs_filename = contigs_filename + ".mfc"

        # run checkV on minia contigs
        os.system(' '.join(["checkv","end_to_end",contigs_filename,accession + "_checkv","-t","4","-d","/checkv-db-v0.6"]))
        os.system(' '.join(["gzip",accession + "_checkv/completeness.tsv"]))
        os.system(' '.join(["gzip",accession + "_checkv/quality_summary.tsv"]))

        # upload contigs and other stuff to s3
        outputBucket = "serratus-assemblies"
        s3.upload_file(compressed_contigs_filename, outputBucket, accession + ".minia.contigs.fa.mfc")
        s3.upload_file(inputDataFn, outputBucket, inputDataFn)
        s3.upload_file(miniaStatsFn, outputBucket, miniaStatsFn)
        try:
            # these files might not exist if checkv failed (sometimes when contigs file is too small)
            s3.upload_file(accession + "_checkv/completeness.tsv.gz", outputBucket, accession + ".checkv.completeness.tsv.gz")
            s3.upload_file(accession + "_checkv/quality_summary.tsv.gz", outputBucket, accession + ".checkv.quality_summary.tsv.gz")
        except:
            print("can't upload completeness.tsv.gz/quality_summary.tsv.gz to s3")
 

        endTime = datetime.now()
        diffTime = endTime - startTime
        logMessage(accession, "File processing time - " + str(diffTime.seconds), LOGTYPE_INFO) 


def main():
    accession = ""
    region = "us-east-1"
   
    if "Accession" in os.environ:
        accession = os.environ.get("Accession")
    if "Region" in os.environ:
        region = os.environ.get("Region")

    if len(accession) == 0:
        exit("This script needs an environment variable Accession set to something")

    logMessage(accession, 'parameters: ' + accession+  "  " + region, LOGTYPE_INFO)

    process_file(accession,region)


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

if __name__ == '__main__':
   main()

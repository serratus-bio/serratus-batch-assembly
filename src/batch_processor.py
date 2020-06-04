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
        
        prefix = fileName
        print("region - " + region)
        startTime = datetime.now()

        # go to /tmp (important, that's where local storage / nvme is)
        os.chdir("/tmp")
        
        # check free space
        os.system(' '.join(["df", "-h", "."]))

        # download reads from accession
        os.system('mkdir out/')
        os.system('../parallel-fastq-dump --split-files --outdir out/ --threads 4 --sra-id '+accession)
        print("downloaded file to",local_file)

        # potential todo: there is opportunity to use mkfifo and speed-up parallel-fastq-dump -> bbduk step
        # as per https://github.com/ababaian/serratus/blob/master/containers/serratus-dl/run_dl-sra.sh#L26

        # TODO replace with bbduk
        # https://www.protocols.io/view/illumina-fastq-filtering-gydbxs6
        # https://github.com/ababaian/serratus/issues/102
        # run fastp
        os.system(' '.join(["cat","out/*.fastq","|","../fastp", "--trim_poly_x", "--stdin", "-o", "filtered.fastq"]))
        
        # remove orig reads to free up space
        os.system(' '.join(["rm", "out/*"]))

        # run minia
        os.system(' '.join(["../minia", "-kmer-size", "31", "-in", "filtered.fastq"]))
        
        contigs_filename = '.'.join(local_file.split('.')[:-1])+".contigs.fa"

        # run mfc 
        os.system(' '.join(["../MFCompressC",contigs_filename]))
        
        compressed_contigs_filename = contigs_filename + ".mfc"
        
        # upload contigs to s3
        outputBucket = "serratus-assemblies"
        s3.upload_file(compressed_contigs_filename, outputBucket, compressed_contigs_filename)

        # delete original file, maybe
        if delete_original:
            logMessage(fileName, "Deleting original file", LOGTYPE_INFO) 
            s3.delete_object(Bucket = inputBucket, Key = fileName)

        endTime = datetime.now()
        diffTime = endTime - startTime
        logMessage(fileName, "File processing time - " + str(diffTime.seconds), LOGTYPE_INFO) 

    #except Exception as ex:
    #    logMessage(fileName, "Error processing files:" + str(ex), LOGTYPE_ERROR)  

def main():
    accession = ""
    region = "us-east-1"
   
    if "Accession" in os.environ:
        accession = os.environ.get("Accession")
    if "Region" in os.environ:
        region = os.environ.get("Region")

    logMessage(fileName, 'parameters: ' + accession+  "  " + reg, LOGTYPE_INFO)

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

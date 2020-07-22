import boto3
from boto3.dynamodb.conditions import Key, Attr
import csv, sys, argparse
from datetime import datetime
import json
import os
import urllib3
import glob

import darth
import serra
import reads

LOGTYPE_ERROR = 'ERROR'
LOGTYPE_INFO = 'INFO'
LOGTYPE_DEBUG = 'DEBUG'

# other parameters
nb_threads = str(8)

def process_file(contigs, accession, region):

    urllib3.disable_warnings()
    s3 = boto3.client('s3')
    sdb = boto3.client('sdb', region_name=region)
    inputBucket = "serratus-rayan"
    outputBucket = "serratus-public"
    s3_folder = "seq/cov5/annotations.nt_otus.id99/"
    inputDataFn = accession+".inputdata.txt"

    print("region - " + region, flush=True)
    print("accession - " + accession, flush=True)
    # check free space
    os.system(' '.join(["df", "-h", "."]))

    startBatchTime = datetime.now()
    
    os.chdir("/serratus-data")

    contigs_filename = os.path.basename(contigs)
    s3.download_file(inputBucket, contigs, contigs_filename)

    os.system("ls -l " + contigs_filename)
    
    # basic: if it's a xRR accession, get the raeds.
    has_reads = False
    if accession[1:3] == 'RR':
        print("getting reads",flush=True)
        force_redownload = False
        reads.get_reads(accession, s3, s3_folder, outputBucket, force_redownload, sdb, nb_threads, inputDataFn)
        has_reads = True
        s3_folder = "assemblies/annotations/"

    serra.serra(accession, contigs_filename, s3, s3_folder, outputBucket)
    darth.darth(accession, contigs_filename, s3, s3_folder, outputBucket, has_reads=has_reads)

    # finishing up
    endBatchTime = datetime.now()
    diffTime = endBatchTime - startBatchTime
    print(accession, "File processing time - " + str(diffTime.seconds), flush=True) 


def main():
    contigs = ""
    region = "us-east-1"
   
    if "Contigs" in os.environ:
        contigs = os.environ.get("Contigs")
    if "Region" in os.environ:
        region = os.environ.get("Region")

    if len(contigs) == 0:
        exit("This script needs an environment variable Contigs set to something")

    contigs_filename = os.path.basename(contigs)
    accession = contigs_filename.split('.')[0] # basic, will work with non-'.' containing files too

    print("contigs",contigs, "accession:",accession, "region: " + region, flush=True)

    try:
        process_file(contigs, accession, region)
    except Exception as ex:
        print("Exception occurred during process_file() with arguments", contigs_filename, region,flush=True) 
        print(ex,flush=True)
        import traceback
        traceback.print_exc()

    #cleanup
    # it is important that this code isn't in process_file() as that function may stop for any reason
    print("checking free space",flush=True)
    os.chdir("/serratus-data")
    os.system(' '.join(["ls","-Rl",accession+"*"])) 
    os.system(' '.join(["rm","-Rf",accession+"*"])) 
    os.system(' '.join(["df", "-h", "."]))

if __name__ == '__main__':
   main()

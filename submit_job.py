import json
import boto3
import sys

if len(sys.argv) < 2:
    exit("argument: [accession]")

accession = sys.argv[1]
if "RR" not in accession:
    exit("accession should be of the form: [E/S]RR[0-9]+")

batch = boto3.client('batch')
region = batch.meta.region_name
assembler = "minia"
already_on_s3 = True

response = batch.submit_job(jobName='MiniaBatchProcessingJobQueue', 
                            jobQueue='MiniaBatchProcessingJobQueue', 
                            jobDefinition='MiniaBatchJobDefinition', 
                            containerOverrides={
                                "command": [ "python", "batch_processor.py"],
                                "environment": [ 
                                    {"name": "Accession", "value": accession},
                                    {"name": "Region", "value": region},
                                    {"name": "Assembler", "value": assembler},
                                    {"name": "AlreadyOnS3", "value": str(already_on_s3)},
                                ]
                            })


print("Job ID is {}.".format(response['jobId']))

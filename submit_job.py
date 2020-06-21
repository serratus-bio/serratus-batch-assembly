import json
import boto3
import sys

if len(sys.argv) < 2:
    exit("argument: [accession]")

accession = sys.argv[1]
if "RR" not in accession:
    exit("accession should be of the form: [E/S]RR[0-9]+")

if len(sys.argv) > 2:
    assembler = sys.argv[2]
    if assembler not in ["minia","coronaspades"]:
        exit("assembler needs to be minia or coronaspades")
else:
    assembler = "minia"

batch = boto3.client('batch')
#region = batch.meta.region_name
region = "us-east-1"
already_on_s3 = True

jobDefinition = 'RayanSerratusAssemblyBatchJobDefinition'
if assembler == "coronaspades" or 'himem' in sys.argv:
    jobDefinition = 'RayanSerratusAssemblyHimemBatchJobDefinition'

response = batch.submit_job(jobName='RayanSerratusAssemblyBatchJobQueue', 
                            jobQueue='RayanSerratusAssemblyBatchJobQueue', 
                            jobDefinition=jobDefinition, 
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

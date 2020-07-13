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
    if assembler not in ["minia","coronaspades","none"]:
        exit("assembler needs to be 'minia' or 'coronaspades' or 'none'")
else:
    assembler = "coronaspades"

batch = boto3.client('batch')
#region = batch.meta.region_name
region = "us-east-1"

jobDefinition = 'RayanSerratusAssemblyBatchJobDefinition'
if assembler == "coronaspades" or 'himem' in sys.argv:
    jobDefinition = 'RayanSerratusAssemblyHimemBatchJobDefinition'

force_redownload = False
with_darth = False
with_serra = True

response = batch.submit_job(jobName='RayanSerratusAssemblyBatchJobQueue', 
                            jobQueue='RayanSerratusAssemblyBatchJobQueue', 
                            jobDefinition=jobDefinition, 
                            containerOverrides={
                                "command": [ "python", "batch_processor.py"],
                                "environment": [ 
                                    {"name": "Accession", "value": accession},
                                    {"name": "Region", "value": region},
                                    {"name": "Assembler", "value": assembler},
                                    {"name": "ForceRedownload", "value": str(force_redownload)},
                                    {"name": "Darth", "value": str(with_darth)},
                                    {"name": "Serra", "value": str(with_serra)},
                                ]
                            })


print("Job ID is {}.".format(response['jobId']))

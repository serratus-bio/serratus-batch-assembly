import json
import boto3
import sys

if len(sys.argv) < 2:
    exit("argument: [s3_filename]")

filename = sys.argv[1]

batch = boto3.client('batch')
region = "us-east-1"

jobDefinition = 'RayanSerratusAssemblyHimemBatchJobDefinition' # needed for Vadr

response = batch.submit_job(jobName='RayanSerratusAssemblyBatchJobQueue', 
                            jobQueue='RayanSerratusAssemblyBatchJobQueue', 
                            jobDefinition=jobDefinition, 
                            containerOverrides={
                                "command": [ "python", "annot_batch_processor.py"],
                                "environment": [ 
                                    {"name": "Contigs", "value": filename},
                                    {"name": "Region", "value": region},
                                ]
                            })


print("Job ID is {}.".format(response['jobId']))

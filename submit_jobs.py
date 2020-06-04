import json
import boto3

batch = boto3.client('batch')
region = batch.meta.region_name

response = batch.submit_job(jobName='SerratusAssemblyBatchProcessingJobQueue', 
                            jobQueue='SerratusAssemblyBatchProcessingJobQueue', 
                            jobDefinition='SerratusAssemblyBatchJobDefinition', 
                            containerOverrides={
                                "command": [ "python", "batch_processor.py"],
                                "environment": [ 
                                    {"name": "Accession", "value": accession},
                                    {"name": "Region", "value": region},
                                ]
                            })


print("Job ID is {}.".format(response['jobId']))

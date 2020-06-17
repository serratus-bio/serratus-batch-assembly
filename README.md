# Construction of viral contigs using [fastp/bbduk]+Minia+CheckV on AWS Batch

### Source

Taken from: ["Orchestrating an Application Process with AWS Batch using AWS CloudFormation"](https://aws.amazon.com/blogs/compute/orchestrating-an-application-process-with-aws-batch-using-aws-cloudformation/)

But I removed all the CodeCommit stuff (replaced by `deploy-docker.sh` manual deployment to ECR).

Amazon Elastic Container Registry (ECR) is used as the Docker container registry. An AWS Batch job is manually triggered by `submit_job.py`.

Provided CloudFormation template has all the services (VPC, Batch *managed*, IAM roles, EC2 env)

### Installation 

Execute the below commands to spin up the infrastructure cloudformation stack.

```
./spinup.sh
./deploy-docker.sh
```

If you ever recreate the stack (e.g. after `cleanup.sh`), you don't need to run `deploy-docker.sh` unless the Dockerfile or scripts in `src/` were modified.

### Running an assembly job

1. `./submit_job.py SRRxxxxxx`
2. In AWS Console > Batch, monitor how the job runs.

### Code Cleanup

In short:

```
./cleanup.sh
```

Which deletes the CloudFormation stack.

What it doesn't do (need sto be done manually):

AWS Console > ECR - serratus-batch-assembly-job - delete the image(s) that are pushed to the repository

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


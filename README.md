# Construction of contigs using fastp+Minia on AWS Batch

### Source

Taken from: ["Orchestrating an Application Process with AWS Batch using AWS CloudFormation"](https://aws.amazon.com/blogs/compute/orchestrating-an-application-process-with-aws-batch-using-aws-cloudformation/)

But I removed all the CodeCommit stuff (replaced by `deploy-docker.sh` manual deployment to ECR).

Amazon Elastic Container Registry (ECR) is used as the Docker container registry. AWS Batch will be triggered by the lambda when a dataset file is dropped into the S3 bucket. 

Provided CloudFormation template has all the services (VPC, Batch *managed*, IAM roles, EC2 env, S3, Lambda)

### Installation 

Execute the below commands to spin up the infrastructure cloudformation stack.

```
./spinup.sh
./deploy-docker.sh
```

If you ever recreate the stack (e.g. after `cleanup.sh`), you don't need to run `deploy-docker.sh` unless the Dockerfile or scripts in `src/` were modified.

### Running an assembly job

1. ./submit_job.py [textfile_with_list_of_accessions]
2. In AWS Console > Batch, Notice the Job runs and performs the operation based on the pushed container image.

### Code Cleanup

In short:

```
./cleanup.sh
```

Which does:

    ```
    $ aws cloudformation delete-stack --stack-name batch-processing-job

    ```

What it doesn't do:

AWS Console > ECR - batch-processing-job-repository - delete the image(s) that are pushed to the repository

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


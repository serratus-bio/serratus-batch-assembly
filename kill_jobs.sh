#! /bin/bash
myJOBQueue=RayanSerratusAssemblyBatchJobQueue

for i in $(aws batch list-jobs --job-queue $myJOBQueue --output text --query jobSummaryList[*].[jobId])
do
  echo "Deleting RUNNING Job: $i"
  aws batch terminate-job --job-id $i --reason "Terminating job."
  echo "Job $i deleted"
done

for i in $(aws batch list-jobs --job-queue $myJOBQueue --job-status runnable --output text --query jobSummaryList[*].[jobId])
do
  echo "Deleting RUNNABLE Job: $i"
  aws batch terminate-job --job-id $i --reason "Terminating job."
  echo "Job $i deleted"
done

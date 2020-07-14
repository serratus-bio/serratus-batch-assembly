myJOBQueue=RayanSerratusAssemblyBatchJobQueue
succeeded=$(aws batch list-jobs --job-queue $myJOBQueue --job-status succeeded --output text --query jobSummaryList[*].[jobId] | wc -l)
runnable=$(aws batch list-jobs --job-queue $myJOBQueue --job-status runnable --output text --query jobSummaryList[*].[jobId] | wc -l)
running=$(aws batch list-jobs --job-queue $myJOBQueue --job-status running --output text --query jobSummaryList[*].[jobId] | wc -l)
echo "$runnable RUNNABLE $running RUNNING $succeeded SUCCEEDED"

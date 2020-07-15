echo "job minutes"
myJOBQueue=RayanSerratusAssemblyBatchJobQueue
aws batch list-jobs --job-queue $myJOBQueue --job-status succeeded --output text --query jobSummaryList[*].[jobId,startedAt,stoppedAt] | tail -n 100| awk '{print $1,"duration",($3-$2)/1000/60}'
#; "date -d@"$2 |  getline mydate; print mydate}' 

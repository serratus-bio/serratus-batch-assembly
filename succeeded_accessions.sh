myJOBQueue=RayanSerratusAssemblyBatchJobQueue
jobstatus=succeeded
tolookfor="_"

jobstatus=failed
tolookfor="RR"

aws batch list-jobs --job-queue $myJOBQueue --job-status $jobstatus --output text --query jobSummaryList[*].[jobId] > lists/all_$jobstatus.jobs.txt

rm -f lists/all_$jobstatus.txt
# one line at a time
#for job in `cat 50k_succeeded.jobs.txt`

# 10 lines at a time
while mapfile -t -n 50 ary && ((${#ary[@]})); do
	input_jobs=$(printf '%s\n' "${ary[@]}")
	input_jobs=$(echo $input_jobs | sed 's/\n//g' )
	echo "$input_jobs"
	aws batch describe-jobs --jobs $input_jobs | jq '.jobs |.[] | .container.environment |.[] ' |grep "$tolookfor" |awk '{print $2}' | sed 's/"//g'	>> lists/all_$jobstatus.txt
done < lists/all_$jobstatus.jobs.txt

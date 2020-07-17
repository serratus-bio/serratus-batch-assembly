myJOBQueue=RayanSerratusAssemblyBatchJobQueue
aws batch list-jobs --job-queue $myJOBQueue --job-status succeeded --output text --query jobSummaryList[*].[jobId] | tail -n 1000 > 1000_succeeded.jobs.txt

rm -f 1000_succeeded.txt
# one line at a time
#for job in `cat 50k_succeeded.jobs.txt`

# 10 lines at a time
while mapfile -t -n 50 ary && ((${#ary[@]})); do
	input_jobs=$(printf '%s\n' "${ary[@]}")
	input_jobs=$(echo $input_jobs | sed 's/\n//g' )
	echo "$input_jobs"
	aws batch describe-jobs --jobs $input_jobs | jq '.jobs |.[] | .container.environment |.[] ' |grep "_" |awk '{print $2}' | sed 's/"//g'	>> 1000_succeeded.txt
done < 1000_succeeded.jobs.txt

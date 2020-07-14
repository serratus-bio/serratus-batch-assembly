myJOBQueue=RayanSerratusAssemblyBatchJobQueue
#aws batch list-jobs --job-queue $myJOBQueue --job-status succeeded --output text --query jobSummaryList[*].[jobId] > 50k_succeeded.jobs.txt

rm -rf 50k_succeeded.txt
# one line at a time
#for job in `cat 50k_succeeded.jobs.txt`

# 10 lines at a time
while mapfile -t -n 50 ary && ((${#ary[@]})); do
	input_jobs=$(printf '%s\n' "${ary[@]}")
	input_jobs=$(echo $input_jobs | sed 's/\n//g' )
	echo "$input_jobs"
	aws batch describe-jobs --jobs $input_jobs | jq '.jobs |.[] | .container.environment |.[] ' |grep RR |awk '{print $2}' | sed 's/"//g'	>> 50k_succeeded.txt
done < 50k_succeeded.jobs.txt

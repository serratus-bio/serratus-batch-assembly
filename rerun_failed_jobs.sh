#cd lists && paste <(awk '{gsub(/\./,"",$4); print $4}' rescaffold.jobids.txt) rescaffold.txt > rescaffold.job_accession.txt
# python rerun_failed_jobs.py > rerun_failed_jobs.txt


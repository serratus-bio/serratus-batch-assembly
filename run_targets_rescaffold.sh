#for f in `cat lists/rescaffold.txt`
for f in `cat rerun_failed_jobs.txt`
do
    #echo $f
    #if grep -q $f 50k_succeeded.txt then
    #	    echo "job $f already succeeded"
    #	    continue
    #    fi
    python submit_job.py $f coronaspades | \
	    tee -a lists/rescaffold.jobids.rerun.txt
done

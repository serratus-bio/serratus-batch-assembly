for f in `cat list_100`
do
    python submit_job.py $f
done

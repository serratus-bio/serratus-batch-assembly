for f in `cat list_100`
do
    echo $f
    python submit_job.py $f
done

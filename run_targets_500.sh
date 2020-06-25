for f in `cat ../serratus-batch-dl/first_500.txt`
do
    echo $f
    python submit_job.py $f
done

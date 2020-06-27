for f in `cat find_non_assembled.txt`
do
    #echo $f
    python submit_job.py $f coronaspades
done

for f in `cat lists/CoV_id95-60_reads100p_score30p.unique.txt`
do
    #echo $f
    python submit_job.py $f coronaspades
done

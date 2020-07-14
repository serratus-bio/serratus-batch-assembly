for f in `cat lists/union_p_sra_score20_CoV_score20_read10.sra_STAT_accessions.txt`
do
    #echo $f
    #if grep -q $f 50k_succeeded.txt then
    #	    echo "job $f already succeeded"
    #	    continue
    #    fi
    python submit_job.py $f coronaspades
done

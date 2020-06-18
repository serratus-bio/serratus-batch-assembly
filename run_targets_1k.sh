for f in `awk '{print $1}' assembly_targets_first_1k.tsv | tail -n +2`
do
    #echo $f
    python submit_job.py $f
done

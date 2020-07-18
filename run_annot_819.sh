#for f in `ls -1 ~/master_table/cov5/cov5.complete.uclust0.99.fa.split/`
#for f in `cat ~/master_table/cov5/cov5.complete.uclust0.99.fa.split/missing.txt`
#for f in `ls -1 ~/master_table/cov5_cg.id99/split/`
for f in `cat ~/master_table/cov5_cg.id99/rerun.txt`
#for f in `cat master_table/darth.tosubmit.txt`
do
    #python annot_submit_job.py cov5/complete_genomes/$f 
    #python annot_submit_job.py cov5/complete_genomes_id99/$f 
    #python annot_submit_job.py master_table_assemblies/$f.fa
    python annot_submit_job.py cov5/complete_genomes_id99/$f.cov5_cg.fa
done

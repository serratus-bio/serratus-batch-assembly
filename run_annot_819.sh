#for f in `ls -1 ~/master_table/cov5/cov5.complete.uclust0.99.fa.split/`
#for f in `cat ~/master_table/cov5/cov5.complete.uclust0.99.fa.split/missing.txt`
#for f in `ls -1 ~/master_table/cov5_cg.id99/split/`
#for f in `cat ~/master_table/cov5_cg.id99/rerun.txt`
#for f in `cat master_table/darth.tosubmit.txt`
#for f in `ls -1 ~/master_table/cov5_cg.id99/split_fragment/`
#for f in `cat ~/master_table/cov5_cg.id99/list_annotated.cg.todo.txt`
#for f in `ls -1 ~/master_table/nt_otus.id99/split/`
#for f in `cat ~/master_table/cov5_cg.id99/toro.txt`
#for f in `cat master_table/forgotten_bgc_rescaffold.txt`
#for f in `cat detect_non_updates.txt`
for f in `cat misfits.txt`
do
    #python annot_submit_job.py cov5/complete_genomes/$f 
    python annot_submit_job.py master_table_assemblies/$f.fa | \
	    	tee -a misfits.jobids.txt
	    	#tee -a lists/forgotten_bgc_rescaffold.nonupdates.jobids.txt
    #python annot_submit_job.py cov5/complete_genomes_id99/$f
    #python annot_submit_job.py cov5/fragments_id99/$f 
    #python annot_submit_job.py cov5/nt_otus.id99/$f
done

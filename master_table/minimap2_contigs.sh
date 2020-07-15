#!/bin/bash


for assembly_type in "*.bgc_cov.fa" "*.checkv_filtered.fa"
do
echo "$assembly_type"

align () {
echo "aligning to" $reftype $ref
find $HOME/master_table/data/ -name "$assembly_type" ! -size 0 | \
parallel -j15 "\
echo {} && minimap2 \
      -t 1 \
      -a \
      -N 1 \
      $ref \
      {} \
      > {}.$reftype.sam  2>/dev/null\
      && 
python serratus_assembly_minimap2_qc.py \
     {}.$reftype.sam \
     | awk '{ print \$7\" \" \$10}' \
     > {}.$reftype.master_table"
}

reftype=complete
ref=$HOME/master_table/cov5/cov5.complete.uclust0.99.mmi

align 

reftype=frag
ref=$HOME/master_table/cov5/cov5.frag.97p.uclust0.99.mmi

align

reftype=rs
ref=$HOME/master_table/cov5/cov5.rs.mmi

align

done

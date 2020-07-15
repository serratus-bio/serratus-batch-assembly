#!/bin/bash

align () {
echo "aligning to" $reftype $ref
find $HOME/master_table/data/ -name "*.checkv_filtered.fa" ! -size 0 | \
parallel -j15 "\
minimap2 \
      -t 1 \
      -a \
      -N 1 \
      $ref \
      {} \
      > {}.$reftype.sam"
}

reftype=complete
ref=$HOME/master_table/cov5/cov5.complete.uclust0.99.mmi

#align

reftype=frag
ref=$HOME/master_table/cov5/cov5.frag.97p.uclust0.99.mmi

align

reftype=rs
ref=$HOME/master_table/cov5/cov5.rs.mmi

align

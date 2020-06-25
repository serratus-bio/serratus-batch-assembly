assembler=$1
aws s3 ls s3://serratus-public/assemblies/contigs/ |grep $assembler | awk '{print $4}' | sed "s/\.$assembler\.checkv_filtered\.fa//g" |sort > find_non_assembled.assembled.txt
diff assembly_targets_first_1k.txt find_non_assembled.assembled.txt | grep "<" |awk '{print $2}' | tee find_non_assembled.txt

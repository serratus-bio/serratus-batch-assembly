aws s3 ls s3://serratus-public/seq/cov5/annotations/ | grep darth.input_md5 > list_annotated.txt
grep _cg list_annotated.txt  |awk '{gsub(/.darth.input_md5/,"",$4); print $4}' |sort > list_annotated.cg.txt
ls -1 split_cg/ |sort > list_annotated.cg.done.txt
comm -3 list_annotated.cg.done.txt list_annotated.cg.txt > list_annotated.cg.todo.txt

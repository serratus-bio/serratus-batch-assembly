aws s3 rm s3://serratus-rayan/genome_structure.data.tsv # FIXME remove it after first time
aws s3 cp genome_structure.data.tsv s3://serratus-rayan/genome_structure/ --acl public-read
aws s3 cp genome_structure.to_plot.txt s3://serratus-rayan/genome_structure/ --acl public-read
aws s3 cp genome_structure.data.marshal s3://serratus-rayan/genome_structure/ --acl public-read

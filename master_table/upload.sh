aws s3 sync ~/master_table/assemblies/ s3://serratus-rayan/master_table_assemblies/
aws s3 cp master_table.csv s3://serratus-rayan/sra_master_table.csv
aws s3api put-object-acl --bucket serratus-rayan --key sra_master_table.csv --acl public-read

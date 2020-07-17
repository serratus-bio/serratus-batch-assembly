aws s3 cp ~/master_table/assemblies/ s3://serratus-rayan/master_table_assemblies/ --recursive --acl public-read
aws s3 cp master_table.csv s3://serratus-rayan/sra_master_table.csv --acl public-read

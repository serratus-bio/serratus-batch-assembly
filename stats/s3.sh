file=$1
aws s3 cp $file s3://serratus-public/assemblies/analysis/
aws s3api put-object-acl --bucket serratus-public --key assemblies/analysis/$file --acl public-read

aws ec2 describe-instances --filters Name=instance-state-name,Values=running |grep CoreCount | awk '{print $2}'  | sed 's/,//g' | awk '{s+=$1} END {print 2*s}'

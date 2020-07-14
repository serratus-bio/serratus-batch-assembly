# just a sample query
#aws batch list-jobs --job-queue $myJOBQueue --job-status succeeded --output text  | awk '{ if ($2 > 1592497234561  ) { print } }'|wc -l

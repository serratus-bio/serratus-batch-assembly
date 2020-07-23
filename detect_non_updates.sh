aws s3 ls s3://serratus-public/assemblies/annotations/ > annotations.txt
python detect_non_updates.py| awk '{print $1}' > detect_non_updates.txt

#further detection of what wasn't recently annotated but should have been
# grep -f lists/rescaffold.txt annotations.txt | grep -v "07-22"  |grep -v "07-23" | grep -v serraplace | grep darth.tar.gz

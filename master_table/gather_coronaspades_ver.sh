TARGET_VER="07-15-mi"
for f in `find ~/master_table/data/ -name "*.coronaspades.txt"`
do
	#echo $f
	head $f |grep -v "SPAdes version" | grep $TARGET_VER | awk '{print $5}' | sed 's/.fastq//g' | sed 's/\/serratus-data\///g' | sed 's/\n//g'
done

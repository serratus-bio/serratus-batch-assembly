s3folder="s3://serratus-public/assemblies/annotations/"
aws s3 ls $s3folder > darth.folder.txt
cat darth.folder.txt |grep darth.tar.gz | awk '{gsub(/.darth.tar.gz/,"",$4) ; print $4}'  |sort > darth.list.txt
cat darth.folder.txt |grep darth.stripped.tar.gz | awk '{gsub(/.darth.stripped.tar.gz/,"",$4) ;print $4}'  |sort > darth.stripped.list.txt
comm -3 darth.list.txt darth.stripped.list.txt > darth.todo.list.txt

job () {
	f=$1.darth.tar.gz
	s3folder=$2
	echo "job: $f $s3folder"
	accession="${f%%.*}"
	#if test -n $(aws s3 ls "$s3folder"$accession.darth.stripped.tar.gz)

	aws s3 cp "$s3folder"$f .
	tar xf $f
  	rm -Rf $accession.darth/read-analysis
	outfile=$accession.fa.darth.stripped.tar.gz
	tar -czvf $outfile $accession.darth
	aws s3 cp $outfile $s3folder
	rm -Rf $accession* # cleanup
}
export -f job

cat darth.todo.list.txt | parallel -j15 "job {} $s3folder"

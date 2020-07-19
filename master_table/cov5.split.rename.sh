cd split
for f in `ls *.fa`
do
	#cov5_cg.id99.id_NC_039207.1.fa"
	nf=$(echo $f | python -c "import sys; s = sys.stdin.read().strip(); print('%s.%s.fa' % ('.'.join(s.split('.')[2:4]).replace('id_',''),'.'.join(s.split('.')[:2])))")
	mv $f $nf
done

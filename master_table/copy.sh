cd data
#aws s3 sync s3://serratus-public/assemblies/other/   . --exclude "*" --include "*.darth.tar.gz" #no! too big!
aws s3 sync s3://serratus-public/assemblies/other/   . --exclude "*" --include "*.bgc_statistics.txt"
aws s3 sync s3://serratus-public/assemblies/other/   . --exclude "*" --include "*.coronaspades.txt"
aws s3 sync s3://serratus-public/assemblies/other/   . --exclude "*" --include "*.gene_clusters.fa"
aws s3 sync s3://serratus-public/assemblies/other/   . --exclude "*" --include "*.serratax.final"
aws s3 sync s3://serratus-public/assemblies/other/   . --exclude "*" --include "*.serraplace.tar.gz"
aws s3 sync s3://serratus-public/assemblies/contigs/ . --exclude "*" --include "*.gene_clusters.checkv_filtered.fa"

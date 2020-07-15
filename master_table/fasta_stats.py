import sys,os
sys.path.append("../stats/")
import assembly_categories
from pyfasta import Fasta

print("accession\tlength\tnb_contigs\tcategory")
g = open("list_gc_cv_catABCD.txt","w")
for accession in open("list_latest_ver.txt").readlines():
    accession = accession.strip()
    assembly = "/home/ec2-user/master_table/data/" + accession + ".coronaspades.gene_clusters.checkv_filtered.fa"
    if (not os.path.exists(assembly)) or\
            os.stat(assembly).st_size == 0:
        nb_contigs = 0
        total_length = 0
    else:
        f = Fasta(assembly)
        nb_contigs = len(f.keys())
        total_length = sum([len(f[key]) for key in f.keys()])
        
    category = assembly_categories.get_category(total_length, nb_contigs)
    print(accession,total_length,nb_contigs,category, sep='\t')

    if category in "ABCD":
        g.write(accession+"\n")

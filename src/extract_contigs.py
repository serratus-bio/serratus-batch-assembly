# syntax:
# bash checkv_detect.sh | python extract_contigs.py [contigs_filename] [viral_contigs_filename]
import sys
import glob, os
from pyfaidx import Fasta
f = Fasta(sys.argv[1])
g = open(sys.argv[2],"w")
for line in sys.stdin:
    ctg = line.split()[0]
    ctglen = line.split()[1]
    print(sys.argv[1],"found corona contig ID:",ctg)
    if ctglen != len(f[ctg]):
        print("len mismatch?!",ctglen,len(f[ctg]))
    seq = f[ctg]
    g.write(">"+seq.long_name+"\n"+str(seq)+"\n")
g.close()


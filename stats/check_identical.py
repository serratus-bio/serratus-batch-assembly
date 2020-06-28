def rev_compl(st):
    nn = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N':'N'}
    return "".join(nn[n] for n in reversed(st))

from pyfasta import Fasta  

contigs = []

for filename in open("catA-v3.txt").read().strip().split('\n'):
    filename = filename.replace('s3://serratus-public/assemblies/contigs/','')
    g = Fasta("/home/rayan/serratus-assemblies/" + filename)
    contig = str([g[key] for key in g.keys()][0])
    #print(len(contig))
    if contig > rev_compl(contig):
        contig = rev_compl(contig)
    contigs += [contig]

import collections
repetitions = 0
for item, count in collections.Counter(contigs).items():
    if count > 1:
        print("contig",len(item),"repeated",count)
        repetitions += count-1
print(repetitions,"duplicates")


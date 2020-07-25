import csv
from collections import defaultdict

# get single-contig accessions

single_contig = set()
with open("master_table.csv") as csvfile:
#with open("master_table.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        nb_contigs = int(row['nb_contigs'])
        if nb_contigs == 1: 
            #print(row['accession'])
            single_contig.add(row['accession'])


## Load OTUs/accession correspondance

def strip(x):
    return x.replace('/G','').replace('/A','')

otu99, otu97 = set(), set()
dotu97 = defaultdict(list)
for line in open("../lists/label_otu.id99_97.tsv"):
    if len(line) == 0: continue
    label, ex99, ex97 = line.strip().split()
    label, ex99, ex97 = strip(label), strip(ex99), strip(ex97)
    otu99.add(ex99)
    otu97.add(ex97)
    #print(label,ex99,ex97)
    dotus97[ex97] += [label]

print(len(otu97),"OTUs 97%")
print(len(otu99),"OTUs 99%")

# Load genome structures

contains_rdrp = set()
eval("genome_structure.data.py")


# Get list of RdRP-containing, single-contig accessions for each OTU

for ex97 in otu97:
    for accession in dotus97[ex97]:
        if accession in single_contig:
            # TBC
            pass


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
    dotu97[ex97] += [label]

print(len(otu97),"OTUs 97%")
print(len(otu99),"OTUs 99%")

# Load genome structures

contains_rdrp = set()
gsdata = open("genome_structure.data.py").read()
genome_structures = eval("("+gsdata+")")
print(len(genome_structures),"structures")
dgs     = dict()
dgs_ids = dict()
for structure in genome_structures:
    accession, lst = structure
    dgs[accession]     = lst
    dgs_ids[accession] = set()
    for start,end,id,ctg,is_complete in lst:
        dgs_ids[accession].add(id)


# Get list of RdRP-containing, single-contig accessions for each OTU

nb_single_contig_found = 0
nb_single_contig_and_rdrp_found = 0
for ex97 in sorted(list(otu97)):
    found_single_contig = None
    for accession in dotu97[ex97]:
        #print(ex97,accession)
        if accession in single_contig:
            nb_single_contig_found += 1
            if accession in dgs_ids and 'RdRP_1' in dgs_ids[accession]:
                nb_single_contig_and_rdrp_found += 1
                found_single_contig = accession
                break
    if found_single_contig is None:
        print("OTU",ex97,"(%d accessions)" % len(dotu97[ex97]), "couldn't find a single single-contig RdRP-containing accession")
    else:
        print("OTU",ex97,"(%d accessions)" % len(dotu97[ex97]), "using",found_single_contig)

print(nb_single_contig_found,"/",len(otu97),"single-contig found in OTUs")
print(nb_single_contig_and_rdrp_found,"/",len(otu97),"single-contig AND complete RdRP found in OTUs")

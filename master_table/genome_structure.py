import csv, os
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

import marshal
marshal_filename = "genome_structure.data.marshal"
if not os.path.exists(marshal_filename) or os.stat(marshal_filename).st_size == 0:
    print("creating marshal file from","genome_structure.data.py","data")
    gsdata = open("genome_structure.data.py").read()
    genome_structures = eval("("+gsdata+")")
    outmarshal = open(marshal_filename,"wb")
    marshal.dump(sorted(genome_structures),outmarshal)
    outmarshal.close()
    # also write it to CSV for good measure
    tsv_outfile = open("genome_structure.data.tsv","w")
    tsv_writer = csv.writer(tsv_outfile, delimiter='\t')
    tsv_writer.writerow(['accession','start_position','end_position','gene_name','contig_name','is_complete'])
    for structure in genome_structures:
        list_features = structure[1]
        if len(list_features) == 0: continue
        for feature in list_features:
            tsv_writer.writerow([structure[0]] + list(feature))
    tsv_outfile.close()

else:
    # load marshal file (faster)
    print("opening marshal file",marshal_filename)
    gsdata = open(marshal_filename,'rb')
    genome_structures = marshal.load(gsdata)
    gsdata.close()
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

to_plot = set()

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
        to_plot.add((found_single_contig,ex97))

print(nb_single_contig_found,"/",len(otu97),"single-contig found in OTUs")
print(nb_single_contig_and_rdrp_found,"/",len(otu97),"single-contig AND complete RdRP found in OTUs")

# add Toro and Epsy to plot
torolike = "SRR4920045 SRR5234495 SRR6291266"
epsys = """ERR3994223
SRR1324965
SRR5997671
SRR10917299
SRR8389791
SRR2418554
SRR7507741
SRR6788790
SRR6311475"""
for collection_name, collection_lst in [('toro',torolike.split()),('Epsy',epsys.split('\n'))]:
    for elt in collection_lst:
        elt = elt.strip()
        if elt in single_contig:
            to_plot.add((elt,collection_name))
        else:
            print("can't add",elt,"from",collection_name,"as it's not single-contig")
        if elt in otu97:
            for accession in dotu97[elt]:
                if accession in single_contig:
                    to_plot.add((accession,collection_name))
                    print("added",accession,"for",collection_name)
                else:
                    print("can't add",collection_name,accession,"as it's not single-contig")

g = open("genome_structure.to_plot.txt","w")
for accession, why in to_plot:
    g.write("%s %s\n" % (accession, why))
g.close()

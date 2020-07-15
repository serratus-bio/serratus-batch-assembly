import sys,os
sys.path.append("../stats/")
import assembly_categories
from pyfasta import Fasta
import pandas as pd
from tqdm import tqdm

columns = ["accession","length","nb_contigs","category","serratax_id","serraplace_id",\
           "refseq_neighbour","refseq_pctid","genome_neighbour","genome_pctid",\
           "fragment_neighbour","fragment_pctid"]

true_reftype = {"refseq":"rs","genome":"complete","fragment":"frag"} # some correspondence between master table columns and my filenames

g = open("list_catABCD.txt","w") # accessorily save catABCD's

dd = dict() # dict of dict

for accession in tqdm(open("list_latest_ver.txt").readlines()):
    accession = accession.strip()
    assembly = "/home/ec2-user/master_table/data/" + accession + ".coronaspades.gene_clusters.checkv_filtered.fa"

    if (not os.path.exists(assembly)) or\
            os.stat(assembly).st_size == 0:
        assembly = "/home/ec2-user/master_table/data/" + accession + ".coronaspades/" + accession + ".coronaspades.bgc_cov.fa"
        if (not os.path.exists(assembly)) or\
            os.stat(assembly).st_size == 0:
            nb_contigs = 0
            total_length = 0
            continue # skip that accession

    f = Fasta(assembly)
    nb_contigs = len(f.keys())
    total_length = sum([len(f[key]) for key in f.keys()])

    category = assembly_categories.get_category(total_length, nb_contigs)
    #print(accession,total_length,nb_contigs,category, sep='\t')
    dd[accession] = {"accession": accession,
                 "length":total_length,
                 "nb_contigs":nb_contigs,
                 "category":category}

    if category in "ABCD":
        g.write(accession+"\n")

    # gather .sam stats
    for reftype in ["refseq","genome","fragment"]:
        filename = assembly + "." + true_reftype[reftype] +".master_table"
        neighbor = ""
        pctid = "*"
        if os.path.exists(filename):
            ls = open(filename).readlines()[0].split() # FIXME: reading 1 line only for now
            if len(ls) == 2: # no ref genome
                neighbor, pctid = ls
            else:
                print(filename,"has bad format:",ls)
        else:
            print(filename,"doesnt exist")
        dd[accession][reftype + '_neighbour'] = neighbor
        dd[accession][reftype + '_pctid'] = pctid

    # get serratax info
    serratax_filename = "/home/ec2-user/master_table/data/" + accession + ".coronaspades/" + accession + ".coronaspades.gene_clusters.checkv_filtered.fa.serratax.final"
    if os.path.exists(serratax_filename):
        serratax_info = open(serratax_filename).read().strip().split()
        if len(serratax_info) > 0:
            serratax_id = serratax_info[0]
        else:
            serratax_id = "_empty_"
        dd[accession]['serratax_id'] = serratax_id


    os.system("cp " + assembly + " /home/ec2-user/master_table/assemblies/" + accession + ".fa")
    #break

data = pd.DataFrame.from_dict(dd, columns=columns, orient='index')
#print(data.to_string(index=False))
g = open("master_table.csv","w")
g.write(data.to_csv(index=False, sep=','))

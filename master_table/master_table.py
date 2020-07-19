import sys,os
sys.path.append("../stats/")
import assembly_categories
from pyfasta import Fasta
import pandas as pd
from tqdm import tqdm

columns = ["accession","length","nb_contigs","category","serratax_id","serraplace_id",\
           "refseq_neighbour","refseq_pctid","genome_neighbour","genome_pctid",\
           "fragment_neighbour","fragment_pctid","platform"]

true_reftype = {"refseq":"rs","genome":"complete","fragment":"frag"} # some correspondence between master table columns and my filenames

seqtech = dict(map(lambda x:x.split(),open("seq_tech.txt").readlines())) # grab list of seq technologies

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
    nb_contigs_above_10kbp = len([key for key in f.keys() if len(f[key]) >= 10000])
    nb_contigs_above_20kbp = len([key for key in f.keys() if len(f[key]) >= 20000])
    total_length = sum([len(f[key]) for key in f.keys()])

    category = assembly_categories.get_category(total_length, nb_contigs)
    #print(accession,total_length,nb_contigs,category, sep='\t')
    dd[accession] = {"accession": accession,
                 "length":total_length,
                 "nb_contigs":nb_contigs,
                 "category":category}

    if category in "ABCD":
        g.write(accession+"\n")

    #if total_length > 50000:
    #   print("tot length",total_length)
    #   print("nb contigs above 10 kbp",nb_contigs_above_10kbp)
    #   print("nb contigs above 20 kbp",nb_contigs_above_20kbp)

    # gather .sam stats
    for reftype in ["refseq","genome","fragment"]:
        filename = assembly + "." + true_reftype[reftype] +".nt_otus.id99.master_table"
        neighbor = ""
        pctid = "*"
        if os.path.exists(filename):
            nei_aln = []
            for line in open(filename).readlines():
                ls = line.split()
                if len(ls) == 3: # no ref genome
                    length, neighbor, pctid = ls
                    length = int(length)
                    nei_aln += [(length,neighbor,pctid)]
                else:
                    print(filename,"has bad format:",ls)
            length, neighbor, pctid = sorted(nei_aln)[::-1][0]
        else:
            print(filename,"doesnt exist")
        dd[accession][reftype + '_neighbour'] = neighbor
        dd[accession][reftype + '_pctid'] = pctid

    # get serratax info
    serratax_filename = "/home/ec2-user/master_table/data/" + accession + ".coronaspades/" + accession + ".coronaspades.gene_clusters.checkv_filtered.fa.serratax.final"
    if not os.path.exists(serratax_filename):
        #get the BGC serratax
        serratax_filename = "/home/ec2-user/master_table/data_bgc/" + accession + ".fa.serratax.final"

    if os.path.exists(serratax_filename):
        serratax_info = open(serratax_filename).read().strip().split()
        if len(serratax_info) > 0:
            serratax_id = serratax_info[0]
        else:
            serratax_id = "_empty_"
        dd[accession]['serratax_id'] = serratax_id

    if accession in seqtech and seqtech[accession] != 'notfound':
        dd[accession]['platform'] = seqtech[accession]
    else:
        dd[accession]['platform'] = '?'

    os.system("cp " + assembly + " /home/ec2-user/master_table/assemblies/" + accession + ".fa")
    #break


# perform surgery on the master table
# dd = dict([x for x in dd.items() if x[1]['seqtech'] != 'NANOPORE') #UNTESTED CODE

data = pd.DataFrame.from_dict(dd, columns=columns, orient='index')
#print(data.to_string(index=False))
g = open("master_table.csv","w")
g.write(data.to_csv(index=False, sep=','))

import csv
with open("master_table.prior_to_rescaffolding.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        nb_contigs = int(row['nb_contigs'])
        length = int(row['length'])
        if nb_contigs == 1: continue
        refseq_pctid = float(row['refseq_pctid'])
        genome_pctid = float(row['genome_pctid'])
        if genome_pctid >= 97: continue 
        fragment_pctid = row['fragment_pctid']
        print(row['accession'])
        #print(nb_contigs,length, refseq_pctid,genome_pctid,fragment_pctid)

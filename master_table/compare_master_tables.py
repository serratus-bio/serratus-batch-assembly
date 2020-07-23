import csv

rescaffold = set(map(lambda x:x.strip(),open("../lists/rescaffold.txt").readlines()))

def mst(filename):
    d = dict()
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            accession = row['accession']
            nb_contigs = int(row['nb_contigs'])
            length = int(row['length'])
            if 'filtering_method' in row: filtering_method = row['filtering_method']
            d[accession]=(nb_contigs,length)
    return d

new=    mst("master_table.csv")
old=    mst("master_table.prior_to_rescaffolding.csv")

nb_differences = 0
nb_new = 0
for accession in new:
    if accession not in old: 
        nb_new += 1
        continue
    if new[accession] != old[accession]:
        nc, nl = new[accession]
        oc, ol = old[accession]
        not_rescaffolded = "| *" if accession not in rescaffold else "|"
        print(accession, "|", oc, "|", nc, "|", ol, "|", nl, not_rescaffolded)
        nb_differences += 1
print(nb_differences,"differences")
print(nb_new ,"new")

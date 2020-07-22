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

for accession in new:
    if accession not in old: continue
    if new[accession] != old[accession]:
        print(accession)
        print(new[accession])
        print(old[accession])
        if accession not in rescaffold:
            print("!! not rescaffolded",accession)
        print("--")

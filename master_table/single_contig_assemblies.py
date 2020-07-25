import csv
with open("master_table.csv") as csvfile:
#with open("master_table.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        nb_contigs = int(row['nb_contigs'])
        if nb_contigs == 1: 
            print(row['accession'])

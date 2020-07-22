import csv

rescaffold = set(map(lambda x:x.strip(),open("../lists/rescaffold.txt").readlines()))

with open("master_table.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        accession = row['accession']
        if accession not in rescaffold: continue
        filtering_method = row['filtering_method']
        if filtering_method != "bgc": continue
        print(accession)

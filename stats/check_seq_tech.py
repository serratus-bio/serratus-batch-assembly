import csv
import glob

tech = dict()
for filename in glob.glob('sra/*.txt'):
    reader = csv.DictReader(open(filename))
    for row in reader:
        accession = row['Run']
        platform = row['Platform']
        tech[accession] = platform

for accession in open("catA-v3.accessions.txt").read().strip().split('\n'):
    if accession not in tech:
        print(accession,"not found")
        continue
    print(accession,tech[accession])

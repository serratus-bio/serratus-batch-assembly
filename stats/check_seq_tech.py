import csv
import glob
import gzip

tech = dict()
for filename in glob.glob('sra/*csv*'):
    opener = gzip.open(filename,'rt') if filename.endswith("gz") else open(filename)
    try:
        reader = csv.DictReader(opener)
        for row in reader:
            try:
                accession = row['Run']
            except:
                print("no Run in ",filename,"?")
            platform = row['Platform']
            tech[accession] = platform
    except:
        print("malformed csv",filename)

for accession in open("../master_table/master_table.accessions.txt").read().strip().split('\n'):
    if accession not in tech:
        print(accession,"notfound")
        continue
    print(accession,tech[accession])

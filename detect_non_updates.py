from subprocess import check_output
from dateutil import parser
from datetime import datetime, timedelta

accessions = set()
for accession in open("master_table/forgotten_bgc_rescaffold.txt"):
    accession = accession.strip()
    accessions.add(accession)

last_hour_date_time = datetime.now() - timedelta(hours = 4)

for line in open("annotations.txt"):
    
    if "darth.tar.gz" not in line: continue
    ls = line.split()
    fn = ls[3]
    accession = fn.split('.')[0]
    if accession not in accessions: continue
    #print(accession,line)
    dt = parser.parse(ls[0] + " " + ls[1])
    if dt < last_hour_date_time:
        print(accession,dt)

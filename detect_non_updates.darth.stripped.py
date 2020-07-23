from subprocess import check_output
from dateutil import parser
from datetime import datetime, timedelta

print("run beforehand: aws s3 ls s3://serratus-public/assemblies/annotations/ > annotations.txt")


darth = dict()
darth_stripped = dict()

for line in open("annotations.txt"):
    if "darth" not in line: continue
    ls = line.split()
    fn = ls[3]
    accession = fn.split('.')[0]
    #print(accession,line)
    dt = parser.parse(ls[0] + " " + ls[1])
    if "darth.tar.gz" in line:
        darth[accession] = dt
    elif "darth.stripped" in line:
        darth_stripped[accession] = dt

for accession in darth:
    if accession not in darth_stripped:
        print(accession,"has darth but not stripped")
        continue
    dt = darth[accession]
    dts = darth_stripped[accession]
    if dts < dt:
        print("%s.fa" % accession,"has expired stripped")

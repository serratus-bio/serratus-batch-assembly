import os
for line in open("darth.txt"):
    accession = os.path.basename(line).split('.')[0]
    print(accession)

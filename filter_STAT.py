oneK = list(open("assembly_targets_first_1k.txt").read().strip().split())
core20_noSC = list(open("core20_noSC.txt").read().strip().split())

#print("oneK        length",len(oneK),":",oneK[:5],"...")
#print("core20_noSC length",len(core20_noSC),":",core20_noSC[:5],"...")

oneK = set(oneK)
core20_noSC = set(core20_noSC)

for line in open('STAT_accessions.txt'):
    line = line.strip()
    if line in oneK or line in core20_noSC: continue
    print(line)

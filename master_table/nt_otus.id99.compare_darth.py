import glob, os

genomes = set()
for genome in open('nt_otus.id99.list.txt').readlines():
    genome = genome.strip()
    genomes.add(genome)


to_rerun = open("nt_otus.id99.rerun.txt","w")

rdrp_new = set()
rdrp_old = set()

for genome in genomes:
    new_annotations_filename = "annotations.new-darth/%s.darth.alignments.fasta" % genome
    if not os.path.exists(new_annotations_filename):
        #print(genome,"doesn't exist")
        to_rerun.write(genome+"\n")
        continue

    if "RdRP" in open(new_annotations_filename).read():
        rdrp_new.add(genome)
    else:
        #print("no RdRP in",genome,os.stat(annotations_filename).st_size)
        pass
 
for genome in genomes:
    old_annotations_filename = "annotations.old-darth/%s.darth.pfam.alignments.fasta" % genome
 
    if not os.path.exists(old_annotations_filename):
        #print(genome,"doesn't exist")
        continue

   
    if "RdRP" in open(old_annotations_filename).read():
        rdrp_old.add(genome)

print(len(rdrp_new - rdrp_old),'/',len(rdrp_new),"RdRP in new annotations that aren't in old annotations")
print(len(rdrp_old - rdrp_new),'/',len(rdrp_old),"RdRP in old annotations that aren't in new annotations")


robert_list = "NC_001846.1 NC_034440.1 NC_034972.1 JN856008.2 MF593268.1 FJ755618.2 FJ647221.1 KP849472.1 MF618253.1 MH687968.1 MH687970.1 DQ811786.2 AF208066.1 KY406735.1 MF618252.1 DQ811787.1 KR270796.1"
robert_list = robert_list.split()

for robert_genome in robert_list:
    robert_genome = robert_genome + ".nt_otus.id99.fa"
    if robert_genome not in rdrp_new - rdrp_old:
        print(robert_genome,"still not in new annotations")

print(' '.join([x.replace('.nt_otus.id99.fa','') for x in rdrp_new - rdrp_old]))

to_rerun.close()





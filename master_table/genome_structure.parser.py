from Bio import SearchIO
for qresult in SearchIO.parse('genome_structure/SRR9967737.transeq.domtbl','hmmsearch3-domtab'):
     for item in qresult.hits:
          print(item)
	  print(dir(item))

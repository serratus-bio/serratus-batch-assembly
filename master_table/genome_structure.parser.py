from Bio import SearchIO
import sys, os

filename='genome_structure/SRR9967737.transeq.domtbl' # incomplete rdrp
filename="genome_structure/SRR11939968.transeq.domtbl" # complete genome

if len(sys.argv) > 1:
    filename = sys.argv[1]

def inv_transeq_coords(ctg_name, ctg_len, start, end):
    frame = int(ctg_name[-1])
    if frame <= 3:
        return (start*3, end*3) # rough approximation
    else:
        return (ctg_len*3-end*3, ctg_len*3-start*3) # rough approximation too

res = []
for qresult in SearchIO.parse(filename,'hmmsearch3-domtab'):
    for hit in qresult.hits:
        hmm_len = qresult.seq_len
        hmm_id = qresult.id
        contig_len = hit.seq_len
        #print("newhit",hit.query_id,qresult.seq_len,qresult.id)
        hit_len = 0
        for item in hit.hsps:
            hit_name      = item.query_id
            contig_name   = item.hit_id
            transeq_start = item.hit_start
            transeq_end   = item.hit_end
            contig_start, contig_end = inv_transeq_coords(contig_name, contig_len, transeq_start, transeq_end)
            #print(hit_name,contig_name,contig_start, contig_end)
            #print(item.query_span,item.hit_span)
            hit_len += item.hit_span # FIXME: unsure that will properly take care of incomplete genes. Verify that result agrees with Robert's suggestion: " You have to check for an incomplete RdRP alignment, you can't see that without counting gaps in the PFAM a2m. I use 25% gaps as the cutoff.""
        complete = hit_len >= 0.75 * hmm_len
        #print("incomplete",hmm_id,":",hit_len,"/",hmm_len)
        res += [(contig_start, contig_end, hit_name, contig_name, complete)]

accession = os.path.basename(filename).split('.')[0]
print("(\"%s\", (\\" % accession)
for e in sorted(res):
    print(str(e)+",")
print(")),")

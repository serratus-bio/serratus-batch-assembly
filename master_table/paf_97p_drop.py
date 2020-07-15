
exclude = set()
for line in open("cov5.frag.fa.paf"):
    de = 1
    ls = line.split()
    for field in ls:
        if field.startswith("de"):
            de = float(field.split(':')[-1])
            #if de > 0.03:
            #    print(de)
    ql = int(ls[1]) # query length
    qml = int(ls[10]) # query mapped length, incl gaps
    if qml > ql*0.9 and de < 0.03:
       exclude.add(ls[0])

from pyfasta import Fasta
f = Fasta("cov5.frag.fa")
g = open("cov5.frag.97p.fa","w")
for elt in f:
    name = elt.split()[0]
    if name in exclude: continue
    g.write(">%s\n%s\n" % (elt,f[elt]))


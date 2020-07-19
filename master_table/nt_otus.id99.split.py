rs = open("nt_otus.id99.rs.fa","w")
gb = open("nt_otus.id99.gb.fa","w")
frag = open("nt_otus.id99.frag.fa","w")

dest = None
for line in open('nt_otus.id99.fa'):
    if line.startswith('>'):
        if 'complete genome' in line:
            if line.startswith(">NC_"):
                dest=rs
            else:
                dest=gb
        else:
            dest=frag
    #print(line)
    dest.write(line)



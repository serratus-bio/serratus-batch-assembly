rs = open("cov5.rs.fa","w")
gb = open("cov5.gb.fa","w")
frag = open("cov5.frag.fa","w")

dest = None
for line in open('cov5.fa'):
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



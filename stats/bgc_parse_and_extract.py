import os, sys
from pyfasta import Fasta
def process(bgc, exclude=set()):
        if os.stat(bgc).st_size == 0:
            return None, None, None
        f = open(bgc)
        bgc_data = f.read().split('\n')
        nb_cov_bgc = 0
        contigs = []
        current_bgc_subgraph = None
        current_bgc_candidate = None
        current_bgc_domains = None
        reading_domains = False
        is_cov = False
        for line in bgc_data:
            # right determination of nb of domains
            if line.startswith("Domain cordinates:"):
                current_bgc_domains = 0
                continue
            if len(line.strip().split()) == 2:
                a,b = line.split()
                if a.isdigit() and b.isdigit():
                    #print(a,b)
                    current_bgc_domains += 1
                    reading_domains = True
                    continue
            # not the right one (see above)
            #if line.startswith("# domains in the component"):
            #    current_bgc_domains = int(line.split()[-1])
            #    continue
            if reading_domains and is_cov: # if we're done reading domains, add the contig
                #print(line,"-",current_bgc_domains)
                contigs += [(current_bgc_subgraph,current_bgc_candidate,current_bgc_domains)]
                reading_domains = False
                is_cov = False
            if line.startswith("BGC subgraph"):
                current_bgc_subgraph = int(line.split()[-1])
                reading_domains = False
                continue
            if line.startswith("BGC candidate"):
                current_bgc_candidate  = int(line.split()[-1])
                reading_domains = False
                continue
            if line.startswith("#"): continue
            if not "CoV_" in line: continue
            if " " in line: continue
            nb_cov_bgc += 1 #int(line.split()[-1])w
            is_cov = True
        
        bgc_contigs_filename = None
        accession = None
        if nb_cov_bgc >= 2:
            accession = os.path.basename(bgc).replace('.coronaspades.bgc_statistics.txt','')
            if accession in exclude: return None,None,None
            #print(nb_cov_bgc, accession)
            #print(contigs)
            
            # extract interesting contigs
            contigs_filename = bgc.replace('.coronaspades.bgc_statistics.txt','.coronaspades.gene_clusters.fa')
            bgc_contigs_filename = contigs_filename.replace('.coronaspades.gene_clusters.fa','.coronaspades.bgc_cov.fa')
            if os.stat(contigs_filename).st_size == 0: 
                print("empty contigs file but bgc found cov?!",bgc)
                return None, None, None
            f = Fasta(contigs_filename)
            g = open(bgc_contigs_filename,"w")
            for s,c,d in contigs:
                nodepattern = "cluster_%d_candidate_%d_domains_%d" % (s,c,d)
                found = False
                for key in f:
                    if nodepattern in key:
                        found = True
                        g.write(">%s\n%s\n" % (key,f[key]))
                if not found:
                    print(nodepattern,"contig not found in",contigs_filename)
        return accession, nb_cov_bgc, bgc_contigs_filename


if __name__ == "__main__":
    print("processed",process(sys.argv[1]))

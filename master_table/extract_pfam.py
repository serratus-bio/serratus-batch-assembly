import os
import boto3
s3 = boto3.client('s3')

for accession in open("master_table.accessions.txt"):
    outfile = "s3://serratus-public/assemblies/annotations/" + accession + ".fa.darth.alignments.fasta"

    # see if transeq.alignments.fasta already exist
    # otherwise, take pfam.alignments.fasta (previous version of darth)
    # otherwise, extract alignments.fasta from darth output
    
    transeq_fn = "assemblies/annotations/" + accession + ".fa.darth.transeq.alignments.fasta"
    pfam_fn = "assemblies/annotations/" + accession + ".fa.darth.pfam.alignments.fasta"

    transeq_fn2 = "assemblies/other/" + accession + ".coronaspades/" + accession + ".coronaspades.gene_clusters.checkv_filtered.fa.darth.transeq.alignments.fasta"
    pfam_fn2 = "assemblies/other/" + accession + ".coronaspades/" + accession + ".coronaspades.gene_clusters.checkv_filtered.fa.darth.pfam.alignments.fasta"
    if s3_file_exists(s3,"serratus-public",transeq_fn):
        print(accession,"has transeq file")
        os.system("aws s3 cp s3://serratus-public/" + transeq_fn + "  " + outfile)
    elif s3_file_exists(s3,"serratus-public",transeq_fn2):
        print(accession,"has transeq file in other/")
        os.system("aws s3 cp s3://serratus-public/" + transeq_fn2 + "  " + outfile)
    elif s3_file_exists(s3,"serratus-public", pfam_fn):
        print(accession,"has pfamfile")
        os.system("aws s3 cp s3://serratus-public/" + pfam_fn + "  " + outfile)
    elif s3_file_exists(s3,"serratus-public", pfam_fn2):
        print(accession,"has pfamfile in other/")
        os.system("aws s3 cp s3://serratus-public/" + pfam_fn2 + "  " + outfile)
    else:
        # extract alignments.fasta from darth.tar.gz if it iexists
	os.system("aws s3 cp s3://serratus-public/assemblies/annotations/" +  accession +".darth.stripped.tar.gz .")
        os.system("tar xf " +accession +".darth.stripped.tar.gz")
        if os.path.exist(accession+".darth/transeq/alignments.fasta"):
            os.system("aws s3 cp "+accession+".darth/transeq/alignments.fasta " + outfile)
            print("copied transeq from stripped")
        elif os.path.exist(accession+".darth/pfam/alignments.fasta"):
            os.system("aws s3 cp "+accession+".darth/pfam/alignments.fasta " + outfile)
            print("copied pfam from stripped")
	os.system("rm -Rf " +accession+"*")

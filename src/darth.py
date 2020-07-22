import os

def darth(accession, contigs_filename, s3, s3_folder, outputBucket, has_reads = False):
    os.system("mkdir -p /serratus-data/" +accession +".darth")
    os.chdir("/serratus-data/" + accession + ".darth")
    reads = ('/serratus-data/' +accession+".fastq") if has_reads else "none"
    os.system(' '.join(["darth.sh",accession,'/serratus-data/' + contigs_filename, reads, '/darth', "/serratus-data/" + accession + ".darth",str(8)]))
    try:
        s3.upload_file("pfam/alignments.fasta", outputBucket, s3_folder + contigs_filename + ".darth.pfam.alignments.fasta", ExtraArgs={'ACL': 'public-read'})
    except:
        print("cannot upload", accession + ".darth/pfam/alignments.fasta",flush=True)
    try:
        s3.upload_file("transeq/alignments.fasta", outputBucket, s3_folder + contigs_filename + ".darth.transeq.alignments.fasta", ExtraArgs={'ACL': 'public-read'})
    except:
        print("cannot upload", accession + ".darth/transeq/alignments.fasta",flush=True)
    os.chdir("/serratus-data/")
    os.system("tar -zcvf "+ accession + ".darth.tar.gz " + accession + ".darth")
    s3.upload_file(accession + ".darth.tar.gz", outputBucket, s3_folder + contigs_filename + ".darth.tar.gz", ExtraArgs={'ACL': 'public-read'})
    # to verify which file darth was run on 
    os.system("md5sum " + contigs_filename+ " > " + accession + ".darth.input_md5")
    s3.upload_file(accession + ".darth.input_md5", outputBucket, s3_folder + contigs_filename + ".darth.input_md5", ExtraArgs={'ACL': 'public-read'})


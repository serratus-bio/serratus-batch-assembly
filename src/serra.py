import os

def serra(accession, serratax_contigs_input, s3, s3_folder, outputBucket):
        
        os.chdir("/serratus-data/")

        # Serratax
        os.system(' '.join(["serratax",serratax_contigs_input,accession + ".serratax"]))
        try:
            s3.upload_file(accession + ".serratax/tax.final", outputBucket, s3_folder + serratax_contigs_input + ".serratax.final", ExtraArgs={'ACL': 'public-read'})
        except:
            print("couldn't upload tax.final",flush=True)
        os.system("tar -zcvf "+ accession + ".serratax.tar.gz " + accession + ".serratax")
        s3.upload_file(accession + ".serratax.tar.gz", outputBucket, s3_folder + serratax_contigs_input + ".serratax.tar.gz", ExtraArgs={'ACL': 'public-read'})

        # Serraplace
        os.system("mkdir -p /serratus-data/" +accession +".serraplace")
        os.chdir("/serratus-data/" + accession + ".serraplace")
        os.system(' '.join(["/place.sh","-g","-d",'/serratus-data/' + serratax_contigs_input]))
        os.system("ls -l")
        os.chdir("/serratus-data/")
        os.system("tar -zcvf "+ accession + ".serraplace.tar.gz " + accession + ".serraplace")
        s3.upload_file(accession + ".serraplace.tar.gz", outputBucket, s3_folder + serratax_contigs_input + ".serraplace.tar.gz", ExtraArgs={'ACL': 'public-read'})



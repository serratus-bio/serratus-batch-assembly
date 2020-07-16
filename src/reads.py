import os
import utils
from utils import sdb_log
from datetime import datetime
import glob

# from serratus-batch-dl
def fastp(accession, folder, sdb, nb_threads, extra_args=""):
    # Separate fastq files into paired- and single-end reads
    #based on https://github.com/hawkjo/sequencetools/blob/master/clean_fastqs_in_subdirs.py
    fastq_files = glob.glob(folder+"/"+accession+"*.fastq")
    pe_fastq_files = []
    se_fastq_files = []
    for fname in fastq_files:
        if fname[-8:] == '_1.fastq':
            # If first of pair is found, add both
            fname2 = fname[:-8] + '_2.fastq'
            if fname2 not in fastq_files:
                print('Unpaired _1 file: ' + fname,flush=True)
                sdb_log(sdb,accession,'read_unpaired1','True')
                se_fastq_files.append(fname)
            else:
                pe_fastq_files.append((fname, fname2))
        elif fname[-8:] == '_2.fastq':
            # If second of pair is found, test for presence of first, but do nothing
            fname1 = fname[:-8] + '_1.fastq'
            if fname1 not in fastq_files:
                print('Unpaired _2 file: ' + fname,flush=True)
                sdb_log(sdb,accession,'read_unpaired2','True')
                se_fastq_files.append(fname)
        else:
            se_fastq_files.append(fname)

    os.system('rm -f ' + accession + '.fastq') # should be unnecessary
    for f1, f2 in pe_fastq_files:
        os.system(' '.join(["/fastp", "--thread", nb_threads, "--trim_poly_x", "-i", f1, "-I", f2, "--stdout", extra_args, ">>", accession + ".fastq"]))
    for f in se_fastq_files:
        os.system(' '.join(["/fastp", "--thread", nb_threads, "--trim_poly_x", "-i", f,            "--stdout", extra_args, ">>", accession + ".fastq"]))


def get_reads(accession, s3, force_redownload, sdb, nb_threads, inputDataFn):
    readsBucket = "serratus-rayan"

    already_on_s3 = utils.s3_file_exists(s3, readsBucket, "reads/"+accession+".fastq")
    
    os.chdir("/serratus-data")
    local_file = accession + ".fastq"

    if (not already_on_s3) or force_redownload:
        print("downloading reads from SRA to EBS..",flush=True)
        startTime = datetime.now()
        
        os.system('mkdir -p out/')
        
        prefetch_start = datetime.now()
        os.system('prefetch --max-size 35G '+accession)
        prefetch_time = datetime.now() - prefetch_start 
        sdb_log(sdb,accession,'prefetch_time',int(prefetch_time.seconds))

        os.system('mkdir -p tmp/')
        pfqdump_start = datetime.now()
        os.system('/parallel-fastq-dump --skip-technical --split-e --outdir out/ --tmpdir tmp/ --threads ' + nb_threads + ' --sra-id '+accession)
        pfqdump_time = datetime.now() - pfqdump_start
        sdb_log(sdb,accession,'pfqdump_time',int(pfqdump_time.seconds))

        files = os.listdir(os.getcwd() + "/out/")
        print("after fastq-dump, dir listing of out/", files,flush=True)
        g = open(inputDataFn,"w")
        for f in files:
            print("file: " + f + " size: " + str(os.stat("out/"+f).st_size), flush=True)
            g.write(f + " " + str(os.stat("out/"+f).st_size)+"\n")
        g.close()

        # potential todo: there is opportunity to use mkfifo and speed-up parallel-fastq-dump -> bbduk step
        # as per https://github.com/ababaian/serratus/blob/master/containers/serratus-dl/run_dl-sra.sh#L26

        # run fastp
        fastp_start = datetime.now()
        fastp(accession,"out/", sdb, nb_threads)

        if os.stat(accession+".fastq").st_size == 0:
            # fastp output is empty, most likely those reads have dummy quality values. retry.
            print("retrying fastp without quality filtering", flush=True)
            sdb_log(sdb,accession,'fastp_noqual','True')
            fastp(accession,"out/",sdb, nb_threads, "--disable_quality_filtering")
 
        if os.stat(accession+".fastq").st_size == 0:
            # fastp output is STILL empty. could be that read1 or read2 are too short. consider both unpaired
            print("retrying fastp unpaired mode", flush=True)
            os.system('mv out/' + accession + '_1.fastq out/' + accession + '_a.fastq')
            os.system('mv out/' + accession + '_2.fastq out/' + accession + '_b.fastq')
            sdb_log(sdb,accession,'fastp_unpaired','True')
            fastp(accession,"out/",sdb, nb_threads, "--disable_quality_filtering")
           
        if os.stat(accession+".fastq").st_size == 0:
            print("fastp produced empty output even without quality filtering", flush=True)
            sdb_log(sdb,accession,'fastp_empty','True')
            exit(1)

        print("fastp done, now uploading to S3",flush=True)
        fastp_time = datetime.now() - fastp_start 
        sdb_log(sdb,accession,'fastp_time',int(fastp_time.seconds))

        # upload filtered reads to s3
        upload_to_s3 = False
        if upload_to_s3:
            upload_start = datetime.now()
            s3.upload_file(accession+".fastq", readsBucket, "reads/"+accession+".fastq")
            upload_time = datetime.now() - upload_start
            sdb_log(sdb,accession,'upload_time',int(upload_time.seconds))
 
        # cleanup. #(important when using a local drive)
        os.system(' '.join(["rm","-f","out/"+accession+"*.fastq"]))
        os.system(' '.join(["rm","-f","public/sra/"+accession+".sra"]))
        os.system('rm -Rf ' + accession) # seems to be the right path

        endTime = datetime.now()
        diffTime = endTime - startTime
        sdb_log(sdb,accession,'batch_assembly_dl_time',int(diffTime.seconds))
        sdb_log(sdb,accession,'batch_assembly_dl_date',str(datetime.now()))
        print(accession, "Serratus-batch-dl processing time - " + str(diffTime.seconds),flush=True) 

    else:
        s3.download_file(readsBucket, "reads/" + accession + ".fastq", local_file)
        print("downloaded saved reads from", "s3://" + readsBucket + "/reads/" + accession + ".fastq", "to",local_file, flush=True)

        g = open(inputDataFn,"w")
        g.write(accession + ".fastq is " + str(os.stat(local_file).st_size)+" bytes \n")
        g.close()
        
        # compute number of lines and add it to the log file
        os.system(' '.join(["wc", "-l", local_file,"| cut -d' ' -f1 >",accession+".number_lines.txt"]))
        os.system(' '.join(["echo", "-n", "nbreads: ", "|", "cat", "-", accession + ".number_lines.txt", ">>", inputDataFn]))
        
        # log number of reads
        with open(accession+".number_lines.txt") as f:
            nb_reads = str(int(f.read())/4)
            file_size = str(os.stat(local_file).st_size)
            sdb_log(sdb,accession,'nb_reads',nb_reads)
            sdb_log(sdb,accession,'file_size',file_size)



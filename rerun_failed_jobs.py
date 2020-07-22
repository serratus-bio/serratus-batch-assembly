failed_jobs = set()
for line in open("lists/all_failed.jobs.txt"):
    job = line.strip()
    failed_jobs.add(job)

jd = dict()
#input_file="lists/rescaffold.job_accession.txt"
input_file="lists/rescaffold.jobids.rerun.job_accession.txt"
for line in open(input_file):
    job, accession = line.strip().split()
    jd[job] = accession

for job in failed_jobs:
    if job in jd:
        print(jd[job])

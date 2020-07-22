# gets the status of a list of jobid's
import subprocess, sys

if len(sys.argv) < 2:
    exit("args: [list of job ID's, e.g. the output of submit_job.py (e.g. rescaffold.jobids.txt) ]")

jobs = set()
for line in open(sys.argv[1]):
    if len(line.strip()) == 0: continue
    job  = line.split()[-1].strip('.')
    jobs.add(job)


myJOBQueue="RayanSerratusAssemblyBatchJobQueue"
succeeded=set(subprocess.check_output(f"aws batch list-jobs --job-queue {myJOBQueue} --job-status succeeded --output text --query jobSummaryList[*].[jobId]",shell=True).decode().strip().split('\n'))
failed=   set(subprocess.check_output(f"aws batch list-jobs --job-queue {myJOBQueue} --job-status failed    --output text --query jobSummaryList[*].[jobId]",shell=True).decode().strip().split('\n'))
runnable= set(subprocess.check_output(f"aws batch list-jobs --job-queue {myJOBQueue} --job-status runnable  --output text --query jobSummaryList[*].[jobId]",shell=True).decode().strip().split('\n'))
running=  set(subprocess.check_output(f"aws batch list-jobs --job-queue {myJOBQueue} --job-status running   --output text --query jobSummaryList[*].[jobId]",shell=True).decode().strip().split('\n'))

#print(runnable)
print("from the list:",len(runnable & jobs),"runnable",len(running & jobs),"running",len(succeeded & jobs),"succeeded",len(failed & jobs),"failed")
print("total:",len(runnable),"runnable",len(running),"running",len(succeeded),"succeeded",len(failed),"failed")

accessions = []
for line in open('catA-v3.accessions.txt'):
    accessions += [line.strip()]

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

batches = 500

for chunk in chunks(accessions,batches):
    print(','.join(chunk))
    print()

# small
#export Accession=SRR10975663
# bit bigger
#export Accession=SRR10041282
# on S3, part of the 1k assembly test
export Accession=SRR9156994
export Region=us-east-1
export AlreadyOnS3=True
export Assembler=coronaspades
python batch_processor.py 

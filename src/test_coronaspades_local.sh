# small
#export Accession=SRR10975663
# bit bigger
#export Accession=SRR10041282
# on S3, part of the 1k assembly test. a small sample that contains a virus!
export Accession=SRR11859141 
export Region=us-east-1
export AlreadyOnS3=True
export Assembler=coronaspades
python batch_processor.py 

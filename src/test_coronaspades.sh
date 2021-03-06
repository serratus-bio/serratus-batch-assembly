#!/bin/bash

set -e

NAME=serratus-batch-assembly-job
#NOCACHE=--no-cache
docker build $NOCACHE -t $NAME \
             --build-arg AWS_ACCESS_KEY_ID=$(./get-aws-profile.sh --key) \
             --build-arg AWS_SECRET_ACCESS_KEY=$(./get-aws-profile.sh --secret) \
             --build-arg AWS_DEFAULT_REGION=us-east-1 \
              .
docker run \
    -e AWS_ACCESS_KEY_ID=$(./get-aws-profile.sh --key)\
    -e AWS_SECRET_ACCESS_KEY=$(./get-aws-profile.sh --secret)\
    -e AWS_DEFAULT_REGION=us-east-1\
    -e Accession=SRR11859141\
    -e Assembler=coronaspades \
    -e ForceRedownload=False\
    -e Darth=True\
    -e Serra=True\
    $NAME \
    python batch_processor.py 

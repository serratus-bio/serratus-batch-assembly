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
    -e Contigs="master_table_assemblies/ERR1301446.fa"\
    $NAME \
    python annot_batch_processor.py 

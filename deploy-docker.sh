#!/bin/bash

cd src
ACCOUNT=$(aws sts get-caller-identity --query Account --output text) # AWS ACCOUNT ID
DOCKER_CONTAINER=serratus-batch-assembly-job
REPO=${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/${DOCKER_CONTAINER}
TAG=build-$(date -u "+%Y-%m-%d")
echo "Building Docker Image..."
docker build -t $DOCKER_CONTAINER \
             --build-arg AWS_ACCESS_KEY_ID=$(./get-aws-profile.sh --key) \
             --build-arg AWS_SECRET_ACCESS_KEY=$(./get-aws-profile.sh --secret) \
             --build-arg AWS_DEFAULT_REGION=us-east-1 \
              .
echo "Authenticating against AWS ECR..."
eval $(aws ecr get-login --no-include-email --region us-east-1)
# create repository (only needed the first time)
aws ecr create-repository --repository-name $DOCKER_CONTAINER
echo "Tagging ${REPO}..."
docker tag $DOCKER_CONTAINER:latest $REPO:$TAG
docker tag $DOCKER_CONTAINER:latest $REPO:latest
echo "Deploying to AWS ECR"
docker push $REPO

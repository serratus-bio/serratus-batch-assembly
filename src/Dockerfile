FROM python
# https://pythonspeed.com/articles/alpine-docker-python/

WORKDIR /

COPY batch_processor.py .

RUN pip install --upgrade pip && \
    pip install boto3 awscli 

# local AWS credentials
ARG AWS_DEFAULT_REGION
#ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

ARG AWS_ACCESS_KEY_ID
#ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID

ARG AWS_SECRET_ACCESS_KEY
#ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

# fastp install
RUN curl -L -o fastp http://opengene.org/fastp/fastp 
RUN chmod +x fastp 

# TODO: bbduk install

# Minia install from binaries
RUN curl -L -o minia-v3.2.3-bin-Linux.tar.gz https://github.com/GATB/minia/releases/download/v3.2.3/minia-v3.2.3-bin-Linux.tar.gz 
RUN tar xf minia-v3.2.3-bin-Linux.tar.gz && rm minia-v3.2.3-bin-Linux.tar.gz
RUN mv minia-v3.2.3-bin-Linux/bin/minia ./ 

# MFcompress
RUN aws s3 cp s3://aws-unitigs-tools/MFCompress-linux64-1.01.tgz .
RUN tar xf MFCompress-linux64-1.01.tgz && rm MFCompress-linux64-1.01.tgz
RUN mv MFCompress-linux64-1.01/MFCompressC ./

# fastq-dump setup
# https://github.com/ababaian/serratus/blob/5d288765b6e22bf7ba1b69148e0013d65560b968/containers/serratus-dl/Dockerfile#L51
RUN curl -L -o /root/.ncbi/user-settings.mkfg https://raw.githubusercontent.com/ababaian/serratus/master/containers/serratus-dl/VDB_user-settings.mkfg
# https://github.com/ababaian/serratus/blob/5d288765b6e22bf7ba1b69148e0013d65560b968/containers/serratus-dl/serratus-dl.sh#L167
RUN DLID="$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 8 | head -n 1 )-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1 )-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1 )-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1 )-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 12 | head -n 1 )"
RUN sed -i "s/52e8a8fe-0cac-4bf2-983a-3617cdba7df5/$DLID/g" /root/.ncbi/user-settings.mkfg

RUN pwd
RUN df -h .
RUN ls


#FROM python
# https://pythonspeed.com/articles/alpine-docker-python/
FROM continuumio/miniconda3:4.8.2
# for conda

WORKDIR /

COPY batch_processor.py .

RUN pip install --upgrade pip && \
    pip install boto3 awscli 

RUN conda install -c conda-forge -c bioconda checkv bbmap

# local AWS credentials
ARG AWS_DEFAULT_REGION
#ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

ARG AWS_ACCESS_KEY_ID
#ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID

ARG AWS_SECRET_ACCESS_KEY
#ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

#SRA toolkit (from serratus-dl)
ENV SRATOOLKITVERSION='2.10.4'
RUN wget --quiet https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/${SRATOOLKITVERSION}/sratoolkit.${SRATOOLKITVERSION}-centos_linux64.tar.gz &&\
    tar xzf sratoolkit.${SRATOOLKITVERSION}-centos_linux64.tar.gz &&\
    rm -f sratoolkit.${SRATOOLKITVERSION}-centos_linux64.tar.gz &&\
    mkdir -p /opt/sratools &&\
    # Keep sratools grouped together, so its easy to copy them all out into the runtime
    bash -c "mv sratoolkit.${SRATOOLKITVERSION}-centos_linux64/bin/{vdb-config*,prefetch*,fastq-dump*,fasterq-dump*,sra*} /opt/sratools" &&\
    # Install into /usr/local/bin for the rest of the build
    cp -r /opt/sratools/* /usr/local/bin &&\
    mkdir /etc/ncbi
# https://github.com/ababaian/serratus/blob/5d288765b6e22bf7ba1b69148e0013d65560b968/containers/serratus-dl/Dockerfile#L51
RUN mkdir -p /root/.ncbi
RUN wget -O /root/.ncbi/user-settings.mkfg https://raw.githubusercontent.com/ababaian/serratus/master/containers/serratus-dl/VDB_user-settings.mkfg
RUN sed -i "s/\/root\/ncbi/\/mnt\/serratus-data/g" /root/.ncbi/user-settings.mkfg
RUN vdb-config --report-cloud-identity yes
# https://github.com/ababaian/serratus/blob/5d288765b6e22bf7ba1b69148e0013d65560b968/containers/serratus-dl/serratus-dl.sh#L167
RUN DLID="$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 8 | head -n 1 )-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1 )-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1 )-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1 )-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 12 | head -n 1 )" && sed -i "s/52e8a8fe-0cac-4bf2-983a-3617cdba7df5/$DLID/g" /root/.ncbi/user-settings.mkfg


# parallel-fastq-dump install
RUN wget --quiet https://raw.githubusercontent.com/rvalieris/parallel-fastq-dump/master/parallel-fastq-dump
RUN chmod +x parallel-fastq-dump

# fastp install
RUN wget --quiet http://opengene.org/fastp/fastp 
RUN chmod +x fastp 

# Minia install from binaries
RUN wget --quiet https://github.com/GATB/minia/releases/download/v3.2.4/minia-v3.2.4-bin-Linux.tar.gz 
RUN tar xf minia-v3.2.4-bin-Linux.tar.gz && rm minia-v3.2.4-bin-Linux.tar.gz
RUN mv minia-v3.2.4-bin-Linux/bin/minia ./ 

# MFcompress
RUN aws s3 cp s3://serratus-rayan/tools/MFCompress-linux64-1.01.tgz .
RUN tar xf MFCompress-linux64-1.01.tgz && rm MFCompress-linux64-1.01.tgz
RUN mv MFCompress-linux64-1.01/MFCompressC ./

# checkV database (huge, 1.7GB leading to 6GB uncompressed) 
RUN aws s3 cp s3://serratus-rayan/tools/checkv-db-v0.6.tar.gz .
RUN tar xf checkv-db-v0.6.tar.gz && rm checkv-db-v0.6.tar.gz
RUN export CHECKVDB=/checkv-db-v0.6

# for local testing ; will be mounted on AWS Batch
RUN mkdir -p /mnt/serratus-data 

RUN pwd
RUN df -T
RUN ls


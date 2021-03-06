#FROM python
# https://pythonspeed.com/articles/alpine-docker-python/
FROM continuumio/miniconda3:4.8.2
# for conda

WORKDIR /

# for coronaSPAdes
RUN apt-get update
RUN apt-get install -y  libbz2-dev cmake g++ zlib1g-dev

RUN pip install --upgrade pip && \
    pip install boto3 awscli pyfaidx

# openssl=1.0 is for samtools
RUN conda install -c conda-forge -c bioconda checkv bbmap samtools openssl=1.0

# local AWS credentials
ARG AWS_DEFAULT_REGION
#ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

ARG AWS_ACCESS_KEY_ID
#ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID

ARG AWS_SECRET_ACCESS_KEY
#ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

#SRA toolkit (from serratus-dl)
ENV SRATOOLKITVERSION='2.10.7'
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
RUN wget --quiet -O /root/.ncbi/user-settings.mkfg https://raw.githubusercontent.com/ababaian/serratus/master/containers/serratus-dl/VDB_user-settings.mkfg
RUN sed -i "s/\/root\/ncbi/\/serratus-data/g" /root/.ncbi/user-settings.mkfg
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

# coronaSPAdes
ENV CORONASPADESVERSION=SPAdes-3.15.0-corona-2020-07-15-mi
RUN wget --quiet http://cab.spbu.ru/files/coronaSPAdes/$CORONASPADESVERSION.tar.gz
RUN tar xf $CORONASPADESVERSION.tar.gz && rm $CORONASPADESVERSION.tar.gz
RUN cd $CORONASPADESVERSION && sed -i 's/Boost REQUIRED/Boost 1.63 EXACT REQUIRED/g' src/cmake/deps.cmake && ./spades_compile.sh

# MFcompress
RUN aws s3 cp s3://serratus-rayan/tools/MFCompress-linux64-1.01.tgz .
RUN tar xf MFCompress-linux64-1.01.tgz && rm MFCompress-linux64-1.01.tgz
RUN mv MFCompress-linux64-1.01/MFCompressC ./

# for local testing ; will be mounted on AWS Batch
RUN mkdir -p /serratus-data 

# checkV database (huge, 1.7GB leading to 6GB uncompressed) 
# FIXME if this is uncommented in production, please comment it to save image space
# this isn't critical as it is overwritten by a mount in the EC2 instance anyway
#RUN aws s3 cp s3://serratus-rayan/tools/checkv-db-v0.6.tar.gz .
#RUN tar xf checkv-db-v0.6.tar.gz && rm checkv-db-v0.6.tar.gz
#RUN mv checkv-db-v0.6 /serratus-data/
#RUN ls /serratus-data/
#RUN touch /serratus-data/test
#RUN ls /serratus-data/
# now done in UserData script

################### Serratax 

RUN apt-get -y install emboss
ENV SERRATAX_REFDIR /serratax_ref
ENV SERRATAX_LIBDIR /usr/local/bin
RUN wget --quiet https://serratus-public.s3.amazonaws.com/rce/serratax/tarball/serratax.tar.gz
RUN tar -zxvf serratax.tar.gz
RUN mv serratax_lib/* /usr/local/bin

################### Serraplace
# copied as is 
# except change -j4 to -j10

RUN 	apt-get update &&\
	apt-get -y install git cmake build-essential zlib1g-dev gzip unzip flex bison &&\
	wget --quiet http://eddylab.org/software/hmmer/hmmer-3.3.tar.gz&& tar xzvf hmmer-3.3.tar.gz && cd hmmer-3.3/ &&\
	./configure && make -j10 && make install && cd easel && make install && cd ../../ &&\
	git clone --recursive https://github.com/Pbdas/epa-ng.git &&\
	cd epa-ng && git checkout tags/v0.3.7 && git submodule update --init --recursive && make -j10 && cp bin/epa-ng /usr/local/bin && cd - &&\
	git clone https://github.com/lh3/seqtk.git && cd seqtk && make && cp seqtk /usr/local/bin && cd - &&\
	git clone --recursive https://github.com/lczech/gappa.git &&\
	cd gappa && git checkout f05e9fe && git submodule update --init --recursive && make -j10 && cp bin/gappa /usr/local/bin && cd - &&\
	cd gappa/libs/genesis/apps && git clone https://github.com/Pbdas/genesis-apps.git && make -j10 -C .. && cp ../bin/apps/genesis-apps/msa-merge ../bin/libgenesis.so /usr/local/bin && cd - &&\
	mkdir -p /serraplace && cd /serraplace && wget --quiet https://serratus-public.s3.amazonaws.com/pb/serraplace/reference/refpack.tar.gz && tar xzvf refpack.tar.gz && cd -

RUN wget --quiet https://raw.githubusercontent.com/ababaian/serratus/placement-dev/containers/serraplace/place.sh
# FIXME: remove that once Pierre has updated repo
RUN sed -i 's/serratus-data//g' /place.sh
RUN chmod +x /place.sh


#################### VADR
# copied as is
# except change path to /vadr

RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y cpanminus \
    build-essential \
    libnet-ssleay-perl \
    libcrypt-ssleay-perl \
    git \
    curl \
    zip \
    autoconf

### Perl dependencies:

RUN cpanm install Inline
RUN cpanm install Inline::C
RUN cpanm install LWP::Simple
RUN cpanm install LWP::Protocol::https

### Install VADR:
RUN git clone https://github.com/nawrockie/vadr.git
RUN cd vadr && ./vadr-install.sh linux

### Set up VADR environment variables:
ENV VADRINSTALLDIR="/vadr"
ENV VADRSCRIPTSDIR="$VADRINSTALLDIR/vadr"
ENV VADRMODELDIR="$VADRINSTALLDIR/vadr-models"
ENV VADRINFERNALDIR="$VADRINSTALLDIR/infernal/binaries"
ENV VADREASELDIR="$VADRINSTALLDIR/infernal/binaries"
ENV VADRHMMERDIR="$VADRINSTALLDIR/hmmer/binaries"
ENV VADRBIOEASELDIR="$VADRINSTALLDIR/Bio-Easel"
ENV VADRSEQUIPDIR="$VADRINSTALLDIR/sequip"
ENV VADRBLASTDIR="$VADRINSTALLDIR/ncbi-blast/bin"
ENV PERL5LIB="$VADRSCRIPTSDIR:$VADRSEQUIPDIR:$VADRBIOEASELDIR/blib/lib:$VADRBIOEASELDIR/blib/arch:$PERL5LIB"
ENV PATH="$VADRSCRIPTSDIR:$PATH"


################### Darth
# copypasted as-is from https://bitbucket.org/tomeraltman/darth/src/master/Dockerfile
# except: 
# * add 'darth'/ in the COPY statements
# * replace "/root/vadr/" to "/vadr/"
# * replace "/root/*" to "/darth" 

### Install apt dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y wget emboss samtools parallel bcftools tabix make infernal bowtie2 hmmer gawk

### Install third-party software:
RUN mkdir /darth

## Install FragGeneScan:
RUN cd /darth \
       && wget --quiet https://downloads.sourceforge.net/project/fraggenescan/FragGeneScan1.31.tar.gz \
       && tar xzf FragGeneScan1.31.tar.gz \
       && cd FragGeneScan1.31 \
       && make clean \
       && make fgs

## CM models for VADR:
RUN cd /darth \
       && wget --quiet https://ftp.ncbi.nlm.nih.gov/pub/nawrocki/vadr-models/coronaviridae/CURRENT/vadr-models-corona-1.1-1.tar.gz \
       && tar xzf vadr-models-corona-1.1-1.tar.gz

## CM models for CoV 5' and 3' UTRs:
RUN cd /darth \
       && wget --quiet ftp://ftp.ebi.ac.uk/pub/databases/Rfam/14.2/covid-19/coronavirus.clanin \
       && wget --quiet ftp://ftp.ebi.ac.uk/pub/databases/Rfam/14.2/covid-19/coronavirus.cm \
       && cmpress coronavirus.cm

## Pfam models specifically for CoV:
RUN cd /darth \
    && wget ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam_SARS-CoV-2_2.0/Pfam-A.SARS-CoV-2.hmm \
    && hmmpress Pfam-A.SARS-CoV-2.hmm

### Set up environment to ease running code from running container:

## Staging scripts:
COPY darth/src/darth.sh /usr/local/bin/
COPY darth/src/tbl2gff.awk /usr/local/bin/
COPY darth/src/canonicalize_contigs.sh /usr/local/bin/
COPY darth/src/sars-cov-2-pfam-order.txt /darth/

## Set script permissions:
RUN chmod 755 /usr/local/bin/darth.sh
RUN chmod 755 /usr/local/bin/canonicalize_contigs.sh

## Forgot to include in vadr image path to Bio-Easel scripts/miniapps, doing so now:
ENV PATH $PATH:/darth/FragGeneScan1.31:/vadr/Bio-Easel/src/easel/miniapp

#################### Final batch stuff

# things that might get modified a lot

COPY checkv_corona_entries.txt /
COPY *.py /

RUN pwd
RUN df -T
RUN ls



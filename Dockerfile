FROM ubuntu:18.04
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev unzip wget curl vim git libwebkitgtk-1.0.0 \
  && cd /usr/local/bin \ 
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
#Timezone
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN pip3 install paho-mqtt pysftp
WORKDIR /subscriber
COPY fab_get_model.py fab_get_model.py

ENV LC_ALL=C.UTF-8
CMD python3 fab_get_model.py

#docker build $PWD -t ipc-subscriber
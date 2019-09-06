FROM alpine:3.7 

ADD script.py /

ARG influxDBServer="influxdb.sagesdeath.com"

RUN apk add --no-cache python3 && \ 
apk add --no-cache lm_sensors nmap &&\
python3 -m ensurepip && \ 
rm -r /usr/lib/python*/ensurepip && \
pip3 install --upgrade pip setuptools && \
pip3 install influxdb &&\ 
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \ 
rm -r /root/.cache



CMD python3 script.py --influxDB=${influxDBServer}

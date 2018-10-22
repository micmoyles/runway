FROM python:2.7-wheezy
RUN mkdir -p /data/REMIT/transmit
RUN mkdir -p /data/REMIT/archive
RUN mkdir -p /usr/local/packages/python
COPY src/stomp/* /usr/local/packages/python/stomp/
COPY src/* /usr/src/app/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python","/usr/src/app/remitSubscriber.py"]

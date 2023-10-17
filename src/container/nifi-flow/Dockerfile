# This container has the purpose to auto deploy a existing nifi flow at startup

# The default nifi image from apache
FROM apache/nifi:1.12.0

# The nifi flow to deploy has to be in the same directory like the Dockerfile
COPY flow.xml.gz /opt/nifi/nifi-current/conf/flow.xml.gz 

# Set required permissions
USER root
# folder permissions for mount
RUN chmod 777 /opt/nifi/nifi-current/conf/
# permissions for nifi user id 1000
RUN chown 1000:1000 /opt/nifi/nifi-current/conf/
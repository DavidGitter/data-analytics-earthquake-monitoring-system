# This container has the purpose to auto deploy a existing nifi flow at startup

# The default nifi image from apache
FROM strimzi/kafka:0.20.1-rc1-kafka-2.6.0

#change to root user privileges
USER root:root

RUN yum install -y unzip
RUN mkdir -p /opt/kafka/plugins/s3-sink
COPY confluentinc-kafka-connect-s3-10.5.1.zip /opt/kafka/plugins/s3-sink
RUN unzip /opt/kafka/plugins/s3-sink/confluentinc-kafka-connect-s3-10.5.1.zip -d /opt/kafka/plugins/s3-sink
RUN rm /opt/kafka/plugins/s3-sink/confluentinc-kafka-connect-s3-10.5.1.zip

USER 1001
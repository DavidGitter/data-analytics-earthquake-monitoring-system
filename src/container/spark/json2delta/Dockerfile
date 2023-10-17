FROM gcr.io/datamechanics/spark:3.2-latest

USER root

ENV SPARK_HOME=/opt/spark
ENV PYSPARK_MAJOR_PYTHON_VERSION=3

WORKDIR /opt/spark

COPY --chmod=777 ./app.py /opt/spark/app.py

RUN pip install delta-spark==2.4.0
RUN pip install boto3
# RUN $SPARK_HOME/bin/spark-shell --packages /opt/spark/jars/delta-core_2.12-1.1.0.jar

CMD pyspark  \
    --master local[*] \
    --packages /opt/spark/jars/delta-core_2.12-1.1.0.jar \
    --packages org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.11.901,org.apache.hadoop:hadoop-common:3.3.1 \
    /opt/spark/app.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.functions import lit
from pyspark.sql.types import StructType, StructField, ArrayType, StringType, IntegerType, DoubleType
from pyspark.sql.utils import AnalysisException
from delta import *
import boto3
import time
import json
import os

print("APP-INFO: Started spark job json2delta")

#TODO: static values -> change to env templating
s3_endpoint_url = "http://minio.eqms-minio.svc.cluster.local:80"
s3_bucket_name = "eqms"
aws_access_key_id = "eqms-spark"
aws_secret_access_key = "change-me"

print("APP-INFO: Building Spark Context...")
builder = SparkSession.builder.appName("json2delta-app") \
.config("spark.hadoop.fs.s3a.access.key", aws_access_key_id) \
.config("spark.hadoop.fs.s3a.secret.key", aws_secret_access_key) \
.config("spark.jars.packages", "delta-core_2.12-1.1.0.jar") \
.config("spark.jars.packages", "hadoop-aws-3.3.1.jar") \
.config("spark.jars.excludes", "com.google.guava:guava") \
.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
.config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
.config("spark.hadoop.fs.s3a.path.style.access", "true") \
.config('spark.hadoop.fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider') \
.config("spark.hadoop.fs.s3a.endpoint", s3_endpoint_url) \
.config("spark.delta.logStore.class", "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore") \
.config("hive.metastore.uris", "thrift://eqms-hive-metastore.default.svc.cluster.local:9083") \
.config("spark.sql.catalogImplementation", "hive") \
.config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
.enableHiveSupport()
spark = configure_spark_with_delta_pip(builder).getOrCreate()
print("APP-INFO: Building Spark Context finished")

def getAllJsonPaths(bucketName, subpath):
    fPaths = []
    s3_bucket = s3.Bucket(bucketName)
    for obj in s3_bucket.objects.filter(Prefix=subpath):
        if obj.key.endswith('.json'):
            print("found item: " + obj.key)
            fPaths.append(obj.key)
    return fPaths

bucket_url = "s3a://" + s3_bucket_name + "/"
subf_api_new = "apis-new/usgs/"
subf_api_old = "apis-old/usgs/"
subf_api_failed = "apis-failed/usgs/"
subf_delta = "deltabase.db/eqms/"

try:
    print("APP-INFO: Creating DB in metastore if not existing...")
    spark.sql("CREATE DATABASE IF NOT EXISTS deltabase;")
    print("APP-INFO: Creating table entrys in metastore from " +  bucket_url + subf_delta + " if not existing...")
    spark.sql("CREATE TABLE IF NOT EXISTS deltabase.eqms USING delta LOCATION '"+ bucket_url + subf_delta +"';")
except Exception as e:
    print(f"APP-EXCEPTION:  {e}")

while(True):
    # look for json data from apis
    try:
        s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key, endpoint_url=s3_endpoint_url, region_name='eu-central-1')
        bucket = s3.Bucket(s3_bucket_name)

        print("APP-INFO: looking for json in " + s3_bucket_name + "/" + subf_api_new)
        jsonPaths = getAllJsonPaths(bucketName=s3_bucket_name, subpath=subf_api_new)
        if(len(jsonPaths) > 0):
            for fpath in jsonPaths:
                try:
                    convert_failed = False
                    print("APP-INFO: Loading " + fpath)
                    jdf = spark.read.option("multiLine", "true").json(bucket_url + fpath)
                    jdf.show()
                    print("APP-INFO: saving to delta table...")

                    eq_data = jdf.selectExpr("inline(features)")        \
                        .withColumn("id", col("id").cast("string")) \
                        .withColumn("longitude", col("geometry.coordinates").getItem(0).cast("double")) \
                        .withColumn("latitude", col("geometry.coordinates").getItem(1).cast("double"))  \
                        .withColumn("depth", col("geometry.coordinates").getItem(2).cast("double")) \
                        .withColumn("geometry.type", col("geometry.type").cast("string")) \
                        .withColumn("dmin", col("properties.dmin").cast("double")) \
                        .withColumn("sources", col("properties.sources").cast("string")) \
                        .withColumn("tz", col("properties.tz").cast("integer")) \
                        .withColumn("mmi", col("properties.mmi").cast("double")) \
                        .withColumn("type", col("properties.type").cast("string")) \
                        .withColumn("title", col("properties.title").cast("string")) \
                        .withColumn("magType", col("properties.magType").cast("string")) \
                        .withColumn("nst", col("properties.nst").cast("integer")) \
                        .withColumn("sig", col("properties.sig").cast("integer")) \
                        .withColumn("tsunami", col("properties.tsunami").cast("integer")) \
                        .withColumn("mag", col("properties.mag").cast("double")) \
                        .withColumn("alert", col("properties.alert").cast("string")) \
                        .withColumn("gap", col("properties.gap").cast("double")) \
                        .withColumn("rms", col("properties.rms").cast("double")) \
                        .withColumn("place", col("properties.place").cast("string")) \
                        .withColumn("net", col("properties.net").cast("string")) \
                        .withColumn("code", col("properties.code").cast("string")) \
                        .withColumn("ids", col("properties.ids").cast("string")) \
                        .withColumn("types", col("properties.types").cast("string")) \
                        .withColumn("felt", col("properties.felt").cast("integer")) \
                        .withColumn("cdi", col("properties.cdi").cast("double")) \
                        .withColumn("url", col("properties.url").cast("string")) \
                        .withColumn("time", col("properties.time").cast("long")) \
                        .withColumn("detail", col("properties.detail").cast("string")) \
                        .withColumn("updated", col("properties.updated").cast("long")) \
                        .withColumn("status", col("properties.status").cast("string"))
                    
                    meta_data = jdf \
                        .withColumn("metadata.generated", col("metadata.generated").cast("long")) \
                        .withColumn("metadata.count", col("metadata.count").cast("integer")) \
                        .withColumn("metadata.api", col("metadata.api").cast("string")) \
                        .withColumn("metadata.title", col("metadata.title").cast("string")) \
                        .withColumn("metadata.url", col("metadata.url").cast("string")) \
                        .withColumn("metadata.status", col("metadata.status").cast("integer")) \
                        .withColumn("eq_hash_key", col("eq_hash_key").cast("string")) \
                        .withColumn("api_name", col("api_name").cast("string")) 
                    
                    usgs_data = eq_data
                    meta_data = meta_data.withColumnRenamed("type", "api.data.type")
                    usgs_data = usgs_data.withColumn("constant", lit(1))
                    usgs_data = meta_data.crossJoin(usgs_data).drop("constant")
                    usgs_data = usgs_data.drop("features")
                    usgs_data = usgs_data.drop("metadata")
                    usgs_data = usgs_data.drop("properties")
                    usgs_data = usgs_data.drop("geometry")
                    usgs_data = usgs_data.drop("bbox")

                    usgs_data.write.format("delta").mode("append").save(bucket_url + subf_delta)
                    
                except AnalysisException as ae:
                    print(f"APP-EXCEPTION: {ae}")
                    print("APP-INFO: Converting failed, trying to archive to failed...")
                    convert_failed = True
                    print("APP-INFO: archiving " + fpath + " to " + subf_api_failed)
                    sobject = bucket.Object(fpath)
                    sobject.copy_from(Bucket=s3_bucket_name, CopySource=f'{s3_bucket_name}/{fpath}', Key=subf_api_old + fpath.replace(subf_api_new, ""))
                    print("APP-INFO: deleting " + fpath)
                    bucket.Object(fpath).delete()
                    print("APP-INFO: successfully archived failed file " + fpath)
                except Exception as e:
                    print(f"APP-EXCEPTION: {e}")
                    print("APP-INFO: trying to write table in errorifexists-mode...")
                    usgs_data.write.format("delta").mode("errorifexists").save(bucket_url + subf_delta)

                if(convert_failed == False):
                    print("APP-INFO: archiving " + fpath + " to " + subf_api_old)
                    sobject = bucket.Object(fpath)
                    sobject.copy_from(Bucket=s3_bucket_name, CopySource=f'{s3_bucket_name}/{fpath}', Key=subf_api_old + fpath.replace(subf_api_new, ""))
                    print("APP-INFO: deleting " + fpath)
                    bucket.Object(fpath).delete()
                    print("APP-INFO: successfully converted and archived " + fpath)
    except Exception as e:
        print(f"APP-EXCEPTION:  {e}")

    try:
        #DEBUG print delta table
        print("APP-DEBUG: Printing current delta table:")
        tdf = spark.read.format("delta").load(bucket_url + subf_delta)
        tdf.show()
    except Exception as e:
        print(f"APP-EXCEPTION:  {e}")

    try:
        print("APP-INFO: Creating DB in metastore if not existing...")
        spark.sql("CREATE DATABASE IF NOT EXISTS deltabase;")
        print("APP-INFO: Creating table entrys in metastore from " +  bucket_url + subf_delta + " if not existing...")
        spark.sql("CREATE TABLE IF NOT EXISTS deltabase.eqms USING delta LOCATION '"+ bucket_url + subf_delta +"';")
    except Exception as e:
        print(f"APP-EXCEPTION:  {e}")

    print("APP-INFO: Currently no data to convert available, sleeping for 30s...")
    time.sleep(30)

spark.stop()

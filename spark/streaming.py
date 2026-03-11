import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

import pyspark

# Required packages for Kafka and PostgreSQL
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.6.0 pyspark-shell'
# Let PySpark resolve SPARK_HOME and JAVA_HOME implicitly in Linux

# Kafka Configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
TOPIC_NAME = "transactions_topic"

# PostgreSQL Configuration
PG_URL = os.environ.get("PG_URL", "jdbc:postgresql://localhost:5433/pipelinedb")
PG_PROPERTIES = {
    "user": "user",
    "password": "password",
    "driver": "org.postgresql.Driver"
}

def write_to_postgres(batch_df, batch_id):
    """Write micro-batch to PostgreSQL."""
    batch_df.write \
        .jdbc(url=PG_URL, table="transactions", mode="append", properties=PG_PROPERTIES)
    print(f"Batch {batch_id} written to PostgreSQL")

def main():
    spark = SparkSession.builder \
        .appName("RealTimeDataPipeline") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.6.0") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")

    # Define the schema of the incoming JSON data
    schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("transaction_type", StringType(), True),
        StructField("transaction_timestamp", TimestampType(), True)
    ])

    print("Subscribing to Kafka topic...")
    # Read from Kafka topic
    raw_stream = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", TOPIC_NAME) \
        .option("startingOffsets", "latest") \
        .load()

    # The value is a binary type, cast it to String and parse the JSON
    parsed_stream = raw_stream.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    print("Starting stream to PostgreSQL...")
    # Write stream to PostgreSQL using foreachBatch
    query = parsed_stream \
        .writeStream \
        .foreachBatch(write_to_postgres) \
        .outputMode("append") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()

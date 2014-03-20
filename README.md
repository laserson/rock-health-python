rock-health-python
==================

Code for Rock Health Python-for-Hadoop overview

Using CDH5b2 running YARN, Spark, and Impala


## Get some n-gram data

Get about 20 GB of ngram data from Google:

```bash
# run this on the cluster
# make sure to change the HFDS directories in the script
hadoop fs -mkdir -p /user/laserson/rock-health-python/ngrams
python get_some_ngrams.py
```

Push the data into S3

```bash
hadoop fs \
        -D fs.s3n.awsAccessKeyId=$AWS_ACCESS_KEY_ID \
        -D fs.s3n.awsSecretAccessKey=$AWS_SECRET_ACCESS_KEY \
        -cp \
        /user/laserson/rock-health-python/ngrams \
        s3n://rock-health-python/ngrams
```

## Hadoop Streaming


```bash
# find the streaming jar
find /opt/cloudera -name "*streaming*jar"

hadoop jar \
        /opt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-streaming-2.2.0-cdh5.0.0-beta-2.jar \
        -input rock-health-python/ngrams \
        -output rock-health-python/output-streaming \
        -mapper streaming-mapper.py \
        -combiner streaming-reducer.py \
        -reducer streaming-reducer.py \
        -jobconf stream.num.map.output.key.fields=3 \
        -jobconf stream.num.reduce.output.key.fields=3 \
        -jobconf mapred.reduce.tasks=72 \
        -file streaming-mapper.py \
        -file streaming-reducer.py
```

## mrjob

Run in mrjob on cluster

```bash
export HADOOP_HOME="/opt/cloudera/parcels/CDH/lib/hadoop-mapreduce"

./mrjob-ngrams.py -r hadoop \
        --hadoop-bin /usr/bin/hadoop --jobconf mapred.reduce.tasks=72 \
        -o hdfs:///user/laserson/rock-health-python/output-mrjob \
        hdfs:///user/laserson/rock-health-python/ngrams
```

Run in mrjob through AWS

```bash
# remember to set your AWS credentials
./mrjob-ngrams.py -r emr \
        --ec2-instance-type m1.large \
        --num-ec2-instances 13 \
        --no-output \
        --output-dir s3://rock-health-python/output-mrjob \
        s3://rock-health-python/ngrams/*
```


## luigi

You must point to your streaming jar in a `client.cfg` file.

```bash
python luigi-ngrams.py Ngrams \
        --local-scheduler \
        --n-reduce-tasks 10 \
        --source hdfs:///user/laserson/rock-health-python/ngrams \
        --destination hdfs:///user/laserson/rock-health-python/output-luigi
```


## PySpark

PySpark can do this interactively.  First start a PySpark shell

```bash
export SPARK_JAVA_OPTS="-Dspark.executor.memory=30g"
MASTER=spark://bottou01-10g.pa.cloudera.com:7077 IPYTHON=1 pyspark
```

Then interactively compute

```python
# we are cheating a bit here bc the map function is simplified
from spark_ngrams import process_ngram_cheat

ngrams = sc.textFile("hdfs:///user/laserson/rock-health-python/ngrams")

neighbors = ngrams.flatMap(process_ngram_cheat).reduceByKey(lambda x, y: x + y)

ngrams.cache()
```


## BigML model scoring

Download the iris data

```bash
wget http://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data

# start a PySpark shell
MASTER=spark://bottou01-10g.pa.cloudera.com:7077 IPYTHON=1 pyspark
```

Now using PySpark, expand the data set and save to HDFS

```python
# load the raw data
with open('iris.data', 'r') as ip:
    raw = filter(lambda x: x != '', [line.strip() for line in ip])

single = sc.parallelize(raw, 5).map(lambda line: '\t'.join(line.split(',')[:-1]))
replicated = single.flatMap(lambda x: [x]*1000000)
replicated.saveAsTextFile('rock-health-python/iris_text')
```

Now, register this data set with Impala so it can read it

```sql
CREATE DATABASE IF NOT EXISTS rock_health;
USE rock_health;

CREATE EXTERNAL TABLE iris_text (
    sepal_length DOUBLE,
    sepal_width DOUBLE,
    petal_length DOUBLE,
    petal_width DOUBLE
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/laserson/rock-health-python/iris_text';
```

Score the model on the ~150M points with PySpark

```python
from models import predict_species
observations = sc.textFile('/user/laserson/rock-health-python/iris_text') \
        .map(lambda line: tuple([float(val) for val in line.split('\t')[1:]]))
predictions = observations.map(lambda tup: predict_species(*tup))
predictions.distinct().collect()
```

Create a UDF from the Python model

```python
from impala.dbapi import connect
from impala.udf import ship_udf
from numba.ext.impala import udf, FunctionContext, DoubleVal, IntVal
from models import predict_species

# connect to impala
host = 'bottou01-10g.pa.cloudera.com'
user = 'laserson'
conn = connect(host=host, port=21050)
cursor = conn.cursor(user='laserson')
cursor.execute('USE rock_health')

# compile and ship
predict_species = udf(IntVal(FunctionContext, DoubleVal, DoubleVal, DoubleVal))(predict_species)
ship_udf(cursor, predict_species, '/user/laserson/rock-health-python/iris.ll', host, user=user)

# run the same query
cursor.execute("SELECT DISTINCT predict_species(sepal_width, petal_length, petal_width) FROM iris_text")
```

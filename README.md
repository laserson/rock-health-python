rock-health-python
==================

Code for Rock Health Python-for-Hadoop overview

Using CDH5b2 running YARN and Spark


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


Run streaming example

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


Run in mrjob on cluster

```bash
export HADOOP_HOME="/opt/cloudera/parcels/CDH/lib/hadoop-mapreduce"

./mrjob-ngrams.py -r hadoop \
        --hadoop-bin /usr/bin/hadoop --jobconf mapred.reduce.tasks=72 \
        -o hdfs:///user/laserson/rock-health-python/output-mrjob \
        hdfs:///user/laserson/rock-health-python/ngrams

# remember to set your AWS credentials
./mrjob-ngrams.py -r emr \
        --ec2-instance-type m1.large \
        --num-ec2-instances 13 \
        --no-output \
        --output-dir s3://rock-health-python/output-mrjob \
        s3://rock-health-python/ngrams/*
```




Now for luigi.  You must point to your streaming jar in a `client.cfg` file.

```bash
python luigi-ngrams.py Ngrams \
        --local-scheduler \
        --n-reduce-tasks 10 \
        --source hdfs:///user/laserson/rock-health-python/ngrams \
        --destination hdfs:///user/laserson/rock-health-python/output-luigi
```








```sql
CREATE DATABASE rock_health;
```

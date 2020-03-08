---
layout: post
title:  "Apache Spark - SparkUI: Deep Dive"
date:   2020-01-07 10:17:00 +0700
categories: [apache-spark]
---

## Apache Spark Internals - Deep Dive 

The driver program hosts `SparkContext()`, which is the heart of the Spark Application. A channel is required to be set up via the cluster manager and the Driver Program that offers resources to host the application. The application thereafter is shipped to Worker Nodes to host executors and run multiple tasks simultaneously. As the application is up and running, multiple JVMs kick off in a production environment – even though the distributed environment: the application – has been written as if one had only a single JVM. Thus, the Spark UI Console is a useful tool for us to measure the details of the Spark Application to improve its performance. Since the cluster manager assigns Worker Node(s) to the program, SparkContext() will communicate directly with executors. The communication between executors and the drivers happen via RPC messages through Netty (org.apache.spark.rpc.netty) – a low level infrastructure - that sends current statuses of the Spark Application. 
Through Event Sources the `DAGScheduler` takes the RDD lineage and evaluates the execution plan with the help of the `TaskSchedulerImpl` and `SchedulerBackend` (`CoarseGrainedSchedulerBackend`) - the main scheduler backend. In case dynamic partitioning is of interest, there are different customized scheduler backends for Yarn and Mesos (`FineGrainedSchedulerBackend` (deprecated)) in cluster mode. These components communicate and exchange information about the Spark Application. One can intervene via the `SparkContext()` that talks to this distributed environment responsible for executing the tasks assigned to them by the driver.  Event Buses – single threaded components – process all the events that were sent during the execution of the DSL that expresses distributed computations using this distributed environment like Hadoop Yarn or built-in Spark Standalone. 

When `SparkContext()` is fully initialized and the tasks are submitted to the `DAGScheduler`, the Spark Application starts. Throughout initialization, `SparkContext()` starts a `LiveListenerBus` that is responsible for processing the events as the application is being set up. The second Bus is the `JobProgressListener` (with `LiveListenerBus`) responsible for collecting all the data that the SparkUI (controlled by spark.ui.enabled) uses to show the statistics. A way to optimize Spark is to disable the webUI  (which in turn will not start listeners [“`EnvironmentListener”`, “`StorageStatusListener`”, “`ExevuttorsListener`”, “`StorageListener`”, “`RDDOperationGraphListener`”] with `LiveListenerBus`) to lower the pressure on the driver JVM and in turn make it faster without collecting data on the JVM. The SparkUI is only displayable because all the SparkListeners collected the information about the distributed computation (Spark Application). The SparkUI is available at port 4040 by default – in case it is taken Spark will find the next consecutive available port. The Spark Application UI is only available when the application is running. Once the `SparkContext()` is stopped the SparkUI is gone. If the preservation of the SparkUI information is of interest, Spark History Server needs to be enabled – essentially this is a UI of the logs that were collected while the application was up and running. To sum up, Spark UI is just a bunch of `SparkListeners` that collect all the information that the webUI will ever show – thus the information available on the SparkUI is limited to the available information collected by the SparkListeners. The JobProgressListener combines all the information in over 20 internal registries to make the lookup faster while the ExecutorsListener show you the event timeline for executors. 
The `LiveListenerBus` (forwarding and intercepting events one by one) to SparkListeners is created when the SparkContext() starts and it lives in the driver along with the `DAGScheduler` and `TaskScheduler` – when `spark-submit` happens in the application, the SparkListenerEvent Event Bus asynchronously processes these information. To simplify, we have multiple events passed by/to executors by/to the driver. However, in case of Structured Streaming, we have LiveListenerBus event buses. Spark History Server has an individual listener bus behaving as if the application was still running after termination. It reads JSON encoded events from a file and shows the sparkUI. These events are passed by the DAGScheduler and SparkContext to the LiveListenerBus. 

SparkListener is essentially a developer API that can be used to extend what is available in Spark out-of-the-box. By extending the SparkListener, we can access all the information that spark shows through the SparkUI. Another approach is to use the `SparkFirehoseListener` – (the interface is different from the API perspective). We can also register custom listener through `SparkContext.addSparkListener` / `spark.extraListener`s. Eventually, SparkListener will provide us with IPs and all the information that is available in the web UI. 

## Spark Monitoring
There are several open-source projects offering Jupyter Notebook extensions for Apache Spark integration.

#### Jupyter Spark (Mozilla)

**Jupyter Spark** by Mozilla includes a progress indicator for the current Notebook cell if it invokes a Spark job. Queries the Spark UI service on the backend to get the required Spark job information.
Mozilla uses `jupyter notebook --Spark.url="http://localhost:4040"` to scrape the UI and reconstruct it within Jupyter. They  take unnecessary extra steps and their approach will not work well in cluster mode, because they don't retrieve the YARN application state via YARN's (/ResourceManager's) REST API.

**What Mozilla critically lacks:**
- https://archive.cloudera.com/cdh5/cdh/5/hadoop/hadoop-yarn/hadoop-yarn-site/WebServicesIntro.html#Example_usage
- https://archive.cloudera.com/cdh5/cdh/5/hadoop/hadoop-yarn/hadoop-yarn-site/ResourceManagerRest.html#Cluster_Application_API

For example, Spark exposes a Web UI via the REST API at http://localhost:4040/api/v1/applications , which looks exactly what they are scraping - and is already in a JSON format:
```json
[ {
"id" : "local-1583668951936",
"name" : "PySparkShell",
"attempts" : [ {
"startTime" : "2020-03-08T12:02:30.896GMT",
"endTime" : "1969-12-31T23:59:59.999GMT",
"lastUpdated" : "2020-03-08T12:02:30.896GMT",
"duration" : 0,
"sparkUser" : "mikepetridisz",
"completed" : false,
"appSparkVersion" : "2.4.5",
"startTimeEpoch" : 1583668950896,
"endTimeEpoch" : -1,
"lastUpdatedEpoch" : 1583668950896
....
} ]
} ]
```

A way to explore this JSON file would looks like this (without bs4 scraping):
```scala
%scala
val df = spark.read.json("/var/log/spark-history/application_XYZ_..")
df.filter("Event='SParkListenerTaskEnd'").select("Task Metrics.*").printSchema...
```
These Spark internal Task metrics provide info on the executor activity, run time, CPU time used, I/O metrics, JVM, Garbage Collection, Shuffle activity, etc.

#### Spark Monitor by CERN
Spark Monitor uses the programmatic interface via SparkListeners.
- Their custom class: extends SparkListener:
  - class `StageInfoRecorderListener` extends `SparkListener` {...}
  - Methods react on events to collect data:
  - `override def onStageCompleted(stageCompleted: SparkListenerStageCompleted): Unit = {`
```scala
val stageInfo = stageCompleted.stageInfo`
val taskMetrics = stageInfo.taskMetrics
val jobId = StageIdtoJobId(stageInfo.stageId)
```
  - Attaching custom Listener class to Spark Session:
  - `--conf spark.extraListeners=..`

```scala
from sparkmeasure import StageMetrics
stagemetrics = StageMetrics(spark)

# print report to standard output
stagemetrics.print_report()

# Save session metrics data in json format:
df = stagemetrics.create_stagemetrics_DF("PerfStageMetrics")
stagemetrics.save_data(df.orderBy("jobId", "stageId"), "/tmp/stagemetrics_test1"
```

Takeaway: Spark Monitor lacks spark.sparkContext.statusTracker

#### What are some other ways to monitor Spark?


**(1) Dropwizard/Codahale metrics library**
External monitoring tools, such as:
https://metrics.dropwizard.io/4.1.2/
http://ganglia.sourceforge.net/
http://dag.wiee.rs/home-made/dstat/
https://linux.die.net/man/1/iostat


**(2) History Server **

History Server reads from Event Log (JSON file)
`./sbin/start-history-server.sh`
`spark.eventLog.enabled=true`
`spark.eventLog.dir = <path>`

If we run in cluster mode, we can reconstruct the UI of a finished application through Spark’s history server like this:
```scala
# in your spark-defaults.conf file add the following properties
spark.eventLog.enabled true
spark.eventLog.dir hdfs://LOCATION/TO/SPARK/EVENT/LOG

spark.yarn.historyServer.address SPARK_HISTORY_SERVER_HOST
spark.history.ui.port SPARK_HISTORY_SERVER_PORT

spark.yarn.services org.apache.spark.deploy.yarn.history.YarnHistoryService
spark.history.fs.logDirectory hdfs://LOCATION/TO/SPARK/EVENT/LOG

# starting the history server
$/PATH/TO/SPARK/sbin/start-history-server.sh
```

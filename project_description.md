# Final Assignment: Robust Journey Planning

Executive summary - build a robust SBB journey planner for the Zürich area, and make a short video presentation of it - to be done in **groups of 4 or 5**, before **May 25**, noon.

## Content

* [Important dates](#important-dates)
* [Problem Motivation](#problem-motivation)
* [Problem Description](#problem-description)
* [Project submission checklist](#project-submission-checklist)
* [Grading method](#grading-method)
* [Dataset description](#dataset-description)

    - [Actual data](#actual-data)
    - [Time tables](#time-table-data)
    - [Stations data](#stations-data)
    - [Misc data](#misc-data)

* [Hints](#hints)
* [References](#references)
* [FAQ](#faq)

## Important dates

The assignment (clear, well-annotated notebook; report-like), **with a short, 7-minute video of your presentation** is due on **Monday May 25th, 12:00 (noon) CEST** (note the change of date).

Instead of an oral defense as initially planned, we will organize short Q&A discussions of 6 minutes per group. These discussions will be scheduled on **Wednesday May 27th, 13:00 - 17:30 CEST** - tentatively, actual times to be discussed on a case by
case basis.

## Problem Motivation

Imagine you are a regular user of the public transport system, and you are checking the operator's schedule to meet your friends for a class reunion.
The choices are:

1. You could leave in 10mins, and arrive with enough time to spare for gossips before the reunion starts.

2. You could leave now on a different route and arrive just in time for the reunion.

Undoubtedly, if this is the only information available, most of us will opt for option 1.

If we now tell you that option 1 carries a fifty percent chance of missing a connection and be late for the reunion. Whereas, option 2 is almost guaranteed to take you there on time. Would you still consider option 1?

Probably not. However, most public transport applications will insist on the first option. This is because they are programmed to plan routes that offer the shortest travel times, without considering the risk factors.

## Problem Description

In this final project you will build your own _robust_ public transport route planner to improve on that. You will reuse the SBB dataset (See next section: [Dataset Description](#dataset-description)).

Given a desired arrival time, your route planner will compute the fastest route between two stops within a provided uncertainty tolerance expressed as interquartiles.
For instance, "what route from A to B is the fastest at least Q% of the time if I want to leave from A (resp. arrive at B) at instant T". Note that *uncertainty* is a measure of a route not being feasible within the time computed by the algorithm.

In order to answer this question you will need to:

- Model the public transport infrastructure for your route planning algorithm using the data provided to you.
- Build a predictive model using the historical arrival/departure time data, and optionally other sources of data.
- Implement a robust route planning algorithm using this predictive model.
- Test and validate your results.
- Implement a simple Jupyter-based visualization to demonstrate your method, using Jupyter dashboard such as [Voilà](https://voila.readthedocs.io/en/stable/) or [ipywidgets](https://ipywidgets.readthedocs.io/en/stable/user_guide.html).

Solving this problem accurately can be difficult. You are allowed a few **simplifying assumptions**:

- We only consider journeys at reasonable hours of the day, and on a typical business day, and assuming the schedule of May 13-17, 2019.
- We allow short (max 500m "As the Crows Flies") walking distances for transfers between two stations, and assume a walking speed of _50m/1min_ on a straight line, regardless of obstacles, human-built or natural, such as building, highways, rivers, or lakes.
- We only consider journeys that start and end on known station coordinates (train station, bus stops, etc.), never from a random location.
- We only consider stations in a 15km radius of Zürich's train station, `Zürich HB (8503000)`, (lat, lon) = `(47.378177, 8.540192)`.
- We only consider stations in the 15km radius that are reachable from Zürich HB, either directly, or via transfers through other stations within the area.
- There is no penalty for assuming that delays or travel times on the public transport network are uncorrelated with one another.
- Once a route is computed, a traveller is expected to follow the planned routes to the end, or until it fails (i.e. miss a connection).
  You **do not** need to address the case where travellers are able to defer their decisions and adapt their journey "en route", as more information becomes available. This would require to consider all alternative routes (contingency plans) in the computation of the uncertainty levels, which is more difficult to implement.
- The planner will not need to mitigate the traveller's inconvenience if a plan fails. Two routes with identical travel times under the uncertainty tolerance are equivalent, even if the outcome of failing one route is much worse for the traveller than failing the other route, such as being stranded overnight on one route and not the other.
- You do not need to optimize the method, as long as the run-time is reasonable.
- You may assume that the timetables remain unchanged throughout the 2018 - 2019 period.

We will also prepare the data in a form you can easily use and provide you with boiler-plate code to help you with the task,
such as for visualizing routes etc.

## Project submission checklist

* Project and 7-minute video are due before noon of May 25th.

* The final assignment is to be done in **groups of 4 or 5**, remember to update your group member list if needed.

* All projects must be submitted on Renku, as a group project.

* Project must contain `final` in the name, or you can fork the project from [dslab2020/final_project](https://renku.iccluster.epfl.ch/projects/dslab2020/final_project) 

* Project sizes, including history, must not exceed 100Mb. Use git-lfs for your larger data sets, or keep as much data as possible on HDFS.
  Use `git rebase -i <commit-id>` if you accidentally push a large data set on gitlab (you'll need to unprotect your branch and force `git push -f`)

 
## Grading Method

At the end of the term you will provide a 7-minute video, in which each member of the project presents a part of the project.

After reviewing your videos, we will invite each group for a 6 mins Q&A. Before the Q&A, we will validate your method on a list of
pre-selected departure arrival points, and times of day.

We will give grades based on the code, videos and Q&A.

We will use the following criteria:

1. The clarity and conciseness of the video presentation, code and Q&A
2. The formulation of the problem and its decomposition into smaller tasks
3. The originality of the solution design (system design, analytics, presentation)
4. The quality of the implementation
5. The explanation of the pro's and con's / shortcomings of the proposed solution

The solution and associated implementation & explanations will be weighted across the different parts as follows:

- Design and method used to model the public transport network: 20%
- Design and method used to create the predictive models: 20%
- Route planning algorithm: 20%
- Validation method: 20%
- Presentation: 20%

Think of yourselves as a startup trying to sell your solution to the board of a public transport
company. Your video is your elevator pitch. It must be short and convincing, while
keeping up with the aforementioned criterias.

## Dataset Description

For this project we will use the data published on the [Open Data Platform Mobility Switzerland](<https://opentransportdata.swiss>).

We will use the SBB data limited around the Zurich area, focusing only on stops within 15km of the Zurich main train station.

#### Actual data

Students should already be familiar with the [istdaten](https://opentransportdata.swiss/de/dataset/istdaten). A daily feed is available
from the open data platform mobility, and [google drive archives](https://drive.google.com/drive/folders/1SVa68nJJRL3qgRSPKcXY7KuPN9MuHVhJ).

The 2018 and 2019 data is available in csv format and as a Hive table on our HDFS system, under `/data/sbb/istdaten` and `data/sbb/orc` respectively.

Format: the csv istdaten dataset is presented as a collection of textfiles with fields separated by ';' (semi-colon).
There is one bzip compressed file per day, e.g. `/data/sbb/istdaten/2018/01/2018-01-01istdaten.csv.bz2`.
The orc istdaten dataset is presented as a single Hive table.

See homeworks of weeks 3 and 4 for more information about this data, and the methods to access it.

Alternatively, as a backup, and if everything else fails, you can download an older subset of this data from the following links.

- [2017-09.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/2017-09.tar.lzma)
- [2017-10.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/2017-10.tar.lzma)
- [2017-11.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/2017-11.tar.lzma)
- [2017-12.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/2017-12.tar.lzma)
- [2018-01.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/2018-01.tar.lzma)
- [2018-02.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/2018-02.tar.lzma)
- [2018-03.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/2018-03.tar.lzma)
- [2018-04.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/2018-04.tar.lzma)
- [metadata.tar.lzma](https://os.unil.cloud.switch.ch/swift/v1/CFF/metadata.tar.gz)

We provide the relevant column descriptions below.
The full description of the data is available in the opentransportdata.swiss data [istdaten cookbooks](https://opentransportdata.swiss/en/cookbook/actual-data/).
If needed you can translate the column names and descriptions from
German to English with an automated translator, such as [DeepL](<https://www.deepl.com>).

- `BETRIEBSTAG`: date of the trip
- `FAHRT_BEZEICHNER`: identifies the trip
- `BETREIBER_ABK`, `BETREIBER_NAME`: operator (name will contain the full name, e.g. Schweizerische Bundesbahnen for SBB)
- `PRODUCT_ID`: type of transport, e.g. train, bus
- `LINIEN_ID`: for trains, this is the train number
- `LINIEN_TEXT`,`VERKEHRSMITTEL_TEXT`: for trains, the service type (IC, IR, RE, etc.)
- `ZUSATZFAHRT_TF`: boolean, true if this is an additional trip (not part of the regular schedule)
- `FAELLT_AUS_TF`: boolean, true if this trip failed (cancelled or not completed)
- `HALTESTELLEN_NAME`: name of the stop
- `ANKUNFTSZEIT`: arrival time at the stop according to schedule
- `AN_PROGNOSE`: actual arrival time (when `AN_PROGNOSE_STATUS` is `GESCHAETZT`)
- `AN_PROGNOSE_STATUS`: look only at lines when this is `GESCHAETZT`. This indicates that `AN_PROGNOSE` is the measured time of arrival.
- `ABFAHRTSZEIT`: departure time at the stop according to schedule
- `AB_PROGNOSE`: actual departure time (when `AN_PROGNOSE_STATUS` is `GESCHAETZT`)
- `AB_PROGNOSE_STATUS`: look only at lines when this is `GESCHAETZT`. This indicates that `AB_PROGNOSE` is the measured time of arrival.
- `DURCHFAHRT_TF`: boolean, true if the transport does not stop there

Each line of the file represents a stop and contains arrival and departure times. When the stop is the start or end of a journey, the corresponding columns will be empty (`ANKUNFTSZEIT`/`ABFAHRTSZEIT`).
In some cases, the actual times were not measured so the `AN_PROGNOSE_STATUS`/`AB_PROGNOSE_STATUS` will be empty or set to `PROGNOSE` and `AN_PROGNOSE`/`AB_PROGNOSE` will be empty.

#### Time table data

We have copied the  [timetable](https://opentransportdata.swiss/en/cookbook/hafas-rohdaten-format-hrdf/#Abgrenzung) to HDFS, under
`/data/sbb/timetables/csv/`.

Only GTFS format has been copied on HDFS, the full description of which is available in the opentransportdata.swiss data [timetable cookbooks](https://opentransportdata.swiss/en/cookbook/gtfs/).
The more courageous who want to give a try at the [HDFS](https://opentransportdata.swiss/en/cookbook/hafas-rohdaten-format-hrdf/) format must contact us.

You will find there the timetables for the years [2018](https://opentransportdata.swiss/en/dataset/timetable-2018-gtfs)-[2019](https://opentransportdata.swiss/en/dataset/timetable-2019-gtfs) in GTFS format.
The timetables are updated weekly. It is however, ok to assume that the weekly changes are small, and a timetable for
a given week is thus the same for the full year - you can for instance use the schedule of May 13-17, 2019, which was
a typical week for the year.

In addition, we have also converted the files corresponding to the week of May 14th 2019 to the ORC format.
You can find them under `/data/sbb/timetables/orc`.
This format is easily read in Spark as illustrated in the following example. Replace `stop_times` with the appropriate name
in order to read the other tables.

```
spark.read.orc("hdfs:///data/sbb/timetables/orc/stop_times").registerTempTable("stop_times_df")
sqlContext.sql("select * from stop_times_df limit 10)").show(10)
```

Alternatively, `sqlContext` provides a full hive context in Spark, and it supports most of Hive _DDL_, _DML_ (but don't), and _Data Retrieval_ queries.
For your convenience, we include with each data type below, the _DDL_ query that was used to create the external tables in Hive.

**Note**: if you use the HiveContext in Spark, it will use by default a local metadata store, which means that you will
need to create your database and tables from scratch using the usual _DDL_ commands. You can configure your sparkmagic session
to connect to an existing metadata store, but unless you want to access pre-existing views managed by Hive,
you will most probably not need to do that. 

We provide a summary description of the files below. The most relevant files are marked by (+):

* stops.txt(+):

    - `STOP_ID`: unique identifier (PK) of the stop
    - `STOP_NAME`: long name of the stop
    - `STOP_LAT`: stop latitude (WGS84)
    - `STOP_LON`: stop longitude
    - `LOCATION_TYPE`:
    - `PARENT_STATION`: if the stop is one of many collocated at a same location, such as platforms at a train station
    
    The data (3rd week May 2019) is available in ORC format under `/data/sbb/timetables/orc/stops/` - as follows:
    
    ```
    create external table <database>.sbb_stops_orc(
        STOP_ID        string,
        STOP_NAME      string,
        STOP_LAT       double,
        STOP_LON       double,
        LOCATION_TYPE  string,
        PARENT_STATION string
    )
    stored as orc
    location '/data/sbb/timetables/orc/stops'
    tblproperties ('orc.compress'='SNAPPY','immutable'='true');
    ```

* stop_times.txt(+):

    - `TRIP_ID`: identifier (FK) of the trip, unique for the day - e.g. _1.TA.1-100-j19-1.1.H_
    - `ARRIVAL_TIME`: scheduled (local) time of arrival at the stop (same as DEPARTURE_TIME if this is the start of the journey)
    - `DEPARTURE_TIME`: scheduled (local) time of departure at the stop 
    - `STOP_ID`: stop (station) identifier (FK), from stops.txt
    - `STOP_SEQUENCE`: sequence number of the stop on this trip id, starting at 1.
    - `PICKUP_TYPE`:
    - `DROP_OFF_TYPE`:
    
    This data is available in ORC format under `/data/sbb/timetables/orc/stop_times/` - as follows:
    
    ```
    create external table <database>.sbb_stop_times_orc(
        TRIP_ID        string,
        ARRIVAL_TIME   string,
        DEPARTURE_TIME string,
        STOP_ID        string,
        STOP_SEQUENCE  smallint,
        PICKUP_TYPE    tinyint,
        DROP_OFF_TYPE  tinyint
    )
    stored as orc
    location '/data/sbb/timetables/orc/stop_times'
    tblproperties ('orc.compress'='SNAPPY','immutable'='true');
    ```

* trips.txt:

    - `ROUTE_ID`: identifier (FK) for the route. A route is a sequence of stops. It is time independent.
    - `SERVICE_ID`: identifier (FK) of a group of trips in the calendar, and for managing exceptions (e.g. holidays, etc).
    - `TRIP_ID`: is one instance (PK) of a vehicle journey on a given route - the same route can have many trips at regular intervals; a trip may skip some of the route stops.
    - `TRIP_HEADSIGN`: displayed to passengers, most of the time this is the (short) name of the last stop.
    - `TRIP_SHORT_NAME`: internal identifier for the trip_headsign (note TRIP_HEADSIGN and TRIP_SHORT_NAME are only unique for an agency)
    - `DIRECTION_ID`: if the route is bidirectional, this field indicates the direction of the trip on the route.
    
    This data is available in ORC format under `/data/sbb/timetables/orc/trips` - as follows:
    
    ```
    create external table <database>.sbb_trips_orc(
        ROUTE_ID        string,
        SERVICE_ID      string,
        TRIP_ID         string,
        TRIP_HEADSIGN   string,
        TRIP_SHORT_NAME string,
        DIRECTION_ID    tinyint
    )
    stored as orc
    location '/data/sbb/timetables/orc/trips'
    tblproperties ('orc.compress'='SNAPPY','immutable'='true');
    ```
    
* calendar.txt:

    - `SERVICE_ID`: identifier (PK) of a group of trips sharing a same calendar and calendar exception pattern.
    - `MONDAY`..`SUNDAY`: 0 or 1 for each day of the week, indicating occurence of the service on that day.
    - `START_DATE`: start date when weekly service id pattern is valid
    - `END_DATE`: end date after which weekly service id pattern is no longer valid
    
    This data is available in ORC format under `/data/sbb/timetables/orc/calendar` - as follows (note we omitted start-end dates):
    
    ```
    create external table <database>.sbb_calendar_orc(
        SERVICE_ID string,
        MONDAY     boolean,
        TUESDAY    boolean,
        WEDNESDAY  boolean,
        THURSDAY   boolean,
        FRIDAY     boolean,
        SATURDAY   boolean,
        SUNDAY     boolean
    )
    stored as orc
    location '/data/sbb/timetables/orc/calendar'
    tblproperties ('orc.compress'='SNAPPY','immutable'='true');
    ```
    
* routes.txt:

    - `ROUTE_ID`: identifier for the route (PK)
    - `AGENCY_ID`: identifier of the operator (FK)
    - `ROUTE_SHORT_NAME`: the short name of the route, usually a line number
    - `ROUTE_LONG_NAME`: (empty)
    - `ROUTE_DESC`: _Bus_, _Zub_, _Tram_, etc.
    - `ROUTE_TYPE`:
    
    This data is available in ORC format under `/data/sbb/timetables/orc/routes` - as follows:
    
    ```
    create external table <database>.sbb_routes_orc(
        ROUTE_ID         string,
        AGENCY_ID        string,
        ROUTE_SHORT_NAME string,
        ROUTE_LONG_NAME  string,
        ROUTE_DESC       string,
        ROUTE_TYPE       smallint
    )
    stored as orc
    location '/data/sbb/timetables/orc/routes'
    tblproperties ('orc.compress'='SNAPPY','immutable'='true');
    ```
    
Notes: PK=Primary Key (unique), FK=Foreign Key (refers to a Primary Key in another table)

The other files are:

* _calendar-dates.txt_ contains exceptions to the weekly patterns expressed in _calendar.txt_.
* _agency.txt_ has the details of the operators
* _transfers.txt_ contains the transfer times between stations or platforms in the stations.

Figure 1. better illustrates the above concepts relating stops, routes, trips and stop times on a real example (route _11-3-A-j19-1_, direction _0_)


 ![journeys](https://renku.iccluster.epfl.ch/gitlab/dslab2020/final_project/raw/master/data/journeys.svg)
 
 _Figure 1._ Relation between stops, routes, trips and stop times. The vertical axis represents the stops along the route,
             the horizontal axis represents the time of day on a non-linear scale. Solid lines connecting the stops correspond to trips.
             A trip is one instances of a vehicle journey on the route. Trips on same route do not need
             to mark all the stops on the route, resulting in trips having different stop lists for the same route.
             

#### Stations data

You can find also find the stations data [BFKOORD_GEO](https://opentransportdata.swiss/en/dataset/bhlist) under HDFS `/data/sbb/stations/bfkoordgeo.csv`.
This list is older and not as complete as the station (stops.txt) data from the GTFS timetables. Nevertheless, it has the altitude information of
the stations, which is not available from the timetable files, in case you need that. You may find several formats of this file, comma separated,
and tab separated. The version in HDFS is in comma separated format.

- `STATIONID`: identifier of the station/stop
- `LONGITUDE`: longitude (WGS84)
- `LATITUDE`: latitude (WGS84)
- `HEIGHT`: altitude (meters) of the stop
- `REMARK`: long name of the stop

#### Misc data

Althought, not required for this final, you are of course free to use any other sources of data of your choice that might find helpful.

You may for instance download regions of openstreetmap [OSM](https://www.openstreetmap.org/#map=9/47.2839/8.1271&layers=TN),
which includes a public transport layer. If the planet OSM is too large for you,
you can find frequently updated exports of the [Swiss OSM region](https://planet.osm.ch/).

Others had some success using weather data to predict traffic delays.
If you want to give a try, web services such as [wunderground](https://www.wunderground.com/history/daily/ch/r%C3%BCmlang/LSZH/date/2019-8-1), can be a good
source of historical weather data.

## Hints

Before you get started, we offer a few hints:

- Reserve some time to Google-up the state of the art before implementing. There is a substantial amount of work on this topic. Look for *time-dependent*, or *time-varying networks*, *stochastic route planning under uncertainty* and *isochrone maps*. You should also look in the references provided below.
- You should already be acquainted with the data.
However, as you learn more about the state of the art, spend time to better understand your data.
Anticipate what can and cannot be done from what is available to you, and plan your design strategy accordingly. Do not hesitate to complete the proposed data sources with your own if necessary.
- Start small with a simple working solution and improve on it.
In a first version, assume that all trains and buses are always sharp on time.
Focus on creating a sane collaborative environment that you can use to develop and test your work in team as it evolves.
Next, work-out the risk-aware solution gradually - start with a simple predictive model and improve it. In addition you can test your algorithm on selected pairs of stops before generalizing to the full public transport network under consideration.

## References

We offer a list of useful references for those of you who want to push it further or learn more about it:

* Adi Botea, Stefano Braghin, "Contingent versus Deterministic Plans in Multi-Modal Journey Planning". ICAPS 2015: 268-272.
* Adi Botea, Evdokia Nikolova, Michele Berlingerio, "Multi-Modal Journey Planning in the Presence of Uncertainty". ICAPS 2013.
* S Gao, I Chabini, "Optimal routing policy problems in stochastic time-dependent networks", Transportation Research Part B: Methodological, 2006.

## FAQ

This section will be updated with the Frequently Asked Questions during the course of this project. Please stay tuned.

##### 1 - Q: Do we need to take into account walking times at the connections?
* **A**: Yes, but since we do not have the details of the platforms at each location, we can use a universal formula to come up with a reasonable walking time.
We must also allow time for transfers between different modes of transports, such as from bus to tramways.
You can use the transfer time information available from `transfers.txt` from the [timetables](#time-table-data).
Otherwise, we assume that `2min` mininum are required for transfers within a same location
(i.e. same lat,lon coordinates), to which you add _1min per 50m_ walking time
to connect two stations that are at most _500m_ appart, on a straight line distance between their two lat,lon. 

##### 2 - Q: Can we assume statistical independence between the observed delays?
* **A**: Yes, see simplifying assumptions in **Problem Description**.
You will incur no penalty for assuming that the delay of a given train (or other mode of transport, ...), at a given location and time is
independent of the delays for all other trains, locations, and times. Even if our experience tells us that this is most of the time not the case.
Also, you must assume that you have no real-time delays information at the time you plan your journey, which limits the benefits you could gain by assuming such a dependency.

##### 3 - Q: Can I take advantage of the fact that a connection departs late most of the time to allow a plan that would otherwise not be possible according to the official schedule.
* **A**: You may discover that you could take advantage of connections that have a high probability of departing late.
However, this is not recommended, or it should come with a warning.
Imagine from a user experience perspective, how would you react if you are being proposed a plan in which a transfer is scheduled to depart before you arrive?
Furthermore, who would you blame if the plan fails: the planner that came up with a theoretically infeasible plan, or the operator who respected their schedule?

##### 4 - Q: How are the inputs of the solution entered
* **A**: You will enter the numerial IDs of the starting and terminating station (bus, trams, trains, ...), a desired time of arrival, and
a minimum confidence level. You do not need to enter a day. The route is for a typical business day of the week, not a week-end, or bank holiday.
That is you can filter out all services that are not on normal business days from your options.
The output must be the service that allows you to leave at the latest, while arriving before the specified time at your destination,
and with a probability of success equal or higher than the specified certainty level.

##### 5 - Q: Do we need to visualize the output on a map
* **A**: You do not need to visualize the results. A list in textual form will be sufficient. Note that the list must display at a minimum
the starting time, the routes, arrival time, and confidence level.
If it involves transfers, the list must also include the arrival & departure times, and intermediate routes at the transfer points.

##### 6 - Q: How do we validate the solution
* **A**: We can give a hint: we will pick two stations and a maximum time of arrival, which has different routes with known
probability of success.  It is a `sucess` if on a given day and time we are
able to catch all the connections and arrive before the specified time limit, otherwise it is a `failure`. We compute the probability
as `number of successes/(number of successes + number of failures)` by repeating this over a given time period of many days
(business days only), and we compare your results, i.e. routes and minimum success guarantee with ours.

##### 7 - Q: If a stop in the 15km radius is connected only through a bus or train that stops outside the 15km radius, should this stop be considered?
* **A**: No, this stop should be considered, because the bus or train goes through stops that are outside the 15km radius.

##### 8 - Q: Can we use any libraries for the project?
* **A**: You are free to use any libraries you want for the project. The only constraint is that you must configure your Docker image
so that we don't have to configure our jupyter environment ourselves in order to validate your results. Feel free to ask us
if you need us to install the library on the hadoop cluster. 

##### 9 - Q: Any preferences for computing geo distances?
* **A**: Any method with a few meters accuracy, is acceptable - the most accurate is the `vincenty` method, but `harversine` is perfectly
fine, or you can use an existing method from one of the provided libraries. We have installed `geopy`, `networkx`, `scikit-learn`,
`bokeh` and `matplotlib` for your convenience.

##### 10 - Q: Can we solve it as shortest path algorithm?
* **A**: Yes, or more precisely as a constrained shortest path algorithm. It is a robust optimization problem. The constraints
are that you must arrive before a time limit with a minimum confidence level,
and it must be a valid route on the the public transport infrastructure and schedule. The objective is to maximize the time of
derpature, so that you spend the least time between the departing stop and the arrival stop, and any algorithm that achieves
this objective is fine. As a starting point, we present you with a list of algorithms you may want to consider: https://transport.okfn.org/index-60.html.

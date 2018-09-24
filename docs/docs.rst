TSLearn Documentation
=============================

Introduction
------------

The `tslearn` package is conceived to allow learning of temporal data as a time-series. It is an integrated suite, so it provides the necessary modules to convolute  and aligned temporal data with implicit states into static data with explicit states.


Prerequisits
------------
While `tslearn` comes as a complete and self contained project, with not too many external dependencies, it is neccessary in order to harness its full power to install some more components to the host or remote system.

Essential packages are in order to run core functions of realtimemachine:

  * `numpy` (pipy)
  * `pandas` (pipy)
  * `itertools` (pipy)
  * `sklearnext` (github.com/mzoll)

In order to set up and integrate a permanent storage of historical states, which is needed for rapid training from historical data, a responsive SQL-like database instance is required which need to be able to reached with the according python interface for data insert and retrieval operations. For this for example a `ODBC` instance can be used to nagotiate the server-side protocol and transmit request via the `pyodbc` interface.  


Data flow model
---------------
Let's have a look at the data flow model: a new data-point, for example a click,  marks a new `Incident`, convoluted with a stale 'State' into a new _updated_ `State`, which will be convoluted by some lightweight transformations into a `Prime`, which is scored by one or multiple Models into a `Result`.

The objects `Request` and `Response` are transport objects that wrap the outside communication from an higher, outside control instance with the front and the end of the processing machine.  

   Incident >> State >> Prime >> Result


Input data
..........

Your data needs to be representable in some sort of time-progressive stream. As it is a very intuitive example and so covers most of the applications, let's assume a clickstream: Every new click of an *User* would generates a new datapoint, which would need to contain some fields for its unique identification like `UserId` and `TimeStamp`. Furthermore it should contain some rich information about the click-event itself, for example which URL was navigated, what actions have been executed on the website, which device, user-agent/browser or IP-address has been used etc. 


Incident
.......

An `Incident` is a collection of information valid at this precise point of time, a single data-point in a time-series. The time-ordered stream of Incidents therefore represent the flow of information as it is observed and recorded.    

Like all other objects in the `tslearn` data-flow, it has 4 primary header-fields: `uid`, `targetid`, `timestamp`, and `routingkey`. The `targetid` will help us trace the states of a specific user as the propagate through the machinery. The `uid` will be a unique identifier of each data-point as it flows through the machine, the `timestamp` helps to maintain time-order and the `routingkey` is used to rout a specific point of data to the correct channels within the complex rt-machine. Moreover, the header contains a field `meta` at which all kinds of meta-information can be stored in the form of a dictionary. The central field, which will contain all transported payload-information is called 'data'. For the click-stream example, an `Incident` could look like this

```
	Request(
		targetid= 'ABCD',  	# the UserId
		uid = 12345, 		#an incremental Index
		timestamp = '2018-06-01T12:12:01', 	#the timespam
		routinkey = 0, 	#some routing information
		meta = {'someMetaInfo' : "whateverobject"},
		data = {
			url = "http://www.abc.com/sub1/sub2/page.html",
			time = '2018-06-01T12:00:00'
			actions = ['view_page', 'scroll', 'click_botton'],
			ip = '128.1.1.0',
			useragent = 'Mozilla Like 12.2',
			device = 'mobile'
		}
	)
```


State
.....
A `State` object expresses the state that a certain entity has acquired at certain point of time having experienced several _incidents_. It can be understood as the accumulation of information of all previous incidents. A state is therefore deterministically given by the series of all previous `Incidents`. However, it is not instructive to keep all information around, but rather _remember_ only useful information in a possibly convoluted format. This can be done by incrementally augmenting a persistent state with the information issued in each incident.

For our clickstream example this could for example, for example, the time of the first click encountered, the first referer of a session or the history of all clicked urls during a session. 

This process of convoluting information and updating a `State` is called _state-building_ and is performed by a set of `StateBuilder`s, each with a specific set of in and out keys. A routine, which reads the url from the incident-data and appends it to a _url-history_ list stored in the `State` could be one of such StateBuilder.

When thinking about it, it will become obvious that such incremental states will only hold information, which can be sorted into five temporal categories:

	* 'now' : all information which has validity only during the time the request has been issued and is immediately superseded when a new request with new information is sent
	* 'session' : all information that has validity only during a session or sitting; when a new session starts this information is void and will be superseded too
	* 'total' : information that is valid for all times, which will never be superseded but may be updated (mutable)
	* 'perm' : information that is valid for all times, which will never be superseded and never will be updated (immutable)
	* 'prev' : (short for previous) information that has been superseded, but is good to keep around; functions like a one step memory (Markov-memory)
	
These fields can be accessed under ´State.data´ as dictionaries, to which new keys can be freely added or modified.

When building States it should be avoided to convolute away too much of the information. It is better to keep information in such format, that it can be exploited in possibly many, yet undetermined ways. So, for example when the  intent is to determine the time in session as the difference of time the session has started and the current time, it is better to store two fully qualified timestamps, one in _session_ and one in _now_ and calculate the time-difference on the fly than to calculate it at every update and store the value directly under _now_.      


Prime
.....

A `Prime` is a set of proto-features, which are extracted out of *one* state in the process of _prime-building_ by the so-called `PrimeBuilders`. Each PrimeBuilder accesses the information stored in `state.data` and either simply transports or convolutes it, storing the result in `Prime.data`. PrimeBuilders therefore provide a form of data reduction and preparation to proto-features which can be easier digested in subsequent processing, facilitating some processing work, which otherwise would have to be executed multiple times.

The simplest set of PrimeBuilders would be a single PrimeBuilder, which just takes all keys from the `State.data` and writes them one-to-one to the `Prime.data`. A more tailored set of PrimeBuilders, however, would fulfill different tasks specifically. So for the clickstream example, one PrimeBuilder construct the _TimeInSession_-feature by taking the difference of `state.data.now['Time']` and `state.data.session['StartTime']`, while a different PrimeBuilder might want to track the current hour of the day by extracting it from the  `state.data.now['Time']`-field, and a third one might just transport the information of `state.data.perm['Device']` which carries valuable information without any further convolution.

PrimeBuilding is an intermediate step, which has been placed here to allow the information stored in the States to remain genuine in a very basic format, while simply adding new specialized PrimeBuilders can lead to large variety of derivative proto-features. The power of this should not underestimated when it comes to building deep model structures with many parallel submodels, which in themselves are very shifty, but use many common proto-features. 


ScorerModel
......

A `Scorer` is, in essence, an entity that takes a set of (proto-)features and returns, after internal processing, a small number of score-values. A most basic `Scorer` might just hold a simple estimator or `predictor`, which takes the plain values of the input features and outputs a derivative prediction. There are no limits to the internal complexity of each Scorer, and it is really here that the power of packages like `sklearn` and `sklearnext` should be used to efficiently process and score the data. 

To better keep track of different Scorers and the state of their internally learned parameters, a Scorer is enclosed in a `ScorerModel` which provides the interface to the `realtimemachine` processing pipeline. The ScorerModel provides various fields where the name, id, training-date, and current training state of the Model can be tracked. The method `score()` allows to directly pass a Prime to Model and receive the scoring result in the form of a `Result` object.

We will return to the discussion of Models later.


Result
......

A `Result` holds all produced scores in his `data`-field. It is a simply put just a collection object that concludes the linear processing chain of the ´realtimemachine´.


Data duality
............

While until now it was argued that all mentioned objects are insulations of single data-points, we can break up this definition and allow for the representations of many incidents, states, primes, results in DataFrames by alignment of their contents. This is especially of great value when a model needs to be trained or evaluated on bigger datasets. Here the processing of complete data-structures proves to be much faster and then running the pipeline for each data-row individually.



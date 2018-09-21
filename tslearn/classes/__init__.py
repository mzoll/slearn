""" Classes for the RealTimeMachine
The hierarchical structure while processing is :
Request -> Incident -> State -> Prime -> Result -> Response

A Incident holds information that is only current for one specific step in time
A State is a sequentially build by itself stateless object, that encodes the current and all previously received Requests
A Prime is a partial aspect of a State with no or minimal convolution of information
A Result is some kind of modelfuled derivative of Prime, holding a result dictionary
A Resoponse is then the packed up information of the Result

All objects follow the basic interface of having the parameters/attributes

    * uid : obj
        a global unique identifier tracing a Request and concurrent objects through the processing chain
    * targetid : obj 
        an (unique) identifier of an entity for which Requests are generated
    * timestamp : obj
        timestamp for sequence order
    * routingkey : obj
        a key to rout this object through the machinery to the appropriate places
    * meta : dict
        other meta-information on this object
        
best practices are

    * use some sort of hash-value for the _targetid_ for fast, cheap identity checks
    * with incremental time an incremental int as _uid_
    * a datetime.datetime object for _timestamp_ foe easy and ms-precise handling
    * a integer number for routing key, as it works easiest with many other interfaces

"""

from .incident import Incident
from .state import State
from .prime import Prime
from .result import Result

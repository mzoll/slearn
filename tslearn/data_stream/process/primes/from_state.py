'''
Created on Aug 27, 2018

@author: marcel.zoll
'''

from realtimemachine.classes import Incident, State, Prime, Result
from realtimemachine.state_building.constructor import StateConstructor
from realtimemachine.prime_building.constructor import PrimeConstructor

from realtimemachine.state_building.session import SessionTrigger

import copy


class ModelProcessor(object):
    """ holds a mass of ModelProcessors, one for each routing key;
    can _process_ an _Incident_ by the appropriate _Model_, returning a result.

    Parameters
    ----------
    modelcollection : ModelCollection
        A model collection
    sessionTrigger : callable or None
        a callable by the signature  `__call__(incident, oldstate) -> bool` signaling when a new session has started.
        This can for example be handled by a flag in the data or a delta in meta-fields. if None is specified,
        this object will be replaced by a False-returning function, effectively never starting a new session (default: None)
    statecachehandler : CacheHandler or None
        A cachehandler which retrieves and stores states, needed for incremental statebuilding (default: None)
    statestorehandler : StoreHandler or None
        A storehandler which stores states (default: None)
    resultstorehandler : StoreHandler or None
        A storehandler which stores results (default: None)
    """

    class _Processor(object):
        """ knows how to process a _incident_ by a model

        Parameters
        ----------
        model : Model obj
            the scorer model, supporting `score()`,`getStateBuilders()`,`getPrimeBuilders()`
        """

        def __init__(self,
                     stateBuilder_list,
                     sessionTrigger):
            sb_list = self.model.getStateBuilders()
            pb_list = self.model.getPrimeBuilders()
            self._stateconstructor = StateConstructor(sb_list, sessionTrigger)
            self._primeconstructor = PrimeConstructor(pb_list)

        def __call__(self, incident, oldState):
            """ passing in old, stale state and an incident holding new information,
            build the new state and the return the result by evaluation of the model
            """
            # -process the newState
            newState = self._stateconstructor(incident, oldState)
            newState.meta = incident.meta.copy()
            # -process newPrime
            prime = self._primeconstructor(newState)
            # -process newScore
            result = self.model.score(prime)
            return newState, result

    def __init__(self, modelcollection,
                 sessiontrigger=None,
                 statecachehandler=None,
                 statestorehandler=None,
                 resultstorehandler=None):
        self._modelcollection = modelcollection
        self._sessiontrigger = sessiontrigger
        self._statecachehandler = statecachehandler
        self._statestorehandler = statestorehandler
        self._resultstorehandler = resultstorehandler

        if self._sessiontrigger is None:
            self._sessiontrigger = SessionTrigger()

        self._setup = False

    def process(self, incident):
        """ take an incident and take appropriate action according to its routing key:
        retrieve the appropriate stale state, update it by statebuilding,
        perform prime-building and scoring and push a response
        """
        routingkey = incident.routingkey
        targetid = incident.targetid

        # - retrive the old (stale) state from store
        if self._statestorehandler is not None:
            oldState = self._statecachehandler.fetch(routingkey, targetid)
        else:
            oldState = None

        newState, result = self.mp_register[int(routingkey)](incident, oldState)

        # -push the new state to the store and store
        if self._statecachehandler is not None:
            self._statecachehandler.insert(routingkey, targetid, newState)
        if self._statestorehandler is not None:
            self._statestorehandler.insert(routingkey, targetid, newState)

        # -push the new result to the store
        if self._resultstorehandler is not None:
            self._resultstorehandler.insert(routingkey, targetid, result)

        return result

    def setup(self):
        if self._setup:
            raise Exception("Component is already distributed and setup, cannot be setup again")
        self.mp_register = {rk: self._Processor(m, self._sessiontrigger) for rk, m in
                            self._modelcollection.rk_model_dict.items()}
        if self._statecachehandler is not None:
            self._statecachehandler.setup()
        if self._statestorehandler is not None:
            self._statestorehandler.setup()
        if self._resultstorehandler is not None:
            self._resultstorehandler.setup()
        self._setup = True
        return self

    def teardown(self):
        self.mp_register = {}
        if self._statecachehandler is not None:
            self._statecachehandler.teardown()
        if self._statestorehandler is not None:
            self._statestorehandler.teardown()
        self._setup = False
        return self

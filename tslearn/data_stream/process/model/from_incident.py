"""
Created on Jan 30, 2019

@author: marcel.zoll
"""

from tslearn.state_building.constructor import StateConstructor
from tslearn.prime_building.constructor import PrimeConstructor

from tslearn.state_building.session import SessionTrigger

import copy

ROUTING_KEY = 0


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
    """

    class _Processor(object):
        """ knows how to process a _incident_ by a model

        Parameters
        ----------
        model : Model obj
            the scorer model, supporting `score()`,`getStateBuilders()`,`getPrimeBuilders()`
        """

        def __init__(self,
                     model,
                     sessionTrigger):
            self.model = model
            self.model.prepare()

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

    def __init__(self, model,
                 sessiontrigger=None,
                 statecachehandler=None):
        self._model = model
        self._sessiontrigger = sessiontrigger
        self._statecachehandler = statecachehandler

        if self._sessiontrigger is None:
            self._sessiontrigger = SessionTrigger()

        self._setup = False

    def process(self, incident):
        """ take an incident and take appropriate action according to its routing key:
        retrieve the appropriate stale state, update it by statebuilding,
        perform prime-building and scoring and push a response
        """
        targetid = incident.targetid

        # - retrive the old (stale) state from store
        if self._statestorehandler is not None:
            oldState = self._statecachehandler.fetch(ROUTING_KEY, targetid)
        else:
            oldState = None

        newState, result = self.mp(incident, oldState)

        # -push the new state to the store and store
        if self._statecachehandler is not None:
            self._statecachehandler.insert(ROUTING_KEY, targetid, newState)

        return result

    def setup(self):
        if self._setup:
            raise Exception("Component is already distributed and setup, cannot be setup again")
        self.mp = self._Processor(self._model, self._sessiontrigger)
        if self._statecachehandler is not None:
            self._statecachehandler.setup()
        self._setup = True
        return self

    def teardown(self):
        self.mp_register = {}
        if self._statecachehandler is not None:
            self._statecachehandler.teardown()
        self._setup = False
        return self

    def __copy__(self):
        if self._setup:
            raise Exception("Component is already distributed and setup, cannot be copied anymore")

        return ModelProcessor(
            copy.copy(self._modelcollection),
            copy.copy(self._statecachehandler),

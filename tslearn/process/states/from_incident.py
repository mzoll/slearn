"""
Created on Jan 30, 2019

@author: marcel.zoll
"""

from tslearn.state_building.constructor import StateConstructor

from tslearn.state_building.session import SessionTrigger
ROUTING_KEY = 0


class IncidentProcessor(object):
    """ Processes an incident to a State

    Parameters
    ----------
    stateBuilder_list : list of StateBuilders
        the list of StateBuilders
    sessionTrigger : callable or None
        a callable by the signature  `__call__(incident, oldstate) -> bool` signaling when a new session has started.
        This can for example be handled by a flag in the data or a delta in meta-fields. if None is specified,
        this object will be replaced by a False-returning function, effectively never starting a new session (default: None)
    statecachehandler : CacheHandler or None
        A cachehandler which retrieves and stores states, needed for incremental statebuilding (default: None)
    """

    def __init__(self,
                 stateBuilder_list,
                 sessionTrigger=None,
                 statecachehandler=None):
        self._statecachehandler = statecachehandler

        if sessionTrigger is None:
            sessionTrigger = SessionTrigger()

        self._stateconstructor = StateConstructor(stateBuilder_list, sessionTrigger)

        self._setup = False

    def process(self, incident):
        """ take an incident and comstruct from it the new state by querying the cache

        :param incident: Incident
            incoming Incident with new information

        :returns newState: State
            the state that has been augmented with info from the incident
        """
        targetid = incident.targetid

        # - retrive the old (stale) state from store
        if self._statecachehandler is not None:
            oldState = self._statecachehandler.fetch(ROUTING_KEY, targetid)
        else:
            oldState = None

        newState = self._stateconstructor(incident, oldState)
        newState.meta = incident.meta.copy()

        # -push the new state to the store and store
        if self._statecachehandler is not None:
            self._statecachehandler.insert(ROUTING_KEY, targetid, newState)

        return newState

    def setup(self):
        if self._setup:
            raise Exception("Component is already distributed and setup, cannot be setup again")
        if self._statecachehandler is not None:
            self._statecachehandler.setup()
        self._setup = True
        return self

    def teardown(self):
        if self._statecachehandler is not None:
            self._statecachehandler.teardown()
        self._setup = False
        return self

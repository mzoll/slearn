"""
Created on Sep 25, 2017

@author: marcel.zoll

Sequentially construct the State from sequential raw input
"""

from tslearn.classes import Incident, State
from tslearn.state_building.classes import StateBuilder
import datetime as dt

from tslearn.state_building.session import SessionTrigger


class StateConstructor():
    """ Constructs the State by altering the stale State into a new updated State by application of StateBuilders.
    A SessionTrigger, which evaluates the content of a new _Request_ and the stale State, provides the start points of a _new Session_
    
    Parameters
    ----------
    stateBuilder_list : list of StateBuilders
        a list of StateBuilders, each of which will be (conditionally) executed based on their Mixin-subclass 
        in order to build a new State from a stale State
    sessionTrigger : SessionTrigger inst
        specifies when a new Session starts; the default *never* starts a new session
    """

    def __init__(self,
                 stateBuilder_list,
                 sessionTrigger=SessionTrigger()):
        self.stateBuilder_list = stateBuilder_list
        self.sessionTrigger = sessionTrigger
        # --- strip and categorize prelist functions---------
        self.onceSB = []
        self.sessionSB = []
        self.everySB = []
        for sb in self.stateBuilder_list:
            if sb._exec_trigger == StateBuilder.ExecTrigger.once:
                self.onceSB.append(sb)
            elif sb._exec_trigger == StateBuilder.ExecTrigger.session:
                self.sessionSB.append(sb)
            elif sb._exec_trigger == StateBuilder.ExecTrigger.every:
                self.everySB.append(sb)

    def __call__(self, incident, oldstate, reset=False, newSession=False):
        """ Copy and update the _oldstate_ into a _new State_, by the information provided by the _request_  
        
        Parameters
        ----------
        incident : Incient inst
            the Incident with new information to build states from.
        oldState : State inst
            the stale state connected to the request, where targetid must be equal. Specifying None here will be euqal to reset=True
        reset : bool
            flag that all state information should be reset, as if this `targetid` would have been encountered 
            for the first time and no previous information would exist.  
        newSession : bool
            flag if this starts a new session has started. All information at the 'session' field will thereby reset
            
        Returns
        -------
        State : the altered State object  
        """
        if oldstate is None:
            reset = True
            newSession = True
            oldstate = State(None, incident.targetid, None)
        else:
            newSession = newSession or self.sessionTrigger(incident, oldstate)

        # NOTE asserts disabled for speed
        # assert( oldstate.targetid == request.targetid)
        # assert( oldstate.routingkey == request.routingkey)

        # cleanup State if special conditions apply
        if reset:
            newstate = State(incident.uid, incident.targetid, dt.datetime.now())
        elif newSession:
            newstate = oldstate.copy()
            newstate.data.clear_session()
            newstate.data.clear_now()
            newstate.uid = incident.uid
            newstate.timestamp = dt.datetime.now()
        else:
            newstate = oldstate.copy()
            newstate.data.clear_now()
            newstate.uid = incident.uid
            newstate.timestamp = dt.datetime.now()

        # execute the according stateBuilders
        if reset:
            for sb in self.onceSB:
                sb(incident, oldstate, newstate, newSession=newSession, reset=reset)
        if newSession:
            for sb in self.sessionSB:
                sb(incident, oldstate, newstate, newSession=newSession, reset=reset)
        if True:
            for sb in self.everySB:
                sb(incident, oldstate, newstate, newSession=newSession, reset=reset)

        return newstate.copy()  # FIXME pretty sure we do not need the copy any longer here

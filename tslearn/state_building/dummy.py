'''
Created on Mar 1, 2018

@author: marcel.zoll

Fake the behaviour of a StateBuilder
'''

from realtimemachine.state_building.classes import StateBuilder, EveryMixin
import datetime as dt

from common_tools.helpers.value_retrieval import RetrieveValue

class DummyStateBuilder(StateBuilder, EveryMixin):
    """ 
    A dummy StateBuilder for internal testing and verifacation purposes.
    Just put out some fake keys so that it looks like as we have worked something 
    """
    def __init__(self):
        StateBuilder.__init__(self,
                name = 'DummyStateBuilder',
                dep = [],
                inkeys = [],
                outkeys = ['now__Time', 'session__Count', 'perm__AbsCount'])
    def __call__(self, incident, oldState, newState, newSession = False, reset = False):
        if reset:
            oldState.data.perm['AbsCount'] =0
        if reset or newSession:
            oldState.data.session['Count'] =0
        
        newState.data.now['Time'] = dt.datetime.now()
        newState.data.session['Count'] = RetrieveValue(oldState.data.session, 'Count', 0)+1
        newState.data.perm['AbsCount'] = RetrieveValue(oldState.data.perm, 'AbsCount', 0)+1

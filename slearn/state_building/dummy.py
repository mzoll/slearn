'''
Created on Mar 1, 2018

@author: marcel.zoll

Fake the behaviour of a StateBuilder
'''

import datetime as dt
from ..state_building.classes import StateBuilder

from slearn.externals.common_tools.helpers.value_retrieval import RetrieveValue

class DummyStateBuilder(StateBuilder):
    """ 
    A dummy StateBuilder for internal testing and verification purposes.
    Just put out some fake keys so that it looks like as we have worked something 
    """
    inkeys = []  # in and outkeys can be shared between instances, its okay - I think ...
    outkeys = ['now__Time', 'session__Count', 'perm__AbsCount']
    def __init__(self):
        StateBuilder.__init__(self,
                name = 'DummyStateBuilder',
                dep = [],
                inkeys = [],
                outkeys = ['now__Time', 'session__Count', 'perm__AbsCount'],
                exec_trigger=StateBuilder.ExecTrigger.every)
    def __call__(self, incident, oldState, newState, newSession = False, reset = False):
        if reset:
            oldState.data.perm['AbsCount'] =0
        if reset or newSession:
            oldState.data.session['Count'] =0
        
        newState.data.now['Time'] = dt.datetime.now()
        newState.data.session['Count'] = RetrieveValue(oldState.data.session, 'Count', 0)+1
        newState.data.perm['AbsCount'] = RetrieveValue(oldState.data.perm, 'AbsCount', 0)+1

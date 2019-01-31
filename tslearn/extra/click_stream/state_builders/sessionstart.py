
from tsstate_building.classes import StateBuilder, EveryMixin, SessionMixin, OnceMixin

class SessionStartTimeStateBuilder(SessionMixin, StateBuilder):
    """ just remember the start Time of this session """
    def __init__(self):
        StateBuilder.__init__(self,
                name = "SessionStartTimeStateBuilder",
                dep = [],
                inkeys = ['LogTime'],
                outkeys = ['session__SessionStartTime'])
    def __call__(self, newInput, oldState, newState, newSession = False, reset = False):
        if reset or newSession:
            if 'SessionStartTime' in oldState.data.session:
                newState.data.prev['SessionStartTime'] = oldState.data.session['SessionStartTime']
            starttime = RetrieveValue(newInput, 'LogTime', None, 'datetime')
            newState.data.session['SessionStartTime'] = starttime

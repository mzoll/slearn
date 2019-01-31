from tslearn.state_building.classes import StateBuilder, EveryMixin, SessionMixin, OnceMixin

class LogTimeStateBuilder(EveryMixin, StateBuilder):
    """simply write the time as the current time """
    def __init__(self):
        StateBuilder.__init__(self,
            name = 'LogTimeStateBuilder',
            dep = [],
            inkeys = ['Time'],
            outkeys = ['now__Time'])
    def __call__(self, newInput, oldState, newState, newSession = False, reset = False):
        currenttime = RetrieveValue(newInput, 'Time', None, 'datetime')
        newState.data.now['Time'] = currenttime

from tslearn.state_building.classes import StateBuilder, EveryMixin, SessionMixin, OnceMixin

class PageStateBuilder(EveryMixin, StateBuilder):
    """ The current Page with Content

    take the url and strip it down to the domain/path part ; act only on ALL logtypes """

    def __init__(self):
        StateBuilder.__init__(self,
                              name='PageStateBuilder',
                              dep=[],
                              inkeys=['URL'],
                              outkeys=['now__Page'])

    def __call__(self, newInput, oldState, newState, newSession=False, reset=False):
        url = RetrieveValue(newInput, 'URL', '', 'str')
        try:
            page = strip_decay_url(url)
        except:
            page = ''
        newState.data.now['Page'] = page

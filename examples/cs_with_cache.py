'''
Created on Jan 27, 2019

@author: marcel.zoll
'''

import unittest

from tslearn.extra.click_stream.clickstream_gen.clickstream_gen import ClickGenerator
from tslearn.extra.click_stream.clickstream_gen.sub_gens.url_gen import URLGenerator
from tslearn.extra.click_stream.clickstream_gen.sub_gens.agent_gen import UserAgentGenerator

from tslearn.data_stream.process.states.from_incident import IncidentProcessor
from tslearn.classes.incident import Incident

from tslearn.state_building.dummy import DummyStateBuilder


def testClickStreamSampleGen():

    # --- generate a fake click-stream
    N_CLICKS_TOTAL = int(1E+4)

    TIME_DECAY_MEAN_SEC = 30
    CLICK_DECAY_MEAN = 10

    MEAN_CONCUR_USERS = 200

    NUM_PATH0_LEVELS = 8
    MIN_NUM_DOC_LEVELS = 1
    MAX_NUM_DOC_LEVELS = 10

    url_gen = URLGenerator(NUM_PATH0_LEVELS, MIN_NUM_DOC_LEVELS, MAX_NUM_DOC_LEVELS)
    ua_gen = UserAgentGenerator()

    g = ClickGenerator(MEAN_CONCUR_USERS, CLICK_DECAY_MEAN, TIME_DECAY_MEAN_SEC, [url_gen, ua_gen])

    clicks = []
    for i in range(N_CLICKS_TOTAL):
        clicks.append(g.next())

    print(len(clicks))


    # --- convert clicks to incidents

    def incidentConstructor(uid, click):
        d = click.data.copy()
        d.update({'TimeStamp': click.ts})
        return Incident(
                uid = uid,
                targetid = click.uid,
                timestamp = click.ts,
                meta={'origin': 'fakeClickGenerator'},
                data=d)

    incidents = []
    for uid, c in enumerate(clicks):
        incidents.append(incidentConstructor(uid, c))

    def sessionTrigger(*args, **kwargs):
        return False


    # --- prepare for processing
    from tslearn.externals.common_tools.localcache.managed import ManagedCache_Master
    cache = ManagedCache_Master()

    stateBuilder_list = [DummyStateBuilder()]

    ip = IncidentProcessor(stateBuilder_list, sessionTrigger, cache)
    ip.setup()

    states = []
    for i in incidents:
        states.append( ip.process(i) )

    ip.teardown()

    print( len(states) )


if __name__ == "__main__":
    testClickStreamSampleGen()


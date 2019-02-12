#!/usr/bin/env python

"""
Created on Jan 27, 2019

@author: marcel.zoll
"""

from webclickgen import WebClickStreamGen
from tslearn.process.states.from_incident import IncidentProcessor
from tslearn.classes.incident import Incident

from tslearn.state_building.dummy import DummyStateBuilder


N_CLICKS_TOTAL = int(1E+4)

def testClickStreamSampleGen():

    g = WebClickStreamGen()
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


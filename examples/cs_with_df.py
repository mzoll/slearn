#!/usr/bin/env python

"""
Created on Jan 27, 2019

@author: marcel.zoll
"""

import pandas as pd
from slearn.data_pack.dspack import DataStreamPack
from slearn.process.build_states.from_ipack import process
from slearn.state_building.dummy import DummyStateBuilder
from slearn.classes import Incident
from webclickgen import WebClickStreamGen


N_CLICKS_TOTAL = int(1E+4)

def testClickStreamSampleGen():

    g = WebClickStreamGen()
    clicks = []
    for i in range(N_CLICKS_TOTAL):
        clicks.append(g.next())

    print(len(clicks))

    # --- convert clicks to dataframe and eventually DataStreamPack
    df = pd.DataFrame()

    for c in clicks:
        cdict = c.data.copy()
        cdict.update({"UserId": c.userid, "TimeStamp": c.ts})
        df = df.append(cdict, ignore_index=True)

    dsp = DataStreamPack(
        data=df,
        startTime=min(df['TimeStamp']),
        endTime=max(df['TimeStamp']),
        meta={"Fake": True}
    )

    # --- prep for process

    def incidentConstructor(uid, click_row):
        d = click_row.to_dict()
        uid = d.pop('UserId')

        return Incident(
                uid = uid,
                targetid = uid,
                timestamp = click_row['TimeStamp'],
                meta={'origin': 'fakeClickGenerator'},
                data=d)

    def sessionTrigger(*args, **kwargs):
        return False

    targetid_column = 'UserId'

    stateBuilder_list = [DummyStateBuilder()]

    # --- execute the process

    states_df = process(dsp,
                        incidentConstructor,
                        sessionTrigger,
                        stateBuilder_list,
                        targetid_column,
                        nthreads=1,
                        maxbatchsize=10000)

    print( len(states_df) )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    testClickStreamSampleGen()


"""
Created on Jan 27, 2019

@author: marcel.zoll
"""

import pandas as pd
import datetime as dt

from tslearn.extra.click_stream.clickstream_gen.clickstream_gen import ClickGenerator
from tslearn.extra.click_stream.clickstream_gen.sub_gens.url_gen import URLGenerator
from tslearn.extra.click_stream.clickstream_gen.sub_gens.agent_gen import UserAgentGenerator
from tslearn.data_stream.pack import DataStreamPack
from tslearn.data_stream.process.states.from_dsp import playback
from tslearn.state_building.dummy import DummyStateBuilder
from tslearn.classes import Incident

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

    # --- convert clicks to dataframe and eventually DataStreamPack
    df = pd.DataFrame()

    for c in clicks:
        cdict = c.data.copy()
        cdict.update({"UserId": c.uid, "TimeStamp": c.ts})
        df = df.append(cdict, ignore_index=True)

    print(df.columns)
    print(df.shape)

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

    states_df = playback(dsp,
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


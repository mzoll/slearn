"""
Created on Jan 27, 2019

@author: marcel.zoll
"""

import unittest

from tslearn.extras.clickstream_gen.clickstream_gen import ClickGenerator
from tslearn.extras.clickstream_gen.sub_gens.url_gen import URLGenerator
from tslearn.extras.click_stream.clickstream_gen.sub_gens.agent_gen import UserAgentGenerator

from tslearn.data_stream.pack import DataStreamPack
import pandas as pd

from tslearn.data_stream.playback.states.from_dsp import playback


def testClickStreamSampleGen(self):

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
        if i % 50 == 0:
            print(len(g._active_users))

    print(len(clicks))

    # --- convert clicks to dataframe and eventually DataStreamPack
    df = pd.DataFrame()

    for c in clicks:
        df.append(pd.Series({"UserID": c.uid, "TimeStamp": c.ts}.update(c.data)))

    dsp = DataStreamPack(
        routingkey = 0,
        data=df,
        startTime=min(df['TimeStamp']),
        endTime=max(df['TimeStamp']),
        meta = {"Fake": True}
    )

    # --- prep for playback

    def incidentConstructor(uid, click):
        return Incident(
                uid = uid,
                targetid = click.uid,
                timestamp = click.ts,
                meta={'origin': 'fakeClickGenerator'},
                data=click.data)

    def sessionTrigger(*args, **kwargs):
        return False

    targetid_column = 'UserId'

    stateBuilder_list = []

    # --- execute the playback

    states_df = playback(dsp,
                         incidentConstructor,
                         sessionTrigger,
                         stateBuilder_list,
                         targetid_column,
                         nthreads=-1,
                         maxbatchsize=10000)

    print( len(states_df) )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


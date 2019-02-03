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

from tslearn.sklearnext.assembly import TransformerPipe, FeatureUnion
from sklearnext.transformers.assembled.timestamp import TimestampTransformer
from sklearnext.transformers.label import OneHotTransformer
from sklearnext.transformers.cyclic import CyclicSinCosTransformer





def assemblePipeline():
    # assemble the pipeline by bits an pieces

    # OneHot/Label encoding for feature 'Label'
    tf0 = TransformerPipe([
        ('devicebuilder', StateBuilderTransport([DeviceStateBuilder()])),
        ('labelEnc', OneHotTransformer())
    ])

    # Extraction of Hour and Day-of-Month fromfeature  'Time'
    tf1 = TransformerPipe([
        ('startTimeBuilder', StateBuilderTransPort([NowtimeStateBuilder()])),
        ('timestamp', TimestampTransformer())
    ])

    tf2 = TransformerPipe([
        ('sessionDurationBuilder', StateBuilderTransPort([SessiondurationStateBuilder()])),
    ])

    tf3 = TransformerPipe([
        ('sessionLengthBuilder', StateBuilderTransPort([SessiondurationStateBuilder()])),
    ])


    # assemble a set of to use features
    fu = FeatureUnion([
        ('tf0', tf0),
        ('tf1', tf1),
        ('tf2', tf2),
        ('tf3', tf3),
        ('tf2', ColumnsSelect('Cont'))  # feature 'Cont' could have been wrapped into its own pipeline,
        # but no need to convolute as already in correct format
    ], n_jobs=1)

    # define a Classifier estimator; here one that is smarter as the average by growing additional trees
    skl_c0 = GrowingGBClassifier(ntrees_start=100,
                                 ntress_increment=10,
                                 est_params={'max_depth': 3,
                                             'max_features': None},  # auto
                                 scoring='log_loss',  # binary_roc_auc
                                 min_score_improvement=1e-5,
                                 nrounds_noimp=2,
                                 nrounds_stop=sys.maxsize,
                                 cv_test_frac=0.2,
                                 cv_n_splits=3)

    # as we are interested in the probabilities rather than the absolute binary classification use this shim
    skl_cc0 = OneProbClassifierWrapper(skl_c0, predictClass=1)

    # as OneProbClassifier (and GrowingGBClassifier) are using the sklearn interface, make them sklearnext compatible
    cc0 = SKLEstimatorExtender(skl_cc0)

    # this is a complete pipeline, which uses all features except 'Device'
    pred_pipe = Pipeline([
        ("fu", fu),
        ("cc0", cc0)
    ])

    # make a categorical fork for the feature Device, which has two levels
    cf = CategoryFork(pred_pipe,
                      'Device',
                      [('A'), ('B')],
                      n_jobs=1)

    # define this by an alias
    return cf


def gen_click_stream_sample(
    N_CLICKS_TOTAL = 10000,
    TIME_DECAY_MEAN_SEC = 30,
    CLICK_DECAY_MEAN = 10,
    MEAN_CONCUR_USERS = 200,
    NUM_PATH0_LEVELS = 8,
    MIN_NUM_DOC_LEVELS = 1,
    MAX_NUM_DOC_LEVELS = 10,
    ):
    # --- generate a fake click-stream
    url_gen = URLGenerator(NUM_PATH0_LEVELS, MIN_NUM_DOC_LEVELS, MAX_NUM_DOC_LEVELS)
    ua_gen = UserAgentGenerator()

    g = ClickGenerator(MEAN_CONCUR_USERS, CLICK_DECAY_MEAN, TIME_DECAY_MEAN_SEC, [url_gen, ua_gen])

    clicks = []
    for i in range(N_CLICKS_TOTAL):
        clicks.append(g.next())

    return clicks

def main():
    clicks = gen_click_stream_sample()
    print(len(clicks))

    # --- convert clicks to dataframe and eventually DataStreamPack
    df = pd.DataFrame()

    for c in clicks:
        cdict = c.data.copy()
        cdict.update({"UserId": c.uid, "TimeStamp": c.ts})
        df = df.append(cdict, ignore_index=True)

    df.sort_values('TimeStamp', ascending=True, inplace=True)

    # construct some to be guessed labels
    def mark_last(s):
        s2 = pd.Series(0, index=s.index)
        s2.iloc[-1] = 1
        return s2

    target_labels = df.groupby(['UserId'])['TimeStamp'].apply(mark_last)

    dsp = DataStreamPack(
        data=df,
        startTime=min(df['TimeStamp']),
        endTime=max(df['TimeStamp']),
        meta={"Fake": True}
    )


    # --- build a pipeline that has some guessing power
    pipe = build_pipe()

    stateBuilder_list = pipe.getStateBuilders()


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
    main()


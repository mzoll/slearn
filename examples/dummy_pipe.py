#!/usr/bin/env python

"""
Created on Jan 27, 2019

@author: marcel.zoll
"""

import pandas as pd
import datetime as dt
import uuid

from tslearn.data_stream.pack import DataStreamPack
from tslearn.process.states.from_dsp import playback
from tslearn.state_building.dummy import DummyStateBuilder
from tslearn.classes import Incident

from tslearn.sklearnext.assembly import TransformerPipe, FeatureUnion
from tslearn.sklearnext.transport import StateBuilderTransPort
from tslearn.sklearnext.assembly import ColumnsSelect

from sklearn.preprocessing import MinMaxScaler
from sklearnext.transformers.wrappers import SKLTransformerWrapper

from sklearnext.transformers.assembled.timestamp import TimestampTransformer



def assemblePipeline():
    # assemble the pipeline by bits an pieces

    # OneHot/Label encoding for feature 'Label'
    tf0 = TransformerPipe([
        ('devicebuilder', StateBuilderTransPort([DummyStateBuilder])),
        # produces the fileds:
        #   'now__Time' (a time-like feature),
        #   'session__Count' (a linear feature),
        #   'perm__AbsCount' (a linear feature)
        ('fu', FeatureUnion([
            ('tp0', TransformerPipe([
                ('cs', ColumnsSelect('now__Time')),
                ('trans', TimestampTransformer('now__Time'))
            ])),
            ('tp1', TransformerPipe([
                ('cs', ColumnsSelect('session__Count')),
                ('minmax', SKLTransformerWrapper(MinMaxScaler()))
            ])),
            ('tp2', TransformerPipe([
                ('cs', ColumnsSelect('perm__AbsCount')),
                ('minmax', SKLTransformerWrapper(MinMaxScaler()))
            ])),
        ])),
    ])

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

    # this is a complete pipeline
    pred_pipe = Pipeline([
        ("fu", fu),
        ("cc0", cc0)
    ])

    return pred_pipe


def gen_incidents(nmany):
    uid = 1
    i_uuid = str(uuid.uuid4())
    incidents = []
    for _ in range(nmany):
        incidents.append( Incident(uid, i_uuid, dt.datetime.utcnow(), meta={}, data={}) )
        uid += 1
    return incidents


def convert_to_dsp(incs):
    df = pd.DataFrame()

    for c in incs:
        cdict = {"UserId": i.uid, "TimeStamp": i.timestamp}
        df = df.append(cdict, ignore_index=True)

    dsp = DataStreamPack(
        data=df,
        startTime=min(df['TimeStamp']),
        endTime=max(df['TimeStamp']),
        meta={"Fake": True}
    )

    return dsp


def main():
    incs = gen_incidents()

    # --- convert clicks to dataframe and eventually DataStreamPack
    dsp = convert_to_dsp(incs)

    # --- construct dummy prediction pipe
    pred_pipe = assemblePipeline()

    # --- execute the state-building process

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

    states_df = playback(dsp,
                         incidentConstructor,
                         sessionTrigger,
                         stateBuilder_list = pred_pipe.getStateBuilders(),
                         targetid_column = 'UserId',
                         nthreads=1,
                         maxbatchsize=10000)

    print( len(states_df) )

    # --- generate some fake prediction labels

    bin_labels = np.random.rand( len(states_df) ) < 0.2

    # --- feed this into pipeline's fit routine

    pred_pipe.fit(states_df, bin_labels)

    # --- make a prediction for the whole dataset

    pred = pred_pipe.predict(states_df)

    print(len(pred))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    main()


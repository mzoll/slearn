"""
Created on Aug 17, 2018

@author: marcel.zoll
"""

import unittest

import pandas as pd
import datetime as dt

from slearn.data_pack.dspack import DataStreamPack
from slearn.data_pack.process.states.from_dsp import constructStates

from slearn.state_building.dummy import DummyStateBuilder

from slearn.data_pack.click_stream.playback.incidents import dsprow_to_incident


class Test(unittest.TestCase):
    def testDSP(self):

        ltime_first = dt.datetime.now()
        ltime = []
        for i in range(8):
            ltime.append(ltime_first + dt.timedelta(seconds=i))

        df = pd.DataFrame({
            'UserKey': ['A', 'A', 'A', 'A', 'A', 'A', 'B', 'B'],
            'SessionKey': ['A0', 'A0', 'A0', 'A1', 'A1', 'A1', 'B0', 'B0'],
            'LogTime': ltime,
            'SomeData_0': [0, 1, 2, 3, 4, 5, 6, 7],
            'SomeData_1': list(reversed([0, 1, 2, 3, 4, 5, 6, 7])),
        }, index=list(range(42, 48)) + [72, 73])

        dsp = DataStreamPack(routingkey=1, startTime=ltime_first, endTime=ltime_first + dt.timedelta(seconds=8),
                             data=df, meta={})

        def mySessionTrig(incident, oldstate):
            ''' make a trigger that compares the sessionkey saved in the meta-information and triggers on a diff '''
            ind0 = None
            sk_old = oldstate.meta.get('SessionKey')
            if sk_old:
                ind0 = incident.meta.get('SessionKey') != sk_old
            return bool(ind0)

        def myIncidentConst(dsprow):
            ''' just wrap away the constants of the incident constructor '''
            return dsprow_to_incident(dsprow, 'UserKey', 'SessionKey', 'LogTime', routingkey=1)

        sb_list = [DummyStateBuilder()]
        states_df = constructStates(dsp, myIncidentConst, mySessionTrig, sb_list, 'UserKey', nthreads=1)

        """ pandas.DataFrame()
                            now__Time  perm__AbsCount  session__Count
        42 2018-08-20 11:05:16.371905             1.0             1.0
        43 2018-08-20 11:05:16.373899             2.0             2.0
        44 2018-08-20 11:05:16.375894             3.0             3.0
        45 2018-08-20 11:05:16.378904             4.0             1.0
        46 2018-08-20 11:05:16.380899             5.0             2.0
        47 2018-08-20 11:05:16.382875             6.0             3.0
        72 2018-08-20 11:05:16.384870             1.0             1.0
        73 2018-08-20 11:05:16.386865             2.0             2.0
        """


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

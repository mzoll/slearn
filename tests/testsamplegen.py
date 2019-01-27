'''
Created on Jan 27, 2019

@author: marcel.zoll
'''

import unittest

from tslearn.data_stream.click_stream.sample_gen.sample_gen import ClickGenerator
from tslearn.data_stream.click_stream.sample_gen.url_gen import URLGenerator
from tslearn.data_stream.click_stream.sample_gen.agent_gen import UserAgentGenerator


class Test(unittest.TestCase):
    def testClickStreamSampleGen(self):
        N_CLICKS_TOTAL = int(1E+4)

        TIME_DECAY_MEAN_SEC = 30
        CLICK_DECAY_MEAN = 10

        MEAN_CONCUR_USERS = 200

        num_path0_levels = 8
        MIN_NUM_DOC_LEVELS = 1
        MAX_NUM_DOC_LEVELS = 10

        url_gen = URLGenerator(num_path0_levels, MIN_NUM_DOC_LEVELS, MAX_NUM_DOC_LEVELS)
        ua_gen = UserAgentGenerator()

        g = ClickGenerator(MEAN_CONCUR_USERS, CLICK_DECAY_MEAN, TIME_DECAY_MEAN_SEC, [url_gen, ua_gen])

        clicks = []
        for i in range(N_CLICKS_TOTAL):
            clicks.append(g.next())
            if i % 50 == 0:
                print(len(g._active_users))

        print(len(clicks))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


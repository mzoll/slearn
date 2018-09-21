'''
Created on Feb 6, 2018

@author: marcel.zoll
'''

import pandas as pd
from tslearn.classes import Incident


def dsp_to_incidents(dsp, userkey_name, sessionkey_name, timestamp_name):
    incidents = []
    for uid,r in dsp.data.iterrows():
        incident = Incident(uid, r[userkey_name], r[timestamp_name], dsp.routingkey,
            meta = {'UserKey': r[userkey_name], 'SessionKey': r[sessionkey_name], 'Timestamp': r[timestamp_name]},
            data = r.to_dict())
        incidents.append(incident)
    return incidents


def dsprow_to_incident(dsprow, userkey_name, sessionkey_name, timestamp_name, routingkey=None):
    incident = Incident(dsprow.name, dsprow[userkey_name], dsprow[timestamp_name], routingkey,
        meta = {'UserKey': dsprow[userkey_name], 'SessionKey': dsprow[sessionkey_name], 'Timestamp': dsprow[timestamp_name]},
        data = dsprow.to_dict())
    return incident
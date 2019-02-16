"""
Created on Jan 30, 2019

@author: marcel.zoll

Sequentially construct the State from sequential raw input
"""

import math
import time
import pandas as pd
import numpy as np

import logging

from joblib import Parallel, delayed
from slearn.externals.common_tools.tools.groups import GenStrategicGroups
from slearn.externals.common_tools.parallelism import GetNCores

from slearn.classes import State, Incident
from slearn.state_building.constructor import StateConstructor

from slearn.data_pack.pack import StatePack, IncidentPack

logger = logging.getLogger('process')


class _ConstructStateCaller:
    """ caller class which knows how to process sequentially and is fed linewise from pbd.
    
    This component just validates and packs the correct incidents and stale states together and 
    let them be processed by the slearn::StateConstructor. In the end it extracts the data field
    from the returned State and returns a dateframe of these
    
    NOTE : this thing does not know anything about the inital stale state, so the first state
        for each new target-id is computed as if there is no history  
    
    Parameters
    ----------
    incidentConstructor : IncidentConstructor callable
        how to build linewise the Incident from the data presented in the dataframe 
    sessionTrigger : SessionTrigger obj
        on the content and diff between two incidents indicates when a new session starts
    stateBuilder_list : list of slearn.state_building.StateBuilder obj
        the StateBuilders that are applied on the incident data to build states
    """
    def __init__(self,
            sessionTrigger,
            stateBuilder_list):
        self.stateBuilder_list = stateBuilder_list
        #-----------------------------------
        self.stateConstructor = StateConstructor(stateBuilder_list, sessionTrigger)
        #---------- variables for the rolling state ---
        self._targetKey = ""
        self._staleState = State(None, "", None)
    def __call__(self, g, df):
        out_df = pd.DataFrame()
        df.index = g
        for gidx,row in df.iterrows():
            incident = Incident(None, gidx, None, data=row.as_dict())
            
            #cleanup State if special conditions apply
            reset = False
            newSession = False
            if incident.targetid != self._targetKey :
                self._targetKey = incident.targetid
                reset = True
                newSession = True
                self.staleState = None
            
            newState = self.stateConstructor( incident, self.staleState, reset, newSession )
            #make a simple copy of the meta information for now
            newState.meta = incident.meta.copy()
            
            out_df = out_df.append( pd.Series(newState.data.to_flatdict().copy()) )
            
            # the newly updated state becomes the stale state for the next iteration step
            self._staleState = newState
        
        return out_df
            

def process(incidentpack,
            sessionTrigger,
            stateBuilder_list,
            nthreads = -1,
            maxbatchsize = 10000):
    """ 
    Construct the state by reading a DataStreamPack line-wise and sequentially building the state for each line.
    Parallelism is available.

    This is an atomic and agnostic operation, so states are build by just the information from the statepack;
    no external resources are utilized
    
    Parameters
    ----------
    statepack : StatePack
        the packed up data to construct states for
    incidentConstructor : IncidentConstructor callable
        how to build linewise the Incident from the data presented in the dataframe
    sessionTrigger : SessionTrigger obj
        on the content and diff between two incidents indicates when a new session starts
    stateBuilder_list : list of slearn.state_building.StateBuilder obj
        the StateBuilders that are applied on the incident data to build states
    nthreads : int
        number of processing instances (default: -1)
    maxbatchsize : int >0
        Each processing instance will receive a batch of rows of equal size to process, the maximum batchsize can be
        limited (default: 10000)
    
    Returns
    -------
    statepack: StatePack of processed data
    """
    assert(isinstance(incidentpack, IncidentPack))

    header = incidentpack.header.copy()
    data = incidentpack.data.copy()
    meta = incidentpack.meta.copy()
    header.sort_values(['tid','uid'], inplace=True)
    data.reindex(header.index, inplace=True)
    meta.reindex(header.index, inplace=True)

    ncores = GetNCores(nthreads)

    startCallTime = time.perf_counter()
    
    if ncores == 1:
        outdata = _ConstructStateCaller(sessionTrigger, stateBuilder_list)(np.ones(len(data)), data)
    elif ncores > 1:
        nbatches = max(math.ceil(len(data)/maxbatchsize), ncores)
        g = GenStrategicGroups( header['tid'].values, nbatches )
        
        dfGrouped = data.groupby(g)
        func = _ConstructStateCaller(sessionTrigger, stateBuilder_list)
        outdata = pd.concat( Parallel(n_jobs=ncores)(delayed(func)(group) for _, group in dfGrouped) )
    else:
        raise ValueError("ncores is negative : ", ncores)

    exectime = time.perf_counter()-startCallTime
    logger.info("ConstructState took %d seconds for %d rows ( %f ms / row / CPU)" % (exectime, data.shape[0], exectime / data.shape[0] * ncores * 1E3))

    header.reindex(inplace=True)
    outdata.reindex(inplace=True)
    meta.reindex(inplace=True)
    header.sort_values('tid', inplace=True)
    outdata.reindex(header.index, inplace=True)
    meta.reindex(header.index, inplace=True)

    return StatePack(header, outdata, meta)

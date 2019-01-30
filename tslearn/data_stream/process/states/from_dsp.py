"""
Created on Jan 30, 2019

@author: marcel.zoll

Sequentially construct the State from sequential raw input
"""

import math
import time
import pandas as pd

import logging
logger = logging.getLogger('process')

from joblib import Parallel, delayed
from tslearn.externals.common_tools.tools.groups import GenStrategicGroups
from tslearn.externals.common_tools.parallelism import GetNCores

from tslearn.classes import State
from tslearn.state_building.constructor import StateConstructor


class _ConstructStateCaller:
    """ caller class which knows how to process sequentially and is fed linewise from pbd.
    
    This component just validates and packs the correct incidents and stale states together and 
    let them be processed by the tslearn::StateConstructor. In the end it extracts the data field
    from the returned State and returns a dateframe of these
    
    NOTE : this thing does not know anything about the inital stale state, so the first state
        for each new target-id is computed as if there is no history  
    
    Parameters
    ----------
    incidentConstructor : IncidentConstructor callable
        how to build linewise the Incident from the data presented in the dataframe 
    sessionTrigger : SessionTrigger obj
        on the content and diff between two incidents indicates when a new session starts
    stateBuilder_list : list of tslearn.state_building.StateBuilder obj
        the StateBuilders that are applied on the incident data to build states
    """
    def __init__(self,
            incidentConstructor,
            sessionTrigger,
            stateBuilder_list):
        self.incidentConstructor = incidentConstructor
        self.stateBuilder_list = stateBuilder_list
        #-----------------------------------
        self.stateConstructor = StateConstructor(stateBuilder_list, sessionTrigger)
        #---------- variables for the rolling state ---
        self.targetKey = ""
        self.staleState = State(None, "", None)
    def __call__(self, df):
        out_df = pd.DataFrame()
        
        for idx,row in df.iterrows():
            incident = self.incidentConstructor(row)
            
            #cleanup State if special conditions apply
            reset = False
            newSession = False
            if incident.targetid != self.targetKey :
                self.targetKey = incident.targetid
                reset = True
                newSession = True
                self.staleState = None
            
            newState = self.stateConstructor( incident, self.staleState, reset, newSession )
            #make a simple copy of the meta information for now
            newState.meta = incident.meta.copy()
            
            out_df = out_df.append( pd.Series(newState.data.to_flatdict().copy(), name=idx) )
            
            # the newly updated state becomes the stale state for the next iteration step
            self.staleState = newState
        
        return out_df
            

def playback(dsp,
        incidentConstructor,
        sessionTrigger,
        stateBuilder_list,
        targetid_column,
        nthreads = -1,
        maxbatchsize = 10000):
    """ 
    Construct the state by reading a DataStreamPack linewise and sequentially building the state for each line.
    Parallelism is available.
    
    Parameters
    ----------
    dsp : DataStreamPack
        the packed up data to construct states for
    incidentConstructor : IncidentConstructor callable
        how to build linewise the Incident from the data presented in the dataframe
    sessionTrigger : SessionTrigger obj
        on the content and diff between two incidents indicates when a new session starts
    stateBuilder_list : list of tslearn.state_building.StateBuilder obj
        the StateBuilders that are applied on the incident data to build states
    nthreads : int
        number of processing instances (default: -1)
    maxbatchsize : int >0
        Each processing instance will receive a batch of rows of equal size to process, the maximum batchsize can be limited (default: 10000)
    
    Returns
    -------
    indexed pandas.DataFrame containing the fields of the generated states as columns.
    """
    data = dsp.data
    data.sort_index(inplace=True)
    data.sort_values([targetid_column], inplace=True)

    ncores = GetNCores(nthreads)

    startCallTime = time.perf_counter()
    
    if ncores == 1:
        out = _ConstructStateCaller(incidentConstructor, sessionTrigger, stateBuilder_list)(data)
    elif ncores > 1:
        nbatches = max(math.ceil(len(data)/maxbatchsize), ncores)
        g = GenStrategicGroups( data[targetid_column].values, nbatches )
        
        dfGrouped = data.groupby(g)
        func = _ConstructStateCaller(incidentConstructor, sessionTrigger, stateBuilder_list)
        out = pd.concat( Parallel(n_jobs=ncores)(delayed(func)(group) for _, group in dfGrouped) )
    else:
        raise ValueError("ncores is negative : ", ncores)

    exectime = time.perf_counter()-startCallTime
    logger.info("ConstructState took %d seconds for %d rows ( %f ms / row / CPU)" % (exectime, data.shape[0], exectime / data.shape[0] * ncores * 1E3))
    return out

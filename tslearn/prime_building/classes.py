'''
Created on Oct 2, 2017

@author: marcel.zoll

Definitions for PrimeBuilders
'''

from ..classes import Prime, State
import pandas as pd

class PrimeBuilder():
    """ Convolutes data from a state into meta-features.
    
    This step is wedged in between statebuild and inner feature-extraction in order to provide the possibility to keep
    the State pretty general clean from deeply stacked transformations and still provide a place where to perform transformations
    to build meta-features, which are commonly build amongst models.
    """
    def __init__(self):
        self.name = ''
        self.sb_list = [] #list of stateBuilders
        self.inkeys = [] 
        self.outkeys = []
    def __call__(self, state, prime):
        """ convolute variables from states and write them to the prime
        
        Parameters
        ----------
        state : State
            the state holding the input varibales to be convoluted the PrimeBuilder
        prime : Prime 
            the Prime to which the result of the convolution will be written
        """
        invars = [state.data[k] for k in self.inkeys]
        prime.data.update( dict(zip(self.outkeys, self._inner_conv( *invars ))) )
    def dfapply(self, df):
        """ a function that applies the inner_conv on the rows of a dataframe """
        stack = []
        for idx,row in df.loc[:,self.inkeys].iterrows():
            stack.append(self._inner_conv( *row.values))
        return pd.DataFrame(data=stack, index= df.index, columns = self.outkeys)  
    def _inner_conv(self, *args):
        """ a to be overwritten function that is the inner convolution of the variables at self.inkeys passed in as ordered list for args
        Return iteratable structure, which will be mapped to the outkeys 
        """
        raise Exception("you need to overwrite the '_inner_conv' function in %s" % (str(self)))
        res = args[0] + args[1]
        return [res]
    def getStateBuilders(self):
        return self.sb_list

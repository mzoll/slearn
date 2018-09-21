'''
Created on Mar 23, 2018

@author: marcel.zoll
'''

from realtimemachine.prime_building.classes import PrimeBuilder

class StateBuilderTransPort(PrimeBuilder, object):
    """ A hobo PrimeBuilder that does nothing internally, just transport all the outkeys from the specified StateBuilders into the Prime
    
    Parameters
    ----------
    sb_list : list of StateBuilder
        a list with StateBuilder objects
    keys : list of str or None
        the keys which should be transported; a subset of the outkeys of the statebuilders (default: None)
    depsb_list : list of StateBuilders
        list of StateBuilders the stateBuilders in `sb_list` depend upon; these are just dragged along for cals to `getStateBuilders()`
    """
    def __init__(self, sb_list, keys=None, depsb_list=[]):
        self.sb_list = sb_list
        self.depsb_list = depsb_list
        self.inkeys = [ ok for sb in sb_list for ok in sb.outkeys ]
        if keys is None:
            self.outkeys = self.inkeys
        else:
            assert( isinstance(keys, list) ) #typecheck
            if len(sb_list):
                assert( set(keys).issubset(self.inkeys) ) #desired outkeys is subset of inkeys
            self.outkeys = keys
        self.name = '_'.join(['DUMMY']+self.outkeys)
    def __call__(self, state, prime):
        for ik in self.outkeys: 
            prime.data[ik] = state.data[ik]
    def _inner_conv(self, *invars):
        return invars
    def getStateBuilders(self):
        return self.sb_list + self.depsb_list

    
class PipeTransPort(PrimeBuilder, object):
    """ take a tslearn::Assembly::TransformerPipe and convolute things internally,
    the result of which is the ouput for the Prime 
    
    Handling this is a bit complicated as the inkeys and outkeys are in principle not determined until training
    
    Parameters
    ----------
    name : str
        every PrimeBuilder needs a unique name
    transpipe : TransformerPipe
        the transformer pipe
    """
    def __init__(self, name, transpipe):
        self.name = name
        self.transpipe = transpipe
        self.sb_list = self.transpipe.getStateBuilders()
        self.inkeys = [ik for sb in self.sb_list for ik in sb.inkeys]
        #self.outkeys is a late configured field
    def dfapply(self, df):
        df_ = self.transpipe.fit_transform(df)
        self.outkeys = self.transpipe.steps[-1][1].get_feature_names()
        return df_
    def __call__(self, state, prime):
        d = state.data.to_flatdict()
        prime.data.update( self.transpipe.transform_dict(d) )
        
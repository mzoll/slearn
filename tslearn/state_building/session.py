'''
Created on Jun 22, 2018

@author: marcel.zoll
'''

class SessionTrigger():
    """ compares Information in Request and _old State_ and decides if a _new Session_ should be signaled """
    def __call__(self, incident, oldstate):
        """ overwritable method ; specifies when a new session should be started
        
        Parameters
        ----------
        incident : Incident
            the Incident with new information
        oldstate : State
            the old (stale) State
        
        Returns
        -------
        bool : new session started
        """ 
        return False


class NewSessionFlagTrigger(SessionTrigger):
    """ just inspect the payload for a flag 'NewSession' an trigger then """
    #overwrite
    def __call__(self, incident, oldstate):
        return bool( incident.data.get('NewSession') )
            
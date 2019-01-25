
import numpy as np
import datetime as dt
import string
import uuid


if __name__=="__main__":


    DATE_START = dt.datetime.now()
    N_CLICKS_TOTAL = int(1E+4)


    TIME_DECAY_MEAN_SEC = 30

    MIN_NUM_CONCUR_USERS = 20
    MAX_NUM_CONCUR_USERS = 100
    #MIN_NUM_CLICKS = 1
    #MAX_NUM_CLICKS = 20

    CLICK_DECAY_MEAN = 10

    MIN_NUM_PATH0_LEVELS = 4
    MAX_NUM_PATH0_LEVELS = 8

    MIN_NUM_DOC_LEVELS = 1
    MAX_NUM_DOC_LEVELS = 10


    possible_path0_levels = [ ''.join(np.repeat(l, 3)) for l in string.ascii_lowercase ]
    possible_path1_levels = [ ''.join(np.random.choice( list(string.ascii_lowercase) , 3)) ]

    def gen_nidletter_words(nletters):
        """ return a lowercase word of nletters, where all letters are the same; ie 'kkk', 'aaaa' """
        return ''.join(np.repeat( np.random.choice( list(string.ascii_lowercase)), 3))

    def gen_nletter_word(nletters):
        """ return a lowercase word of nletters, randomly drawn from the alphabet; ie 'xhud' """
        return ''.join(np.random.choice( list(string.ascii_lowercase) , nletters))


    domain_structure_gendict = {'protocol': 'https', 'subdomain': 'www', 'host': 'hostname', 'topdomain': 'com', 'path0_levels': [], 'document_paths' : {}, 'document_ext': 'html'}

    urls = []

    num_path0_levels = np.random.choice(range(MIN_NUM_PATH0_LEVELS, MAX_NUM_PATH0_LEVELS), 1)
    domain_structure_gendict['path0_levels'] = np.random.choice(possible_path0_levels, num_path0_levels)

    for p0l in domain_structure_gendict['path0_levels']:
        num_path1_levels_this = np.random.choice(range(MIN_NUM_DOC_LEVELS, MAX_NUM_DOC_LEVELS), 1)
        for p1l in num_path1_levels_this:
            doc_name =  gen_nletter_word(3)
            domain_structure_gendict['document_paths'] = doc_name
            urls.append( domain_structure_gendict['protocol'] + '://' + domain_structure_gendict['subdomain'] + \
                               '.' + domain_structure_gendict['host'] + '.' + domain_structure_gendict['topdomain'] + \
                               '/' + gen_nletter_word(3) + '/' + doc_name + '.' + domain_structure_gendict['document_ext'] )


    active_users = []


    class User(object):
        def __init__(self, init_time, CLICK_DECAY_MEAN=10, TIME_DECAY_MEAN_SEC=30):
            self.CLICK_DECAY_MEAN = CLICK_DECAY_MEAN
            self.TIME_DECAY_MEAN_SEC = TIME_DECAY_MEAN_SEC
            self.uid = uuid.uuid4()
            self.init_time = init_time
            self.n_clicks_term = max(1, np.round(np.random.exponential(self.CLICK_DECAY_MEAN)))
            self.is_active = True

            self._init_props()

        def _init_props(self):
            self.n_clicks = 1
            self.current_url = np.random.choice(urls, 1)
            self.last_click_time = self.init_time
            self.next_click_time = self.last_click_time + dt.timedelta(seconds=np.random.exponential(self.TIME_DECAY_MEAN_SEC))

        def step(self):
            self.n_clicks += 1
            if self.n_clicks >= self.n_clicks_term:
                self.next_click_time = None
                self.is_active = False
                return
            self.current_url = np.random.choice(urls, 1)
            self.last_click_time = self.next_click_time
            self.next_click_time = self.last_click_time + dt.timedelta(seconds=np.random.exponential(self.TIME_DECAY_MEAN_SEC))



    for u in range(np.random.choice(range(MIN_NUM_CONCUR_USERS, MAX_NUM_CONCUR_USERS))):
        active_users.append( User(dt.datetime.now()) )


    clicks = []

    for click in range(N_CLICKS_TOTAL):
        if not len(active_users):
            break

        active_users = list(sorted(active_users, key= lambda u: u.next_click_time) )

        u = active_users.pop()
        u.step()

        clicks.append( { 'uid': u.uid, 'ts': u.last_click_time, 'url': u.current_url }  )
        if u.is_active:
            active_users.append(u)

    print(len(clicks))
    #------------------------------------------------------------
    samp = []
    for i in range(100):
        cur = 0
        while cur<np.random.exponential(10):
            cur+=1
        samp.append(cur)
    np.mean(samp)


    samp = []
    for i in range(100):
        n = np.random.exponential(10)
        samp.append(n)
    np.mean(samp)



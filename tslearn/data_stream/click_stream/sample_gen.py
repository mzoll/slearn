
import numpy as np
import datetime as dt
import string
import uuid
import math


class URLGenerator(object):
    class URLGen_child(object):
        def __init__(self, domain_structure_dict, land_main_prob, step_levelout_prob):
            self.domain_structure_dict = domain_structure_dict
            self.land_main_prob = land_main_prob
            self.step_levelout_prob = step_levelout_prob

        def init_props(self):
            # dice the inital url
            if np.random.rand() < self.land_main_prob:
                self._p0l = '.'
                self.url = self.domain_structure_dict['protocol'] + '://' + self.domain_structure_dict['subdomain'] + \
                           '.' + self.domain_structure_dict['host'] + '.' + self.domain_structure_dict['topdomain']
            else:
                self._p0l = np.random.choice(self.domain_structure_dict['path0_levels'])
                d = np.random.choice(self.domain_structure_dict['path0_document_tree'][self._p0l])
                self.url = self.domain_structure_dict['protocol'] + '://' + self.domain_structure_dict['subdomain'] + \
                                  '.' + self.domain_structure_dict['host'] + '.' + self.domain_structure_dict['topdomain'] + \
                                  '/' + self._p0l + '/' + d + '.' + self.domain_structure_dict[
                                      'document_ext']

        def step(self):
            if np.random.rand() < self.step_levelout_prob or self._p0l == '.':
                self._p0l = np.random.choice(self.domain_structure_dict['path0_levels'])
                d = np.random.choice(self.domain_structure_dict['path0_document_tree'][self._p0l])
                self.url = self.domain_structure_dict['protocol'] + '://' + self.domain_structure_dict['subdomain'] + \
                                '.' + self.domain_structure_dict['host'] + '.' + self.domain_structure_dict['topdomain'] + \
                                '/' + self._p0l + '/' + d + '.' + self.domain_structure_dict[
                                    'document_ext']
            else:
                d = np.random.choice(self.domain_structure_dict['path0_document_tree'][self._p0l])
                self.url = self.domain_structure_dict['protocol'] + '://' + self.domain_structure_dict['subdomain'] + \
                                '.' + self.domain_structure_dict['host'] + '.' + self.domain_structure_dict['topdomain'] + \
                                '/' + self._p0l + '/' + d + '.' + self.domain_structure_dict[
                                    'document_ext']

        def get_dict(self):
            return {'url': self.url}

    def __init__(self,  num_path0_levels=10, MIN_NUM_DOC_LEVELS=5, MAX_NUM_DOC_LEVELS=10):
        self.num_path0_levels = num_path0_levels
        self.MIN_NUM_DOC_LEVELS = MIN_NUM_DOC_LEVELS
        self.MAX_NUM_DOC_LEVELS = MAX_NUM_DOC_LEVELS

        self.domain_structure_gendict = {'protocol': 'https', 'subdomain': 'www', 'host': 'hostname', 'topdomain': 'com',
                                    'path0_levels': [], 'path0_document_tree': {}, 'document_ext': 'html'}
        self._urls = []

        for i in range(num_path0_levels):
            p0l = gen_nletter_word(3)
            self.domain_structure_gendict['path0_levels'].append(p0l)
            self.domain_structure_gendict['path0_document_tree'][p0l] = []
            for j in range(np.random.choice(range(MIN_NUM_DOC_LEVELS, MAX_NUM_DOC_LEVELS))):
                doc_name = gen_nletter_word(3)
                self.domain_structure_gendict['path0_document_tree'][p0l].append(doc_name)
                self._urls.append(self.domain_structure_gendict['protocol'] + '://' + self.domain_structure_gendict['subdomain'] + \
                            '.' + self.domain_structure_gendict['host'] + '.' + self.domain_structure_gendict['topdomain'] + \
                            '/' + p0l + '/' + doc_name + '.' + self.domain_structure_gendict['document_ext'])

    def get_child(self, land_main_prob=0.5, step_levelout_prob=0.3):
        return self.URLGen_child(self.domain_structure_gendict, land_main_prob, step_levelout_prob)


def gen_nidletter_words(nletters):
    """ return a lowercase word of nletters, where all letters are the same; ie 'kkk', 'aaaa' """
    return ''.join(np.repeat(np.random.choice(list(string.ascii_lowercase)), 3))


def gen_nletter_word(nletters):
    """ return a lowercase word of nletters, randomly drawn from the alphabet; ie 'xhud' """
    return ''.join(np.random.choice(list(string.ascii_lowercase), nletters))


class User(object):
    def __init__(self, init_time, CLICK_DECAY_MEAN=10, TIME_DECAY_MEAN_SEC=30, generators={}):
        self.generators = generators

        self.CLICK_DECAY_MEAN = CLICK_DECAY_MEAN
        self.TIME_DECAY_MEAN_SEC = TIME_DECAY_MEAN_SEC
        self.uid = uuid.uuid4()
        self.init_time = init_time
        self.n_clicks_term = 1 + np.round(np.random.exponential(self.CLICK_DECAY_MEAN-1))

        self._init_props()

    def _init_props(self):
        self.n_clicks = 1
        self.last_click_time = self.init_time

        if self.n_clicks_term == 1:
            self.is_active = False
            self.next_click_time = None
        else:
            self.is_active = True
            self.next_click_time = self.last_click_time + dt.timedelta(
                seconds=np.random.exponential(self.TIME_DECAY_MEAN_SEC))

        for gen in self.generators:
            gen.init_props()

    def step(self):
        self.n_clicks += 1
        self.last_click_time = self.next_click_time
        if self.n_clicks >= self.n_clicks_term:
            self.next_click_time = None
            self.is_active = False
            return
        self.next_click_time = self.last_click_time + dt.timedelta(
            seconds=np.random.exponential(self.TIME_DECAY_MEAN_SEC))

        for gen in self.generators:
            gen.step()

    def __str__(self):
        return str(self.uid) + " " + str(self.next_click_time)

    def get_gen_dict(self):
        return [ gen.get_dict() for gen in self.generators ]


class Click(object):
    def __init__(self, uid, ts, data):
        self.uid = uid
        self.ts = ts
        self.data = data


class ClickGenerator(object):
    """  """
    def __init__(self, url_gen, mean_concur_users, CLICK_DECAY_MEAN, TIME_DECAY_MEAN_SEC):
        self._active_users = []
        self.url_gen = url_gen
        self.mean_concur_users = mean_concur_users
        self.CLICK_DECAY_MEAN = CLICK_DECAY_MEAN
        self.TIME_DECAY_MEAN_SEC = TIME_DECAY_MEAN_SEC

        now = dt.datetime.now()

        for u in range(self.mean_concur_users):
            join_time = now - dt.timedelta(seconds= np.random.uniform( 0, self.CLICK_DECAY_MEAN*self.TIME_DECAY_MEAN_SEC))
            u = User(join_time, self.CLICK_DECAY_MEAN, self.TIME_DECAY_MEAN_SEC, [self.url_gen.get_child()])
            if u.is_active:
                self._active_users.append(u)
        self._active_users = list(sorted(self._active_users, key=lambda u: u.next_click_time))

        self._next_userclick_time = self._active_users[0].next_click_time
        self._next_userjoin_time = now + dt.timedelta(
            seconds=self.TIME_DECAY_MEAN_SEC*((self.CLICK_DECAY_MEAN-1)/self.mean_concur_users + np.random.standard_normal()))

        print(self._next_userjoin_time, self._next_userclick_time)

        #call step as many times until the active users have caught up to the now time
        while self._next_userclick_time < now and self._next_userjoin_time < now:
            self._next()

    def next(self):
        """ work of joins in neccessary """
        if self._next_userjoin_time < self._next_userclick_time:
            click_user = User(self._next_userjoin_time, self.CLICK_DECAY_MEAN, self.TIME_DECAY_MEAN_SEC, [self.url_gen.get_child()])

            if click_user.is_active:
                self._active_users.append(click_user)
                self._active_users = list(sorted(self._active_users, key=lambda u: u.next_click_time))
                self._next_userclick_time = self._active_users[0].next_click_time

            self._next_userjoin_time += dt.timedelta(
                seconds=self.TIME_DECAY_MEAN_SEC * (
                            (self.CLICK_DECAY_MEAN - 1) / self.mean_concur_users + np.random.standard_normal()))

            return Click(click_user.uid, click_user.last_click_time, click_user.get_gen_dict())

        if not len(self._active_users):
            raise Exception('ran out of users')

        click_user = self._active_users.pop(0)
        click_user.step()

        if click_user.is_active:
            self._active_users.append(click_user)
            self._active_users = list(sorted(self._active_users, key=lambda u: u.next_click_time))
        else:
            #print('user dropped')
            pass

        if not len(self._active_users):
            raise Exception('ran out of users')

        self._next_userclick_time = self._active_users[0].next_click_time

        return Click(click_user.uid, click_user.last_click_time, click_user.get_gen_dict())

    def __next__(self):
        return self.next()

    def __iter__(self):
        return self


#-----------------------------------------------------------------
if __name__=="__main__":
    N_CLICKS_TOTAL = int(1E+4)

    TIME_DECAY_MEAN_SEC = 30
    CLICK_DECAY_MEAN = 10

    MEAN_CONCUR_USERS = 200

    num_path0_levels = 8
    MIN_NUM_DOC_LEVELS = 1
    MAX_NUM_DOC_LEVELS = 10


    url_gen = URLGenerator( num_path0_levels, MIN_NUM_DOC_LEVELS, MAX_NUM_DOC_LEVELS )

    g = ClickGenerator(url_gen, MEAN_CONCUR_USERS, CLICK_DECAY_MEAN, TIME_DECAY_MEAN_SEC)



    clicks = []
    for i in range(N_CLICKS_TOTAL):
        clicks.append(g.next())
        if i%50==0:
            print(len(g._active_users))



    print(len(clicks))


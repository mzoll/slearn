
import numpy as np
import datetime as dt
import string
import uuid


from tslearn.data_stream.click_stream.sample_gen.url_gen import URLGenerator
from tslearn.data_stream.click_stream.sample_gen.agent_gen import UserAgentGenerator


class Click(object):
    def __init__(self, uid, ts, data):
        self.uid = uid
        self.ts = ts
        self.data = data


class ClickGenerator(object):
    class User(object):
        def __init__(self, init_time, CLICK_DECAY_MEAN=10, TIME_DECAY_MEAN_SEC=30, generators=[]):
            """ An entity that navigates a website

            :param init_time: datetime
            :param CLICK_DECAY_MEAN: float
            :param TIME_DECAY_MEAN_SEC: float
            :param generators: list
            """
            self.generators = generators

            self.CLICK_DECAY_MEAN = CLICK_DECAY_MEAN
            self.TIME_DECAY_MEAN_SEC = TIME_DECAY_MEAN_SEC
            self.uid = uuid.uuid4()
            self.init_time = init_time
            self.n_clicks_term = 1 + np.round(np.random.exponential(self.CLICK_DECAY_MEAN - 1))

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
            return [gen.get_dict() for gen in self.generators]


    def __init__(self, mean_concur_users, CLICK_DECAY_MEAN, TIME_DECAY_MEAN_SEC, generators):
        """
        generate web-clicks in a time-generative process

        :param generators: list
            additional generators, to generate and fill fields for Click.data; will call gen.get_child() on each
        """
        self.mean_concur_users = mean_concur_users
        self.CLICK_DECAY_MEAN = CLICK_DECAY_MEAN
        self.TIME_DECAY_MEAN_SEC = TIME_DECAY_MEAN_SEC
        self.generators = generators

        self._active_users = []

        now = dt.datetime.now()

        for u in range(self.mean_concur_users):
            join_time = now - dt.timedelta(seconds= np.random.uniform( 0, self.CLICK_DECAY_MEAN*self.TIME_DECAY_MEAN_SEC))
            u = self.User(join_time, self.CLICK_DECAY_MEAN, self.TIME_DECAY_MEAN_SEC, [gen.get_child() for gen in self.generators])
            if u.is_active:
                self._active_users.append(u)
        self._active_users = list(sorted(self._active_users, key=lambda u: u.next_click_time))

        self._next_userclick_time = self._active_users[0].next_click_time
        self._next_userjoin_time = now + dt.timedelta(
            seconds=self.TIME_DECAY_MEAN_SEC*((self.CLICK_DECAY_MEAN-1)/self.mean_concur_users + np.random.standard_normal()))

        print(self._next_userjoin_time, self._next_userclick_time)

        #call step as many times until the active users have caught up to the now time
        while self._next_userclick_time < now and self._next_userjoin_time < now:
            self.next()

    def next(self):
        """ work of joins in neccessary """
        if self._next_userjoin_time < self._next_userclick_time:
            click_user = self.User(self._next_userjoin_time, self.CLICK_DECAY_MEAN, self.TIME_DECAY_MEAN_SEC, [gen.get_child() for gen in self.generators])

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



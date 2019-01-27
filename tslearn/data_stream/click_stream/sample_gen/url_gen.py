import string
import numpy as np


class URLGenerator(object):
    class URLGen_child(object):
        """ Subclass to URLGenerator which can be spawned through URLGenerator.get_child() and reponds to step() and get_dict() """
        def __init__(self, domain_structure_dict, land_main_prob=0.5, step_levelout_prob=0.3):
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

    def __init__(self,  num_path0_levels=10, MIN_NUM_DOC_LEVELS=5, MAX_NUM_DOC_LEVELS=10, **child_kwargs):
        """ Gernerates a deep Website domain structure, which can be used to create abitrary click-patterns

        :param num_path0_levels: int
            number of path0 levels
        :param MIN_NUM_DOC_LEVELS: int
            minimum number of documents for each path0-level
        :param MAX_NUM_DOC_LEVELS: int
            max number of documents for each path0-level
        """

        self.num_path0_levels = num_path0_levels
        self.MIN_NUM_DOC_LEVELS = MIN_NUM_DOC_LEVELS
        self.MAX_NUM_DOC_LEVELS = MAX_NUM_DOC_LEVELS
        self.child_kwargs = child_kwargs

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

    def get_child(self, **kwargs):
        param_dict = self.child_kwargs.copy()
        param_dict.update(kwargs)
        return self.URLGen_child(self.domain_structure_gendict, **param_dict)


def gen_nidletter_words(nletters):
    """ return a lowercase word of nletters, where all letters are the same; ie 'kkk', 'aaaa' """
    return ''.join(np.repeat(np.random.choice(list(string.ascii_lowercase)), 3))


def gen_nletter_word(nletters):
    """ return a lowercase word of nletters, randomly drawn from the alphabet; ie 'xhud' """
    return ''.join(np.random.choice(list(string.ascii_lowercase), nletters))


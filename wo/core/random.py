import random
import string


class RANDOM:
    """Random strings generator"""

    def gen(self, length='24'):
        short_random = ''.join([random.choice
                                (string.ascii_letters + string.digits)
                                for n in range(length)])
        return short_random

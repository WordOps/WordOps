import random
import string


class RANDOM:
    """Random strings generator"""

    def gen(self):
        short_random = ''.join([random.choice
                                (string.ascii_letters + string.digits)
                                for n in range(24)])
        return short_random

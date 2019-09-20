import random
import string


class RANDOM:

    def short(self):
        short_random = ''.join([random.choice
                                (string.ascii_letters + string.digits)
                                for n in range(8)])
        return short_random

    def long(self):
        long_random = ''.join([random.choice
                                (string.ascii_letters + string.digits)
                                for n in range(24)])
        return long_random

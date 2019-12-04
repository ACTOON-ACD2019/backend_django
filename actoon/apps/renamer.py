import os
import random
import string


def create_random_name(path, ext):
    check = False
    rand = None

    while check is False:
        rand = "".join(random.sample(string.ascii_lowercase + string.digits, 20)) + ext
        check = True if not os.path.exists(path + rand) else False

    if rand is None:
        return None
    else:
        return rand

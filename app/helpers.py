from datetime import datetime, timedelta
import os

def date3weekslater(dt):
    timeth = dt + timedelta(weeks=3)
    return timeth.date()

def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)
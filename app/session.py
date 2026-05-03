from datetime import datetime
import pytz

TZ = pytz.timezone("Asia/Jakarta")

def now():
    return datetime.now(TZ)

def is_active_session():
    n = now()
    wd = n.weekday()  # 0=Mon

    # weekend off
    if wd >= 5:
        return False

    h = n.hour
    m = n.minute

    # active: 07:00 - 03:50 next day
    if h >= 7 or h < 4:
        if h == 3 and m > 50:
            return False
        return True

    return False

def is_new_session():
    n = now()
    return n.hour == 7 and n.minute == 0

def is_close_session():
    n = now()
    return n.hour == 3 and n.minute == 50

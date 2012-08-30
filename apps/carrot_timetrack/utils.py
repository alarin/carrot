import datetime
import calendar

def work_hours(start, end=None):
    """
    Calculates work hours count beetween two dates

    If end is None, calcs from current to end
    """
    from_now = False
    if not end:
        from_now = True
        end = start
        start = datetime.datetime.today().date()

    if end < start:
        raise Exception('End is before Start')
    days = 0
    iter = start
    while iter != end:
        if calendar.weekday(iter.year, iter.month, iter.day) in xrange(5):
            days += 1
        iter += datetime.timedelta(days=1)

    if from_now:
        if datetime.datetime.now().time() < datetime.time(20, 00):
            days += 1
    else:
        days += 1
    return days * 8
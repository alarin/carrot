from carrot_timetrack.utils import work_hours
from django.test.testcases import TestCase
from datetime import datetime, timedelta
import calendar


class UtilsTestCase(TestCase):
    def get_date_for_weekday(self, weekday):
        day = datetime.today()
        while calendar.weekday(day.year, day.month, day.day) != weekday:
            day = day + timedelta(days=1)
        return day

    def test_workhours_simple(self):
        monday = self.get_date_for_weekday(0)
        self.assertEquals(16, work_hours(monday, monday + timedelta(days=1)))

    def test_workhours_holidays(self):
        friday = self.get_date_for_weekday(4)
        self.assertEquals(16, work_hours(friday, friday + timedelta(days=3)))

    def test_full_week(self):
        monday = self.get_date_for_weekday(0)
        self.assertEquals(40, work_hours(monday, monday + timedelta(days=6)))
        self.assertEquals(80, work_hours(monday, monday + timedelta(days=13)))


# import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
from math     import log, exp
from dateutil.relativedelta import relativedelta
from collections import OrderedDict

import inspect
import calendar
import pprint
pp = pprint.PrettyPrinter(indent=2)

from request_quotes import USD_LIBOR, Eurodollar_Futures

class SwapCurve:

    def __init__(self, present_date, LIBOR, ED):
        self.present_date    = self.datetime_date(present_date)
        self.short_end_rates = LIBOR
        self.middle_rates    = ED
        
        self.VOL             = 0.005

    def datetime_date(self, str_date):
        ''' Casting string-formatted date to datetime.date '''
        return datetime.strptime(str_date, '%Y-%m-%d').date()

    def delta(self, date):
        ''' Daycount from the present date to the input date divided by 360 '''
        return (date - self.present_date).days / 360

    def term_to_days(self, term):
        """
        Transform a string-formatted term to days

        Args:
            term : str
                e.g. 1 week, 3 months
        Returns:
            int : days
        """
        if 'week' in term:
            return int(term[0]) * 7
        elif 'month' in term:
            if '12' in term:
                return int(term[0]) * 365
            return int(term[0]) * 30

    def ED_settlement_date(self, term):
        """
        Return the third Wednesday of the month of 'term'
        which is a settlement date of Eurodollar Futures

        Args:
            term : string or datetime.date
                e.g. DEC 2020, datetime.date(2020, 03, 02)
                
        Returns:
            int : datetime.date
        """
        try:
            datetime_term = datetime.strptime(term, '%b %Y').date()
        except TypeError:
            datetime_term = term

        year, month = datetime_term.year, datetime_term.month
        calendarSUN = calendar.Calendar(firstweekday=calendar.SUNDAY)
        monthlyCalendar = calendarSUN.monthdatescalendar(year, month)
        return [day 
            for week in monthlyCalendar 
                for day in week 
                    if day.weekday() == calendar.WEDNESDAY and day.month == month
        ][2]
        

    def initial_zero_rate(self, date):
        """
        Calculate the zero rate for the first term of middle curve or long end curve
        in order for the initial discount factor calculation

        Args:
            date : datetime.date
        Returns:
            float : zero rate
        """
        calling_from = inspect.stack()[1].function
        shorter_rate = self.short_end_curve() if calling_from == 'middle_curve' else self.long_end_curve()

        for t1, t2 in zip(list(shorter_rate)[:-1], list(shorter_rate)[1:]):
            if t1 <= date <= t2:
                return ((t2-date).days * shorter_rate[t1]   + \
                        (date-t1).days * shorter_rate[t2] ) / (t2 - t1).days


    def short_end_curve(self):
        """
        Generate zero rates from LIBOR or other short-term rates

        Args:
            None
        Returns:
            OrderedDict:
                key : datetime.date
                value : zero rate
        """
        _dict = dict()
        for term, rate in self.short_end_rates.items():
            if term == 'overnight':
                continue

            days_delta       = self.term_to_days(term)
            discount_factor  = 1 / (1 + (days_delta/360) * (rate/100))
            
            term = (self.present_date + timedelta(days_delta))
            _dict[term] = -log(discount_factor) / (days_delta/360) * 100

        return OrderedDict(sorted(_dict.items()))

    def middle_curve(self):
        """
        Generate zero rates from the quotes for Eurodollar Futures

        Args:
            None
        Returns:
            OrderedDict:
                key : datetime.date
                value : zero rate
        """
        _dict = OrderedDict()
        rates_ED = self.middle_rates
        
        zero_date = self.ED_settlement_date(list(rates_ED)[0])
        zero_rate = self.initial_zero_rate(zero_date)
        _dict[zero_date] = zero_rate
        
        discount_factor = exp(-self.delta(zero_date) * zero_rate/100)

        ED_month = lambda t : datetime.strftime(t, '%b %Y').upper()
        while ED_month(zero_date) in list(self.middle_rates):

            settlement_date  = zero_date
            zero_date = self.ED_settlement_date(settlement_date+relativedelta(months=3))

            futures_rate = 100 - self.middle_rates[ED_month(settlement_date)]
            convexity    = 0.5 * (self.VOL**2) * self.delta(settlement_date) * self.delta(zero_date)
            forward_rate = futures_rate - (convexity*100)

            discount_factor /= (1 + ((zero_date - settlement_date).days/360) * (forward_rate/100))
            zero_rate = 100 * (-log(discount_factor)) / (self.delta(zero_date))
            _dict[zero_date] =zero_rate

        return _dict


    def long_end_curve(self):
        pass
 
# LIBOR = {
#     "1 week" : 0.08813,
#     "1 month" : 0.10325,
#     "3 months" : 0.18538,
#     "6 months" : 0.19588,
#     "12 months" : 0.27775
# }

# Eurodollar = {
#     "DEC 2020" : 99.765,
#     "MAR 2021" : 99.8,
#     "JUN 2021" : 99.8,
#     "SEP 2021" : 99.77,
#     "DEC 2021" : 99.715,
#     "MAR 2022" : 99.715,
# }

# hw1 = SwapCurve("2020-11-04", LIBOR, Eurodollar)
# pp.pprint(hw1.short_end_curve())
# pp.pprint(hw1.middle_curve())


today = datetime(2021,3,10).date()

Mar03_2021 = SwapCurve(
    '2021-03-10',
    USD_LIBOR()[today],
    Eurodollar_Futures()
)

pp.pprint(Mar03_2021.short_end_curve())
pp.pprint(Mar03_2021.middle_curve())







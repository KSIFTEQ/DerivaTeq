from math                   import log, exp
from datetime               import datetime, date, timedelta
from collections            import OrderedDict
from scipy.interpolate      import CubicSpline
from dateutil.relativedelta import relativedelta
import inspect
import calendar
import numpy as np
import matplotlib.pyplot as plt

from request_quotes import USD_LIBOR, Eurodollar_Futures, USD_Swap_Rates

class SwapCurve:
    """ 
    This class is to build a swap curve from the latest quotes for LIBOR, Eurodollar FUtures, and IRS by default, 
    or given rates and date by user.        
    """

    def __init__(
        self, 
        present_date = datetime.strftime(datetime.today(), '%Y-%m-%d'), 
        LIBOR = USD_LIBOR(),
        ED = Eurodollar_Futures(), 
        IRS = USD_Swap_Rates()
    ):
        
        self.present_date = self.__datetime_date(present_date)
        self.LIBOR = LIBOR
        self.ED_futures = ED
        self.IRS = IRS
        self.VOL = 0.005

    def __datetime_date(self, str_date):
        ''' Casting string-formatted date to datetime.date '''
        return datetime.strptime(str_date, '%Y-%m-%d').date()

    def __delta(self, date):
        ''' Daycount from the present date to the input date divided by 360 '''
        return (date - self.present_date).days / 360

    def __term_to_days(self, term):
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

    def __ED_settlement_date(self, term):
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
        

    def __initial_zero_rate(self, date):
        """
        Calculate the zero rate for the first term of middle curve or long end curve
        in order for the initial discount factor calculation

        Args:
            date : datetime.date
        Returns:
            float : zero rate
        """
        calling_from = inspect.stack()[1].function
        shorter_rate = self.short_end_curve() if calling_from == 'middle_curve' else self.middle_curve()

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
        for term, rate in self.LIBOR.items():
            if term == 'overnight':
                continue
            
            days_delta       = self.__term_to_days(term)
            discount_factor  = 1 / (1 + (days_delta/360) * (rate/100))
            
            term = (self.present_date + timedelta(days_delta))
            _dict[term] = -log(discount_factor) / (days_delta/360) * 100

        return OrderedDict(sorted(_dict.items()))

    def middle_curve(self):
        """
        Generate zero rates from the Eurodollar Futures quotes

        Args:
            None
        Returns:
            OrderedDict:
                key : datetime.date
                value : zero rate
        """
        _dict = OrderedDict()
        rates_ED = self.ED_futures

        # short-end curve dict의 term들이 이번달 Eurodollar Futures 결제일보다 모두 늦는 경우
        # 초기 zero rate 값을 short-end curve에서 보간할 수 없음
        # 따라서 zero date를 다음달 결제일로 이월하여 계산
        i = 0; zero_rate = None
        while isinstance(zero_rate, type(None)):
            zero_date = self.__ED_settlement_date(list(rates_ED)[i])
            zero_rate = self.__initial_zero_rate(zero_date)
            i += 1
        discount_factor = exp(-self.__delta(zero_date) * zero_rate/100)

        ED_month = lambda t : datetime.strftime(t, '%b %Y').upper()
        while ED_month(zero_date) in list(self.ED_futures):

            settlement_date  = zero_date
            zero_date = self.__ED_settlement_date(settlement_date+relativedelta(months=3))

            futures_rate = 100 - self.ED_futures[ED_month(settlement_date)]
            convexity    = 0.5 * (self.VOL**2) * self.__delta(settlement_date) * self.__delta(zero_date)
            forward_rate = futures_rate - (convexity*100)

            discount_factor /= (1 + ((zero_date - settlement_date).days/360) * (forward_rate/100))
            zero_rate = 100 * (-log(discount_factor)) / (self.__delta(zero_date))
            _dict[zero_date] =zero_rate

        return _dict


    def long_end_curve(self):
        """
        Generate zero rates from the IRS qutoes

        Args:
            None
        Returns:
            OrderedDict:
                key : datetime.date
                value : zero rate
        """
        _dict = OrderedDict()

        term_to_year = lambda term: int(term.replace('-Year', ''))
        zero_date = self.present_date + relativedelta(years=term_to_year(next(iter(self.IRS))))
        zero_rate = self.__initial_zero_rate(zero_date - relativedelta(months=6))
        sum_discount_factor = exp(-0.5 * zero_rate/100)

        IRS_rates_interpolated =  CubicSpline(
            [term_to_year(term) * 365 for term in self.IRS], # 1-Year -> 365, 2-Year -> 2 * 365, ...
            list(self.IRS.values()), # list of rates
        )

        list_terms =  np.linspace(1,31,60,endpoint=False)[:-1] # 1, 1.5, 2, 2.5, ..., 30
        datetime_term = self.present_date + relativedelta(months=6)
        for term in list_terms:
            datetime_term += relativedelta(months=6)
            
            term_to_days = (datetime_term - self.present_date).days
            swap_rate = IRS_rates_interpolated(term_to_days) / 100
            # print(term_to_days, swap_rate);continue

            discount_factor = (1 - 0.5 * swap_rate * sum_discount_factor)/ (1 + 0.5 * swap_rate)
            zero_rate = 100 * -log(discount_factor) / term
            sum_discount_factor += discount_factor

            _dict[datetime_term] = zero_rate

        return _dict

    def curve(self):
        """
        Generate the entire swap curve using three curves above

        Args:
            None
        Returns:
            OrderedDict:
                key : datetime.date
                value : zero rate
        """

        # Only first two items will be taken from the short-end curve (1-week and 1-month)
        short_end_curve = self.short_end_curve()
        while len(short_end_curve) > 2:
            short_end_curve.popitem()

        # Only first three items will be taken from the middle curve (3-month to < 1-year)
        middle_curve = self.middle_curve()
        while len(middle_curve) > 3:
            middle_curve.popitem()

        return {**short_end_curve, **middle_curve, **self.long_end_curve()}

    def plot_curve(self):
        """
        Plot the entire curve

        Args:
            None
        Returns:
            None
        """
        swap_curve = { 
            (date - self.present_date).days : rate 
                for date, rate in self.swap_curve().items()
        }
        x = list(swap_curve)
        y = CubicSpline(x, list(swap_curve.values()))

        datetime_x = [self.present_date + timedelta(i) for i in x]
        plt.plot(datetime_x, y(x))
        plt.title(f'{self.present_date} Swap Curve')
        plt.show()
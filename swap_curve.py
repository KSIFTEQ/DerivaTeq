from datetime import datetime, date, timedelta
from math     import *
from dateutil.relativedelta import relativedelta


class SwapCurve:

    def __init__(self, eval_date, LIBOR, Eurodollar_Futures, FRA):
        self.eval_date = date.fromisoformat(eval_date)
        self.short_end_rates = self.convert_strTerm_to_dateTiime(LIBOR)
        self.middle_rates    = self.convert_strTerm_to_dateTiime(Eurodollar_Futures)
        self.long_end_rates  = self.convert_strTerm_to_dateTiime(FRA)
        self.VOL             = 0.005

    def str_to_datetime(self, str_date):
        return date.fromisoformat(str_date)

    def tau_12(self, t1, t2):
        return (t2 - t1).days/360

    def tau_0(self, t):
        return (t - self.eval_date).days/360

    def convert_strTerm_to_dateTiime(self, term_to_rate):
        new_dict = dict()
        for term in term_to_rate:
            new_dict[self.str_to_datetime(term)] = term_to_rate[term]
        return new_dict

    def interpolated_initial_zero_rate(self, initial_date, curve_index):
        t0 = initial_date
        if curve_index == 0:
            shorter_curve = self.short_end_curve()
        elif curve_index == 1:
            shorter_curve = self.middle_curve()

        shorter_terms = list(shorter_curve)
        for t1, t2 in zip(shorter_terms[:-1], shorter_terms[1:]):
            if t1 < t0 < t2:
                zero_rate_t1 = shorter_curve[t1]
                zero_rate_t2 = shorter_curve[t2]

                # Linear Interpolation
                return zero_rate_t1                                \
                       + (self.tau_0(t0) - self.tau_0(t1)) \
                       * (zero_rate_t2 - zero_rate_t1)             \
                       / (self.tau_0(t2) - self.tau_0(t1))

    def short_end_curve(self):
        zero_rates = dict()
        for date, rate in self.short_end_rates.items():
            time_delta       = self.tau_0(date)
            discount_factor  = (1 + time_delta*rate)**(-1)
            zero_rates[date] = -log(discount_factor)/time_delta
        return zero_rates

    def middle_curve(self):
        zero_dates = list(self.middle_rates.keys())
        initial_zero_rate = self.interpolated_initial_zero_rate(zero_dates[0], 0)
        first_zero_date   = zero_dates[0]
        zero_rates        = {first_zero_date : initial_zero_rate}
        discount_factor   = exp(-self.tau_0(first_zero_date)*initial_zero_rate)

        zipped = zip(self.middle_rates.items(),
                     zero_dates[1:] + [zero_dates[-1]+timedelta(91)])

        for (t1, rate), t2 in zipped:
            futures_rate     = 100 - rate
            convexity        = 0.5*(self.VOL**2)*self.tau_0(t1)*self.tau_0(t2)
            forward_rate     = futures_rate - convexity*100
            discount_factor /= 1 + self.tau_12(t1, t2) * forward_rate/100
            zero_rates[t2]   = -log(discount_factor)/self.tau_0(t2)
        return zero_rates

    def long_end_curve(self):
        zero_dates = list(self.long_end_rates.keys())
        initial_zero_date = zero_dates[0] - timedelta(184)
        initial_zero_rate = self.interpolated_initial_zero_rate(initial_zero_date, 1)
        discount_factor = exp(-0.5*initial_zero_rate)


        zipped = zip(self.long_end_rates.items(), zero_dates[1:])

        zero_rates = dict()
        for (t1, rate), t2 in zipped:
            r1 = rate
            r2 = self.long_end_rates[t2]
            year_delta = relativedelta(t2,t1).years
            zero_rates[t1] = rate
            t0 = t1; loop_range = range(1, year_delta*2)
            for i, j in zip(reversed(loop_range), loop_range):
                t0 += timedelta(182)
                # rate = (r1**self.tau_12(t1,t0) * r2**self.tau_12(t0,t2))/year_delta
                rate = (r1**(0.5*i/year_delta)) * (r2**(0.5*j/year_delta))
                zero_rates[t0] = rate

        zero_rates[zero_dates[-1]] = self.long_end_rates[zero_dates[-1]]
        return zero_rates

    def entire_curve(self):
        curve = dict()
        curve.update(self.short_end_curve())
        curve.update(self.middle_curve())
        curve.update(self.long_end_curve())
        return curve

LIBOR = {
    "2020-11-11" : 0.0010438,
    "2020-12-04" : 0.0013613,
    "2021-02-04" : 0.0023225,
    "2021-05-04" : 0.0024375,
    "2021-11-04" : 0.0033313
}

Eurodollar_Futures = {
    "2020-12-16" : 99.765,
    "2021-03-17" : 99.8,
    "2021-06-16" : 99.8,
    "2021-09-15" : 99.77,
    "2021-12-15" : 99.715,
}

FRA = {
    "2021-11-04" : 0.0024,
    "2022-11-04" : 0.0026,
    "2023-11-04" : 0.0029,
    "2025-11-04" : 0.0042,
    "2027-11-04" : 0.0059,
    "2030-11-04" : 0.0082,
    "2050-11-04" : 0.0124
}

hw1 = SwapCurve("2020-11-04", LIBOR, Eurodollar_Futures, FRA)

import matplotlib.pyplot as plt
curve = sorted(hw1.entire_curve().items())
x, y  = zip(*curve)
# for i, j  in zip(x,y):
#     print(i,j)
plt.plot(x[:10],y[:10])
plt.show()

from swap_curve import SwapCurve
from request_quotes import USD_LIBOR, Eurodollar_Futures, USD_Swap_Rates

import pprint
pp = pprint.PrettyPrinter(indent=2)


# Get quotes
# pp.pprint(USD_LIBOR())
# pp.pprint(Eurodollar_Futures())
# pp.pprint(USD_Swap_Rates())

# Building today's swap curve
today = SwapCurve()
# pp.pprint(today.short_end_curve())
# pp.pprint(today.middle_curve())
# pp.pprint(today.long_end_curve())
# pp.pprint(today.swap_curve())
today.plot_swap_curve()


LIBOR = {
    "1 week" : 0.10438,
    "1 month" : 0.13613,
    "3 months" : 0.23225,
    "6 months" : 0.24375,
    "12 months" : 0.33313
}

Eurodollar = {
    "DEC 2020" : 99.765,
    "MAR 2021" : 99.8,
    "JUN 2021" : 99.8,
    "SEP 2021" : 99.77,
    "DEC 2021" : 99.715,
    "MAR 2022" : 99.715,
}

IRS = {
    '1-Year'  : 0.24,
    '2-Year'  : 0.26,
    '3-Year'  : 0.29,
    '5-Year'  : 0.42,
    '7-Year'  : 0.59,
    '10-Year' : 0.82,
    '30-Year' : 1.24,
}

rates_201104 = swap_curve.SwapCurve("2020-11-04", LIBOR, Eurodollar, IRS)
rates_201104.plot_swap_curve()

# pp.pprint(rates_201104.short_end_curve())
# pp.pprint(rates_201104.middle_curve())
# pp.pprint(rates_201104.long_end_curve())





# Swap Curve
# Overview

This is to provide a swap curve with the latest market rates (LIBOR, Eurodollar Futures, IRS) or the given rates by user. 

## Example
### Get the recent quotes

```python

import request_quotes
print(request_quotes.USD_LIBOR())
print(request_quotes.Eurodollar_Futures())
print(request_quotes.USD_Swap_Rates())
```
	
### Swap Curve

```python
today = SwapCurve()     # Using the latest market rates by default
print(today.curve())    # Return a swap curve as dict
print(today.plot_curve) # Plot the curve of the day


or you can specify the rates and the date

LIBOR = { 
'1 week'   : 0.08513,
'1 month'  : 0.106,
'2 months' : 0.14088,
'3 months' : 0.1825,
'6 months' : 0.19625,
'12 months': 0.28025,
}

Eurodollar_Futures = {
'MAR 2021' : 99.81,
'APR 2021' : 99.825,
'MAY 2021' : 99.83,
'JUN 2021' : 99.83,
'JUL 2021' : 99.83,
'AUG 2021' : 99.82,
'SEP 2021' : 99.81,
'DEC 2021' : 99.75,
'MAR 2022' : 99.78,
}

IRS = {
'1-Year'  : 0.22,
'2-Year'  : 0.27,
'3-Year'  : 0.46,
'5-Year'  : 0.93,
'7-Year'  : 1.29,
'10-Year' : 1.62,
'30-Year' : 2.06,
}

rates_210315 = SwapCurve("2021-03-15", LIBOR, Eurodollar, IRS)
```

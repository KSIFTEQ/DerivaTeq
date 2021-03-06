from scipy.stats import norm
from math import pi
from numpy import log, sqrt


class ImpliedVol(object):
    def __init__(self, spot, strike, interestRate, dividend, vol, tau):
        self.spot = spot
        self.strike = strike
        self.interestRate = interestRate
        self.dividend = dividend
        self.vol = vol
        self.tau = tau

        self.d1Value = (log(self.spot / self.strike) + (self.interestRate - self.dividend + (self.vol ** 2) / 2 * self.tau)) / (sqrt(self.tau) * self.vol)

    def get_upper_bound(self):
        upperBound = sqrt(pi/2) / (self.strike * sqrt(self.tau))

        return upperBound

    def get_lower_bound(self):
        d1 = self.d1Value
        d2 = d1 - self.vol * sqrt(self.tau)
        lowerBound = -norm.cdf(-d2) / (self.strike * sqrt(self.tau) * norm.pdf(d2))

        return lowerBound

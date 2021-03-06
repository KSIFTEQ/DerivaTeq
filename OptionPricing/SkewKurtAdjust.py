from scipy.stats import norm
from numpy import log, sqrt, exp, pi
from enum import IntEnum


class OptionType(IntEnum):
    CALL = 0
    PUT = 1


class SkewKurtAdjust(object):
    def __init__(self, spot, strike, interestRate, vol, tau, dividend):
        self.spot = spot
        self.strike = strike
        self.interestRate = interestRate
        self.vol = vol
        self.tau = tau
        self.dividend = dividend

        self.d1 = (log(self.spot / self.strike) + (self.interestRate - self.dividend + (self.vol**2)/2 * self.tau)) / (sqrt(self.tau) * self.vol)
        self.d2 = self.d1 - (self.vol * sqrt(self.tau))

        self.callOptionValue = self.spot * exp(-self.dividend * self.tau) * norm.cdf(self.d1) - self.strike * exp(-self.interestRate * self.tau) * norm.cdf(self.d2)

    def get_option_value_jarrow_rudd(self, dataSkew, dataKurt, optionType: OptionType):
        param = sqrt(exp(self.vol**2 * self.tau) - 1)

        logSkew = 3*param + param**3
        logKurt = 16*param**2 + 15*param**4 + 6*param**6 + param**8

        lambda1 = dataSkew - logSkew
        lambda2 = dataKurt - logKurt

        a = (exp(-self.d2**2) / 2) / (self.strike * self.vol * sqrt(self.tau * 2 * pi))

        derivatives1 = a * (self.d2 - self.vol * sqrt(self.tau)) / (self.strike * self.vol * sqrt(self.tau))
        derivatives2 = (a / self.strike**2 * self.vol**2 * self.tau) * \
                       ((self.d2 - self.vol * sqrt(self.tau)) ** 2 - (self.vol * sqrt(self.tau)) * (self.d2 - self.vol * sqrt(self.tau)) - 1)

        q3 = -(self.spot * exp(-self.interestRate * self.tau))**3 * (exp(self.vol**2 * self.tau) - 1)**1.5 * (exp(-self.interestRate * self.tau) / 6) * derivatives1
        q4 = ((self.spot * exp(-self.interestRate * self.tau))**4 * (exp(self.vol**2 * self.tau) - 1)**2 * exp(-self.interestRate * self.tau) * derivatives2) / 24

        if optionType == OptionType.CALL:
            optionValue = self.callOptionValue + lambda1 * q3 + lambda2 * q4

        else:
            optionValue = self.callOptionValue + lambda1 * q3 + lambda2 * q4 - self.spot * exp(-self.dividend * self.tau) + self.strike * exp(self.interestRate * self.tau)

        return optionValue

    def get_option_value_corrado_su(self, dataSkew, dataKurt, optionType: OptionType):
        skewness = dataSkew
        kurtosis = dataKurt

        q3 = (1/6) * self.spot * self.vol * sqrt(self.tau) * ((2 * self.vol * sqrt(self.tau)) - self.d1) * norm.pdf(self.d1) + (self.vol**2 * self.tau * norm.cdf(self.d1))
        q4 = (1/24) * self.spot * self.vol * sqrt(self.tau) * ((self.d1**2 - 1 - 3 * self.vol * sqrt(self.tau)*self.d2) * norm.pdf(self.d1)) + (self.vol**3 * self.tau**1.5 * norm.cdf(self.d1))

        if optionType == OptionType.CALL:
            optionValue = self.callOptionValue + skewness * q3 + (kurtosis - 3) * q4

        else:
            optionValue = self.callOptionValue + skewness * q3 + (kurtosis - 3) * q4 - self.spot * exp(-self.dividend * self.tau) + self.strike * exp(-self.interestRate * self.tau)

        return optionValue

    def get_option_value_modified_corrado_su(self, dataSkew, dataKurt, optionType: OptionType):
        skewness = dataSkew
        kurtosis = dataKurt

        w = (skewness/6) * self.vol**3 * self.tau**1.5 + (kurtosis/24) * self.vol**4 * self.tau**2
        d = self.d1 - (log(1+w / (self.vol*sqrt(self.tau))))

        q3 = (1 / (6+6*w)) * self.spot * self.vol * sqrt(self.tau) * (2 * self.vol * sqrt(self.tau) - d) * norm.pdf(d)
        q4 = (1 / (24+24*w)) * self.spot * self.vol * sqrt(self.tau) * (d**2 - 3 * d * self.vol * sqrt(self.tau) + 3 * self.vol**2 * self.tau - 1) * norm.pdf(d)

        if optionType == OptionType.CALL:
            optionValue = self.callOptionValue + kurtosis * q3 + (kurtosis-3) * q4

        else:
            optionValue = self.callOptionValue + skewness * q3 + (kurtosis - 3) * q4 - self.spot * exp(-self.dividend * self.tau) + self.strike * exp(-self.interestRate * self.tau)

        return optionValue

from numpy import where, sqrt, log


class StochasticABR(object):
    def __init__(self, beta, atTheMoney, strikePrices, spot, tau, marketVol):
        self.beta = beta
        self.tau = tau
        self.spot = spot
        self.strikePrices = strikePrices
        self.atTheMoney = atTheMoney
        self.marketVol = marketVol

        self.strikesOutATM = self.strikePrices[where(self.strikePrices != self.atTheMoney)]
        self.marketVolOutATM = self.marketVol[where(self.strikePrices != self.atTheMoney)]
        self.marketVolATM = self.marketVol[where(self.strikePrices == self.atTheMoney)]

    def calibrate_model(self, args):
        """
        :param args: Sequence; alpha, rho, volatility of volatility
        :return: The Black-76 equivalent volatility
        """

        alpha, rho, vVol = args
        forwardX = self.spot * self.strikesOutATM
        forwardXRatio = self.spot / self.strikesOutATM
        betaComplement = 1 - self.beta

        zValue = (alpha / vVol) * (forwardX ** (betaComplement / 2)) * log(forwardXRatio)
        chiZValue = log((sqrt(1 - 2 * rho * zValue + zValue ** 2) + zValue - rho) / (1 - rho))
        zRatio = zValue / chiZValue

        firstTerm = (alpha * zRatio) / (forwardX ** (betaComplement / 2) *
                                        (1 + (betaComplement ** 2 * (log(forwardXRatio)) ** 2 / 24) + (betaComplement ** 4 * (log(forwardXRatio)) ** 4 / 1920)))

        secondTerm = self.tau * (1 + ((betaComplement ** 2 * alpha ** 2 / (24 * forwardXRatio ** betaComplement)) +
                                      0.25 * (rho * self.beta * vVol * alpha) / (forwardX ** (betaComplement / 2)) +
                                      ((2 - 3 * rho ** 2) * vVol ** 2) / 24))

        outOfATM = (self.marketVolOutATM - firstTerm * secondTerm) ** 2

        atmFirstTerm = alpha / (self.spot ** betaComplement)
        atmSecondTerm = betaComplement ** 2 / (24 * self.spot ** (2 * betaComplement)) + \
                        0.25 * (rho * self.beta * alpha * vVol) / (self.spot ** betaComplement) + ((2 - 3 * rho ** 2) * vVol ** 2) / 24

        atm = (self.marketVolATM - atmFirstTerm * atmSecondTerm) ** 2

        blackEquivVol = sum(outOfATM) + atm

        return blackEquivVol

    def get_vol_of_out_atm(self, alpha, rho, vVol):
        forwardX = self.spot * self.strikesOutATM
        forwardXRatio = self.spot / self.strikesOutATM
        betaComplement = 1 - self.beta

        zValue = (alpha / vVol) * (forwardX ** (betaComplement / 2)) * log(forwardXRatio)
        chiZValue = log((sqrt(1 - 2 * rho * zValue + zValue ** 2) + zValue - rho) / (1 - rho))
        zRatio = zValue / chiZValue

        firstTerm = (alpha * zRatio) / (forwardX ** (betaComplement / 2) *
                                        (1 + (betaComplement ** 2 * (log(forwardXRatio)) ** 2 / 24) + (betaComplement ** 4 * (log(forwardXRatio)) ** 4 / 1920)))

        secondTerm = self.tau * (1 + ((betaComplement ** 2 * alpha ** 2 / (24 * forwardXRatio ** betaComplement)) +
                                      0.25 * (rho * self.beta * vVol * alpha) / (forwardX ** (betaComplement / 2)) +
                                      ((2 - 3 * rho ** 2) * vVol ** 2) / 24))

        volOutATM = firstTerm * secondTerm

        return volOutATM

    def get_vol_of_atm(self, alpha, rho, vVol):
        betaComplement = 1 - self.beta

        atmFirstTerm = alpha / (self.spot ** betaComplement)
        atmSecondTerm = betaComplement ** 2 / (24 * self.spot ** (2 * betaComplement)) + \
                        0.25 * (rho * self.beta * alpha * vVol) / (self.spot ** betaComplement) + ((2 - 3 * rho ** 2) * vVol ** 2) / 24

        volATM = atmFirstTerm * atmSecondTerm

        return volATM

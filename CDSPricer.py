import sympy
import math
from collections import OrderedDict
from sympy.core.numbers import Number
from scipy.optimize import root

class CDSPricer:

    def __init__(self,
                 zeroTenor,
                 zeroRates, 
                 cdsTenor,
                 cdsSpread,
                 recoveryRate,
                 numberPremiumPerYear):

        self.zeroRates  = zeroRates
        self.zeroTenor  = list(map(lambda x:x.upper(),zeroTenor))
        self.cdsTenor   = list(map(lambda x:x.upper(),cdsTenor))
        self.cdsSpread  = [bp/10000 for bp in cdsSpread]
        self.recovery   = 1 - recoveryRate
        self.pymtPeriod = numberPremiumPerYear
        self.H          = sympy.Symbol("H")


    def tenorToDays(self, tenorInput):

        if type(tenorInput) == list:

            Days = []
            for tenor in tenorInput:
                if tenor[-1].upper() == "W":
                    Days.append(int(tenor[:-1]) * 7)

                elif tenor[-1].upper() == "M":
                    Days.append(int(tenor[:-1]) *30)

                elif tenor[-1].upper() == "Y":
                    Days.append(int(tenor[:-1]) *360)

            return Days

        elif type(tenorInput) == str:
            if tenorInput[-1].upper() == "W":
                return(int(tenorInput[:-1]) * 7)

            elif tenorInput[-1].upper() == "M":
                return(int(tenorInput[:-1]) *30)

            elif tenorInput[-1].upper() == "Y":
                return(int(tenorInput[:-1]) *360)

    def zeroCurve(self):

        zeroCurveDict = dict(zip(self.tenorToDays(self.zeroTenor), self.zeroRates))
        zeroCurveDict[0] = 0

        defaultTenor = [x*0.25 for x in range(1,41)]
        missingTenor = [tenor*360 for tenor in defaultTenor if tenor not in self.tenorToDays(self.zeroTenor)]



        for i, tenor in enumerate(missingTenor):

            for j, zeroTenor in enumerate(zeroCurveDict):
                if zeroTenor > tenor:
                    break


            x1 = list(zeroCurveDict)[j-1]; x2 = list(zeroCurveDict)[j]
            y1 = list(zeroCurveDict.values())[j-1]; y2 = list(zeroCurveDict.values())[j]

            zeroCurveDict[tenor] = y1 + (tenor - x1) * (y2 - y1) / (x2 - x1)

        # return zeroCurveDict
        return OrderedDict(zeroCurveDict)
        # return dict((x,y) for x,y in sorted(zeroCurveDict.items(), key=lambda key: key[1]))


    def calcNumLoop(self, tenor):

        if tenor[-1].upper() == "M":
            tenorInt   = int(tenor[:-1])
            numLoop = tenorInt / 3

        elif tenor[-1].upper() == "Y":
            tenorInt   = int(tenor[:-1])
            numLoop = tenorInt * 4

        return int(numLoop + 1)

    def premiumLeg(self, tenor, spread):

        premium = 0
        for n in range(1, self.calcNumLoop(tenor)):
            dt = 0.25
            r  = self.zeroCurve()[n*dt*360]
            Z  = math.exp(-r * (dt*n))
            Q  = sympy.exp(-dt * (n-1) * self.H) + sympy.exp(-dt * n * self.H)
            # print(n, -r, dt*n, Z, Q)
            premium += dt * Z * Q
            # print(Z, Q)

        return premium
        # return expr.xreplace({n : round(n,3) for n in expr.atoms(Number)})


    def protectionLeg(self, tenor):

        zeroCurve = self.zeroCurve()

        cdsZeroCurve = {0:0}
        protection = 0; numRange = self.calcNumLoop(tenor)


        for n in range(1, numRange):
            dt = 0.25
            t1 = int(dt*(n-1)*360); t2 = int(dt*n*360)


            cdsZeroCurve[t2] = zeroCurve[t2]
            r0 = cdsZeroCurve[t1]; r1 = cdsZeroCurve[t2]

            Z  = math.exp(-r0 * (dt*(n-1))) + math.exp(-r1 * (dt*n))
            Q  = sympy.exp(-dt * (n-1) * self.H) - sympy.exp(-dt * n * self.H)

            # print(Z, Q)
            protection += Z * Q

        return self.recovery * protection
        # expr = (self.recovery * protection)
        # return expr.xreplace({n : round(n, 3) for n in expr.atoms(Number)})



    def cdsBootstrap(self):
        # print('\n')
        # self.premiumLeg('6m', 80)
        # print('\n')
        # self.protectionLeg('6m')


        for tenor, spread in zip(self.cdsTenor, self.cdsSpread):


        #     # print(self.premiumLeg(tenor, spread)- self.protectionLeg(tenor))
        #     # print('')
            premium = self.premiumLeg(tenor,spread)
            protection = self.protectionLeg(tenor)

            print(premium);print(protection);
            hazardRate =  sympy.solve(sympy.Eq(spread, protection/premium))

            print(tenor, hazardRate)




        # tenor = '6m'; spread = 80/10000


        # print(self.premiumLeg(tenor, spread)); print(self.protectionLeg(tenor))

        # print(self.premiumLeg(tenor, spread) - self.protectionLeg(tenor))




            # hazardCurve[tenor] = hazardRate





zeroTenor = ['1w','1m','3m','6m','1y','2y','3y', '5y', '7y', '10y', '15y', '20y']
zeroRates = [0.001,0.0014,0.0021,0.0022,0.0028,0.0026,0.0029, 0.0042, 0.0059, 0.0083, 0.0094, 0.105]
cdsTenor  = ['6m', '1y', '2y', '3y', '4y', '5y', '7y', '10y']
cdsSpread = [80, 80, 90, 100, 110, 120, 150, 160]
assignment2 = CDSPricer(zeroTenor, zeroRates,cdsTenor,cdsSpread,0.4,4)

assignment2.cdsBootstrap()

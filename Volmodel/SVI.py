"""

SVI model Calibration

"""

# ----------------------------------------------------------------
# IMPORTS

import numpy as np
from scipy.optimize import minimize, fmin


# ----------------------------------------------------------------
# FUNCTIONS 

class SVI:
    
    def __init__(self,  strikes ,forward, tau, marketvol):
        
        self.forward = forward
        self.strikes = strikes
        self.tau = tau
        self.marketw = marketvol**2 * tau
        
    def calibration(self, args):
        
        alpha, beta, rho, mu, sigma = args 
        k = np.log(self.strikes / self.forward)  
        modelw = alpha + beta * ( rho * (k - mu) + np.sqrt( (k - mu)**2 + sigma**2 ) )        
        objective = ( modelw - self.marketw )**2
        
        return sum( objective )

    def volofmodel(self, alpha, beta, rho, mu, sigma):

        k = np.log(self.strikes / self.forward)
        modelw = alpha + beta * ( rho * (k - mu) + np.sqrt( (k - mu)**2 + sigma**2 ) )
        
        return modelw


if __name__=="__main__":

    forward = 280
    strikes = np.array([250,255,260,265,270,275,280])
    marketvol = np.array([0.3,0.28,0.26,0.24,0.22,0.20,0.18]) 
    tau = 0.1
    marketw = marketvol**2 * tau
    k = np.log(strikes / forward)

    # SVI Model의 Calibration은 Contraints를 설정하는 것이 중요
    cons=(
        {'type': 'ineq', 'fun': lambda x: x[0] - 10**(-5)},    
        {'type': 'ineq', 'fun': lambda x: max(marketw) - x[0]},
        {'type': 'ineq', 'fun': lambda x: x[1] - 0.001 },
        {'type': 'ineq', 'fun': lambda x: 1 - x[1]},
        {'type': 'ineq', 'fun': lambda x: x[2] + 1},
        {'type': 'ineq', 'fun': lambda x: 1 - x[2]},
        {'type': 'ineq', 'fun': lambda x: x[3] - 2 * min(k)},
        {'type': 'ineq', 'fun': lambda x: 2 * max(k) - x[3]},
        {'type': 'ineq', 'fun': lambda x: x[4]},
        {'type': 'ineq', 'fun': lambda x: 1 - x[4]} )
        
    initialguess = [0.5*min(marketw), 0.1, -0.5, 0.1, 0.1]
    svi = SVI(strikes, forward, tau, marketvol)
    opt = minimize(svi.calibration, initialguess, constraints = cons)
    solutions = opt.x
    modelw = svi.volofmodel(solutions[0], solutions[1], solutions[2], solutions[3], solutions[4])
    modelvol = np.sqrt( modelw / tau ) 




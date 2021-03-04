#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 11:51:51 2021

@author: yuhojin
"""

from scipy.stats import norm
import numpy as np

class SkewKurtmodels:
    
    def __init__(self, s, strike, interest, vol, tau, dividend):
        
        self.s = s
        self.strike = strike
        self.interest = interest
        self.vol = vol
        self.tau = tau
        self.dividend = dividend
        
        self.d1 = ( np.log(self.s / self.strike) + (self.interest - self.dividend + (self.vol**2)/2) * self.tau ) / \
            (np.sqrt(self.tau) * self.vol)
            
        self.d2 = self.d1 - ( self.vol * np.sqrt(self.tau) ) 
        
        self.call = self.s * np.exp(-self.dividend * self.tau) * norm.cdf(self.d1) - self.strike * np.exp(-self.interest * self.tau) * norm.cdf(self.d2)
        
    #This model adjusts for skewness and kurtosis in the asset price directly not in the return distribution
    
    def BSM_call(self):
        
        return self.call

    
    def JarrowRudd_call(self, dataskew, datakurt, callputtype):
        
        y = np.sqrt(np.exp(self.vol**2 * self.tau) - 1)
        
        logskew = 3 * y + y**3
        logkurt = 16*y**2 + 15*y**4 + 6*y**6 + y**8
        
        lambda1 = dataskew - logskew
        lambda2 = datakurt - logkurt
        
        a =  (np.exp(-self.d2**2) / 2)/(self.strike * self.vol * np.sqrt(self.tau * 2 * np.pi))
        
        deriv1 = a * (self.d2 - self.vol * np.sqrt(self.tau)) / (self.strike * self.vol * np.sqrt(self.tau)) 
        
        deriv2 = ( a / self.strike**2 * self.vol**2 * self.tau ) * \
            ( (self.d2 - self.vol * np.sqrt(self.tau) )**2 - ( self.vol * np.sqrt(self.tau) * (self.d2 - self.vol * np.sqrt(self.tau)) ) -1 )
        
        q3 = -(self.s * np.exp(-self.interest * self.tau ))**3 * (np.exp(self.vol**2 * self.tau) - 1)**(1.5) * \
            ( (np.exp(-self.interest * self.tau)) / 6 ) * deriv1
            
        
        q4 = ( ( self.s * np.exp(-self.interest * self.tau) )**4 * (np.exp(self.vol**2 * self.tau) - 1)**2 * np.exp(-self.interest * self.tau) * deriv2 ) / 24
         
        if callputtype == "call":
            
            value = self.call + (lambda1 * q3) + (lambda2 * q4)
        
        ## put-call parity
        elif callputtype == "put":
            
            value = self.call + (lambda1 * q3) + (lambda2 * q4) - ( self.s * np.exp(-self.dividend * self.tau ) )+ self.strike * np.exp(-self.interest * self.tau)
            
        
        return value
    

    # This model adjusts for skewness and kurtosis in the return distribution not asset price itself.
    
    def CorradoSu_call(self, dataskew, datakurt, callputtype): # dataskew, datakurt of which return distribution
        
        mu3 = dataskew
        
        mu4 = datakurt
        
        q3 = (1/6) * self.s * self.vol * np.sqrt(self.tau) *( (2*self.vol*np.sqrt(self.tau) - self.d1)*norm.pdf(self.d1) + (self.vol**2 * self.tau * norm.cdf(self.d1)) ) 
        
        q4 = (1/24) * self.s * self.vol * np.sqrt(self.tau) * (  (self.d1**2 - 1 - 3*self.vol*np.sqrt(self.tau)*self.d2)*norm.pdf(self.d1) + ( self.vol**3 * self.tau**(1.5) * norm.cdf(self.d1) ) )

        
        if callputtype == "call":
            
            value = self.call + (mu3 * q3) + (mu4 - 3)*q4
        
        ## put-call parity
        elif callputtype == "put":
            
            value = self.call + (mu3 * q3) + (mu4 - 3)*q4 - self.s * np.exp(-self.dividend * self.tau) + self.strike * np.exp(-self.interest * self.tau)

        print(mu3, mu4, q3, q4)

        return value
    
    # This model adjusts for skewness and kurtosis in the return distribution not asset price itself.
    # original model does not satisfy a martingale restriction -> modified
    
    def ModifiedCorradoSu_Call(self, dataskew, datakurt, callputtype): # dataskew, datakurt of which return distribution
    
        mu3 = dataskew
        mu4 = datakurt
        
        w = (mu3/6) * self.vol**3 * self.tau**(1.5) + (mu4/24) * self.vol**4 * self.tau**2
        
        d = self.d1 - (np.log(1+w) / (self.vol*np.sqrt(self.tau)) )
    
        q3 = (1 / (6 * (1+w)) ) * self.s * self.vol * np.sqrt(self.tau) * ( 2 * self.vol*np.sqrt(self.tau) - d ) * norm.pdf(d) 
        
        q4 = (1 / (24 * (1+w))) * self.s * self.vol * np.sqrt(self.tau) * (d**2 - 3 * d * self.vol * np.sqrt(self.tau) + 3 * self.vol**2 * self.tau - 1 ) * norm.pdf(d)
        
        if callputtype == "call":
            
            value = self.call + (mu3 * q3) + (mu4 - 3)*q4
            
        ## put-call parity    
        elif callputtype == "put":
            
            value = self.call + (mu3 * q3) + (mu4 - 3)*q4 - self.s * np.exp(-self.dividend * self.tau) + self.strike * np.exp(-self.interest * self.tau)
        
        return value
    
    
if __name__=="__main__":
    
    
    s = 270
    strike = 265
    interest = 0.02
    vol = 0.3
    tau = 1
    dividend = 0
    callputtype = "call"
    
    dataskew = 1
    datakurt = 4
    ex = SkewKurtmodels(s, strike, interest, vol, tau, dividend)
        
    BSMCall = ex.BSM_call()
    JarrowRuddCall = ex.JarrowRudd_Call(dataskew, datakurt, callputtype)
    CorradoSuCall = ex.CorradoSu_Call(dataskew, datakurt, callputtype)
    ModifiedCorradoSucall = ex.ModifiedCorradoSu_Call(dataskew, datakurt, callputtype)

    
        
"""
Brownian Bridge using conditional expectation 
"""

# ----------------------------------------------------------------
# IMPORTS

import numpy as np
import math

# ----------------------------------------------------------------
# FUNCTIONS 

def brownianBridge(
    numberOfstepinhalfyear, starttime, 
    endtime, startrandomnormal, endrandomnormal
    ):  
    # numberOfstepinhalfyear is expected to be power of 2

    timestep = np.linspace(starttime, endtime, numberOfstepinhalfyear + 1)
    Z = np.random.normal(0, 1, size = numberOfstepinhalfyear + 1)
    holder = numberOfstepinhalfyear
    j_max = 1

    Wiener = np.zeros(numberOfstepinhalfyear + 1)

    Wiener[-1] = np.sqrt(endtime) * endrandomnormal
    Wiener[0] = np.sqrt(starttime) * startrandomnormal

    powerofendtime = int(math.log(numberOfstepinhalfyear, 2))

    for k in range(powerofendtime):

        middle_min = int(holder / 2)
        middle = middle_min
        lower = 0
        upper = holder

        for j in range(j_max):

            a = (
                (timestep[upper] - timestep[middle]) * Wiener[lower]
                + (timestep[middle] - timestep[lower]) * Wiener[upper]
            ) / (timestep[upper] - timestep[lower])
           
            b = np.sqrt(
                (timestep[middle] - timestep[lower])
                * (timestep[upper] - timestep[middle])
                / (timestep[upper] - timestep[lower])
            )

            Wiener[middle] = a + b * Z[middle]

            middle = middle + holder
            lower = lower + holder
            upper = upper + holder

        j_max = 2 * j_max
        holder = middle_min

    return Wiener


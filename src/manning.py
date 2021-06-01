# -*- coding: utf-8 -*-
"""
Mannings equation for flow rate and velocity for different channel cross
sections

Created on Tue Sep 29 01:40:32 2020
@author: 0x1A3
"""
from math import pow, sqrt, sin, cos, acos

def manning(n, R, S, SI=True):
    """
    Flow velocity for turbulent flow using Manning's equation

    Parameters
    ----------
    n : float
        Manning roughness coefficient.
    R : float
        hydraulic radius of the cross section (square meters or square foot).
    S : float
        Channel slope adimentional units (m/m or ft/ft).
    SI : boolean, optional
        True for International System or metric units (m, s, m^3/s), False for
        US customary units (ft, s, cfs). The default is True.

    Returns
    -------
    float
        Flow velocity in meters (or foot) per second.

    """
    if SI:
        k = 1.
    else:
        k = 1.486 # 1.49 
    return (k/n) * pow(R, 2/3.) * pow(S, 1/2.)
    
def manningQ(n, A, R, S, SI=True):
    """
    Flow rate for turbulent flow using Manning's equation

    Parameters
    ----------
    n : float
        Manning roughness coefficient.
    A : float
        Cross-sectional area of the channel in (sq. meters or sq. ft)
    R : float
        hydraulic radius of the cross section (square meters or square foot).
    S : float
        Channel slope adimentional units (m/m or ft/ft).
    SI : boolean, optional
        True for International System or metric units (m, s, m^3/s), False for
        US customary units (ft, s, cfs). The default is True.

    Returns
    -------
    float
        Flow rate, cubic meters per second (cms) or cubic foot per second (cfs)

    """
    return A * manning(n, R, S, SI)

def checkTurbulent(n, R, S, SI=True):
    if SI:
        threshold = 1.1e-13
    else:
        threshold = 1.9e-13
    val = pow(n, 6) * sqrt(R * S)
    return val, val > threshold 

class Triangular:
    """ Triangular
    
    A representation of a triangular cross-section open channel
    """
    def __init__(self, z, y):
        """
        

        Parameters
        ----------
        z : int
            z is the wall slope represented as 1:z, rise:run
        y : float
            y is the depth of the water

        Returns
        -------
        None.

        """     
        self.z = z
        self.y = y
    
    def setDepth(self, y):
        self.y = y
    
    def getArea(self):
        return self.z * self.y * self.y
    
    def getWettedPerimeter(self):
        return 2. * self.y * sqrt(1 + pow(self.z, 2))
    
    def getHydraulicRadius(self):
        return self.getArea() / self.getWettedPerimeter()
    
    def getTopWidth(self):
        return 2. + self.z * self.y
    
    def getDesignParameter(self):
        return 8. / (3 * self.y)

class Rectangular:
    def __init__(self, B, y):
        """
        Parameters
        ----------
        B : float
            B is the base of the channel
        y : float
            y is the depth of the water

        Returns
        -------
        None.

        """
        self.B = B
        self.y = y
    
    def setDepth(self, y):
        self.y = y
        
    def getArea(self):
        return self.B * self.y
    
    def getWettedPerimeter(self):
        return self.B + 2. * self.y
    
    def getHydraulicRadius(self):
        return self.getArea() / self.getWettedPerimeter()
    
    def getTopWidth(self):
        return self.B
    
    def getDesignParameter(self):
        return (5. * self.B + 6. * self.y) / (3. * self.y * (self.B + 2. * self.y))
    
class Trapezoidal:
    def __init__(self, B, z, y):
        self.B = B
        self.z = z
        self.y = y
        
    def setDepth(self, y):
        self.y = y
        
    def getArea(self):
        return (self.B + self.z * self.y) * self.y
    
    def getWettedPerimeter(self):
        return self.B + 2. * self.y * sqrt(1. + pow(self.z, 2))
    
    def getHydraulicRadius(self):
        return self.getArea() / self.getWettedPerimeter()
    
    def getTopWidth(self):
        return self.B + 2. * self.z + self.y
    
    def getDesignParameter(self):
        num = (self.B + 2. * self.z * self.y) * (5. * self.B + 6. * self.y * \
            sqrt(1. + pow(self.z, 2))) + 4. * self.z * pow(self.y, 2) * \
            sqrt(1. + pow(self.z, 2))
        den = 3. * self.y * (self.B + self.z * self.y) * (self.B + 2. * 
            self.y * sqrt(1. + pow(self.z, 2)))
        return num / den

class Circle:
    def __init__(self, d, y):
        self.d = d
        self.y = y
        self.theta = 2. * acos(1. - ((2. * self.y) / self.d))
        
    def getArea(self):
        return 1./8. * (self.theta - sin(self.theta)) * pow(self.d, 2)
    
    def getWettedPerimeter(self):
        return 0.5 * self.theta * self.d
    
    def getHydraulicRadius(self):
        return self.getArea() / self.getWettedPerimeter()
    
    def getTopWidth(self):
        return (sin(self.theta / 2.)) * self.d
    
    def getTopWidthFromY(self):
        return 2. * sqrt(self.y * (self.d - self.y))
    
    def getDesignParameter(self):
        num = 4. * (2. * sin(self.theta) + 3. * self.theta - 5. * \
                    self.theta * cos(self.theta))
        den = 3. * self.d * self.theta * (self.theta - sin(self.theta)) * \
            sin(self.theta / 2.)
        return num / den

if __name__ == "__main__":
    n = 0.017
    z = 2.
    y = 4.
    S = 0.02
    triang = Triangular(z, y)
    SI = False
    
    A = triang.getArea()
    P = triang.getWettedPerimeter()
    R = triang.getHydraulicRadius()
    Q = manningQ(n, A, R, S, SI)
    val, cond = checkTurbulent(n, R, S, False)
    
    str_units = "SI Units" if SI == True else "US customary units"
    
    print("Units:                {:<}".format(str_units))
    print("Area (A):             {:-8.4f}".format(A))
    print("Wetted perimeter (P): {:-8.4f}".format(P))
    print("Hydraulic radius (R): {:-8.4f}".format(R))
    print("Discharge (Q):        {:-8.4f}".format(Q))
    print("Flow is turbulent:    {}".format(cond))



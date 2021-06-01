# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 11:08:19 2020

@author: 0x1A3
"""
from math import pow, cos, sin, tan, radians

def manningDepth(n, b, Q, S, SI=True):
    if SI:
        k = 1.
    else:
        k = 1.49 # 1.486 
    return pow(((n * Q)/(k * b * pow(S, 1/2.))), 3/5.)


def riprapCSU(b, Q, S, phi, theta, SG, SF=1.5, SI=True):
    D = 0.01
    inc = 1E-2
    tol = 1E-2
    max_iter = 1e5
    
    # specific weight of water
    if SI:
        gamma = 9810  # N/m^3
    else:
        gamma = 62.4  # lb/ft^3

    roughness = lambda D : 0.0395 * pow(D, 1/6.)
    trac_force = lambda gamma, d, S : gamma * d * S
    stability_factor = lambda tau, gamma, SG, D : (21. * tau) / (gamma * (SG-1) * D)
    safety_factor = lambda theta, phi, eta : (cos(radians(theta)) * tan(radians(phi))) / (sin(radians(theta)) + eta * tan(radians(phi)))
    # Mannings roughness coefficient Eq. 4.32
    n = roughness(D)
    # Depth to convey the flow
    d = manningDepth(n, b, Q, S, SI)
    # tractive force
    tau = trac_force(gamma, d, S)
    # stability factor
    eta = stability_factor(tau, gamma, SG, D)
    # satety factor
    SFb = safety_factor(theta, phi, eta)
    diff = SF - SFb
    accept = abs(diff) < tol
    
    c_iter = 0  # Initialize the current iteration
    
    print("\nSearching riprap size by iterations\n")
    print("Iter        D        n       phi        d       tau      eta      SFb     Diff   Accept?")
    print("{:8} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:^8}".format(c_iter, D, n, phi, d, tau, eta, SFb, diff, str(accept)))
    
    while (accept != True and c_iter < max_iter):
        D += inc
        c_iter += 1
        
        # Mannings roughness coefficient Eq. 4.32
        n = roughness(D)
        # Depth to convey the flow
        d = manningDepth(n, b, Q, S, SI)
        # tractive force
        tau = trac_force(gamma, d, S)
        # stability factor
        eta = stability_factor(tau, gamma, SG, D)
        # satety factor
        SFb = safety_factor(theta, phi, eta)
        diff = SF - SFb
        accept = abs(diff) < tol
        
        print("{:8} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:^8}".format(c_iter, D, n, phi, d, tau, eta, SFb, diff, str(accept)))

    return D

if __name__ == "__main__":
    # Example 4.17 from Textbook
    SIunits = False
    Q = 115  # cfs
    S = 0.1  # channel slope
    b = 18.  # bottom width
    D50 = 2.5
    SG = 2.65 # specific gravity of stone
    
    theta = 5.71
    phi = 42 # angle of response
    SF = 1.5 # safety factor
    
    ans = riprapCSU(b, Q, S, phi, theta, SG, SF, SIunits)
    
    print("\nSOLUTION:\nThe riprap size is: {:-8.4f}".format(ans))
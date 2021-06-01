# -*- coding: utf-8 -*-
"""
Open channel design

Created on Mon Oct 19 11:26:35 2020
@author: 0x1A3
"""
from manning import manning, Triangular, Trapezoidal, Rectangular

def print_iter(it):
    print("{:8} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:-8.4f} {:^8}".format(
        it.get('i'),
        it.get('y'),
        it.get('A'),
        it.get('R'),
        it.get('v'),
        it.get('Q'),
        it.get('d'),
        it.get('ok')))

def design_channel(n, S, Qdes, **kwargs):
    
    _disp = kwargs.get('disp', 1)  # display iterations
    _tol = kwargs.get('tol', 1E-2)  # tolerance of solution
    _inc = kwargs.get('inc', 1E-2)  # increment
    _max_iter = kwargs.get('max_iter', 1E5)  # maximum iterations
    
    B = kwargs.get('base', 0)
    z = kwargs.get('z', 0)
    SI = kwargs.get('SI', True)
    y = kwargs.get('y', 0.01)
    
    # Define the channel cross-section according to the input data
    if (B >0 and z == 0):
        # Rectangular channel
        section = Rectangular(B, y)
    elif (B == 0 and z > 0):
        # Triangular channel
        section = Triangular(z, y)
    elif (B > 0 and z > 0):
        # Trapezoidal channel
        section = Trapezoidal(B, z, y)
    else:
        print("Cannot design channel")
        return None
    
    iteration = {}
    saved_iter = {}
    
    # First iteration
    A = section.getArea()
    R = section.getHydraulicRadius()
    v = manning(n, R, S, SI)
    Q = A * v
    diff = Qdes - Q
    prev_diff = Qdes - Q
    accept = str(abs(diff) < _tol)
    
    c_iter = 0  # Initialize the current iteration
    
    iteration['i'] = c_iter
    iteration['y'] = y
    iteration['A'] = A
    iteration['R'] = R
    iteration['v'] = v
    iteration['Q'] = Q
    iteration['d'] = diff
    iteration['ok'] = accept
    
    print("\nSearching water depth by iterations\n")
    print("Iter        y        A        R        v        Q       Diff   Accept?")
    print_iter(iteration)

    # Iterate to find the channel depth
    while (accept != True and c_iter < _max_iter):
        y += _inc
        c_iter += 1
        
        # Save the previous iteration
        saved_iter = iteration
        
        # Calculate values of current iteration
        section.setDepth(y)
        A = section.getArea()
        R = section.getHydraulicRadius()
        v = manning(n, R, S, SI)
        Q = A * v
        diff = Qdes - Q
        accept = abs(diff) < _tol
        
        # Update current iteration
        iteration['i'] = c_iter
        iteration['y'] = y
        iteration['A'] = A
        iteration['R'] = R
        iteration['v'] = v
        iteration['Q'] = Q
        iteration['d'] = diff
        iteration['ok'] = accept
        
        # Print the iterations rows
        if (c_iter % _disp) == 0:
            print_iter(iteration)
            
        
        if (saved_iter['d'] > 0) and (iteration['d'] < 0):
            save = False
        # # Solution not found for the level of tolerance
        # if (prev_diff > 0) and (diff < 0):
        #     print("Warning: solution not found for this tolerance. Best approximation is given.")
        #     break
        # else:
            # This will save the current iteration, we need to save the previous
        #     saved_iter = iteration
        # prev_diff = diff

    return y

if __name__ == "__main__":
    # Problem 4.3 from textbook (homework) 
    Qdes = 30
    S = 0.01
    n = 0.025
    side_slope = 1
    
    ans = design_channel(n, S, Qdes, z=side_slope, SI=False, tol=0.1)
    
    # Design erodible channel
    # Example 4.10 from textbook
    # SI = False
    # Q = 20
    # B = 6
    # S = 0.005
    # z = 3
    # n = 0.020  # ordinary firm loam Table 4.2
    # vp = 3.5
    
    # ans = design_channel(n, S, Q, z=z, base=B, SI=False)
    print("\nSOLUTION:\nThe channel depth is: {:-8.4f}".format(ans))
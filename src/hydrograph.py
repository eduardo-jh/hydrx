#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 21:18:22 2020

@author: ecoslacker
"""
from rainfall import SCSStorm

class Hydrograph:
    def __init__(self, iabs, qp, storm):
        self._iabs = iabs
        self._qp_uh = qp
        self._storm = storm
        self._step = 0
        self._time = []
        self._cumulative_runoff = []
        self._qp_sh = 0
    
    def get_cumulative_runoff(self):
        return self._cumulative_runoff
    
    def runoff(self):
        # Hydrograph time step should match the step of the hyetograph
        self._step = self._storm.step
        self._time.clear()
        self._cumulative_runoff.clear()

        cum_rain = 0
        cum_time = 0
        for rain in self._storm.get_hyetograph():
            cum_rain += rain
            if cum_rain <= self._iabs:
                # Account the rainfall into the initial abstractions
                self._cumulative_runoff.append(0)
            else:
                # Once initial abstractions are covered, the runoff can be computed
                runoff = 5
                self._cumulative_runoff.append(runoff)
            self._time.append(cum_time)
            cum_time += self._step
        
        print(self._time)
        print(self._cumulative_runoff)
        
        
        
        
if __name__ == "__main__":
    
    # Generate an exmple storm from HW#3 P6
    PD = 3.34  # rainfall for 12-hr, 100-yr rainfall
    D = 12  # 12-hr rainfall duration
    ts = 0.667  # 40 minutes time step
    storm = SCSStorm(PD, D, ts, SI=False)
    storm.plot_hyetograph()
    print(storm)
    
    Ia = 0.19  # Initial abstractions
    qp = 242  # peak flowrate for the unit hydrograph in CFS 
    hydro = Hydrograph(Ia, qp, storm)
    hydro.runoff()
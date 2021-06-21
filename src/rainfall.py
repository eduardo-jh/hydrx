#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 15:35:00 2020

@author: Eduardo Jiménez Hernández
"""
import csv
import matplotlib.pyplot as plt

class Storm:
    def __init__(self, rainfall, duration=24, timestep=0.5, SI=True):
        """
        Creates a Storm object that represents the depth and distribution
        of a rainfall event.

        Parameters
        ----------
        rainfall : float
            A depth used for the precipitation event, in inches or mm
        duration : int, optional
            The storm (rainfall event) duration, in hours. The default is 24.
        timestep : float, optional
            Time step to generate the rainfall distribution, in hours. The default is 0.5.
        SI : bool, optional
            International Systems units, False for US Customary units. The default is True.

        Returns
        -------
        None.

        """
        assert (duration >=0 and duration<=24), "Storm duration should be between 0 and 24 hr"
        self.duration = duration
        self.step = timestep
        self.rainfall = rainfall
        self.time = []
        self.hyetograph = []
        self.cumulative_rain = []
        self.str = ""
        self.table = "There are no results to show."
        self.SIunits = SI
        self.rainunits = 'mm'
        self.headers = ["Time", "P/P24", "Depth", "Inc. Depth"]
        
        # Display the units according the unit system
        self.rainunits = 'mm' if self.SIunits else 'in'
        
        self.str_rep()
        
    def __str__(self):
        """A string representation of the storm class"""
        return self.str
        
    def str_rep(self):
        """Generate a string representation for the class"""
        self.str = "A Storm instance:\n"
        self.str += " Rainfall: " + str(self.rainfall) + " (" + self.rainunits + ")\n"
        self.str += " Duration: " + str(self.duration) + "\n"
        self.str += " Time step: " + str(self.step)+ "\n"

class SCSStorm(Storm):
    
    def __init__(self, PD, D=24, tstep=0.5, SI=True):
        Storm.__init__(self, PD, duration=D, timestep=tstep, SI=SI)
        self.pt = []  # SCS Ordinate P(t)/P24, rain distrib. factor
        self.str_rep()
        
        # Calculate the SCS Type Curve
        self.scs_curve()
        
        # Calculate the hyetograph
        self.generate_hyetograph()

    def __str__(self):
        """A string representation of the storm class"""
        return self.str
    
    def str_rep(self):
        """Generate a string representation for the class"""
        self.str = "A SCS Storm instance:\n"
        self.str += " Rainfall: " + str(self.rainfall) + " (" + self.rainunits + ")\n"
        self.str += " Duration: " + str(self.duration) + "\n"
        
    def get_hyetograph(self):
        return self.hyetograph
    
    def get_cumulative_rain(self):
        return self.cumulative_rain

    def curvetype2(self, t):
        r"""
        Uses Cronshey/Norman (1981) equation to estimate the ordinate value
        (P/P24) of the SCS Type Curves II and III in a 24 hour storm.

        Parameters
        ----------
        t : float
            The time of the ordinate, in hours (from 0 up to 24)

        Returns
        -------
        Pt : float
            The ordinate P(t)/P24 corresponding to time t
            
        Notes
        -----
        Equation 3.6 from _[1]:
           
        .. math:: \frac{P(t)}{P_{24}} = 0.5 + \frac{T}{24} \left[ \frac{24.04}{2\abs{T} + 0.04 \right]


        where :math:`t` is time and :math:`Τ` is :math:`time - 12` in hours.
        
        References
        ----------
      
        .. [1] O. Haan, C. T., Barfield, B. J., & Hayes, J. C. (1994).
            Chapter 03 Rainfall-Runoff Estimation in Storm Water Computations.
            In Design Hydrology and Sedimentology for Small Catchments
            (pp. 37–103). https://doi.org/10.1016/b978-0-08-057164-5.50007-4

        """
        T = t-12
        Pt = 0.5 + (T / 24) * pow(24.04 / (2 * abs(T) + 0.04), 0.75)
        return Pt
    
    def scs_curve(self):
        """Creates a dimensionless rainfall temporal pattern for
        SCS Type Curves II and III
        """
        ini, end = 12-self.duration/2., 12+self.duration/2.
    
        if ini < 0: ini = 0
        if end > 24: end = 24  # SCS is based on the 24-hr rainfall
        
        # Generate a list of time steps and their corresponding ordinate P/P24
        self.time = [x/100 for x in range(int(ini*100),
                                          int((end+self.step)*100),
                                          int(self.step*100))]
        self.pt = [self.curvetype2(t) for t in self.time]
        
        return self.time, self.pt
    
    def scs_table(self):
        """Returns a string representation of the SCS Type Curve"""
        text = ""
        text += "SCS Curve Types II and III\n"
        text += "    Time    P/P24 \n"
        for (t, p) in zip(self.time, self.pt):
            text += "{:-8.2f} {:-8.4f}\n".format(t, p)
        return text

    def generate_hyetograph(self):
        """Generate the hyetograph"""
        self.cumulative_rain.clear()
        self.hyetograph.clear()
        
        # Calculate the cumulative rain for each time step
        for Pt in self.pt:
            rain = self.rainfall * ((Pt - self.pt[0])/(self.pt[-1] - self.pt[0]))
            self.cumulative_rain.append(rain)
        
        if len(self.cumulative_rain) == 0:
            return
        
        # Get the rainfall intervals (hyetograph) from the cumulativa rainfall
        self.hyetograph.append(self.cumulative_rain[0])
        for i in range(1, len(self.cumulative_rain)):
            self.hyetograph.append(self.cumulative_rain[i] - self.cumulative_rain[i-1])

        # Update the string representation
        self.str += self.table_hyetograph()
        
    def table_hyetograph(self):
        """Returns a string representation of the hyetograph"""
        text = ""
        text += " Start time: {}\n End time: {}\n Time step: {}\n".format(
                self.time[0], self.time[-1], self.step)
        text += "SCS Curve Types II and III\n\n"
        text += " {:8}  {:8} {:8} {:8}\n".format(self.headers[0], self.headers[1], self.headers[2], self.headers[3])
        for (t, p, cr, r) in zip(self.time, self.pt, self.cumulative_rain, self.hyetograph):
            text += "{:-8.2f} {:-8.4f} {:-8.4f} {:-8.4f}\n".format(t, p, cr, r)

        return text
    
    def plot_curve(self, title="", filename=""):
        fig_curve = plt.figure(figsize=(16, 9))
        plt.plot(self.time, self.pt)
        
        if title == "":
            title = "SCS Curve Type II (and III)"
        plt.title(title)
        plt.xlabel("Time (hours)")
        plt.ylabel("P/P24")
        
        if filename != "":
            plt.savefig(filename, bbox_inches='tight', dpi=300, transparent=True)
        fig_curve.show()
    
    def plot_hyetograph(self, title="", filename=""):
        w = 0.2
        if (len(self.hyetograph) <= 12):
            w=0.3
        fig_hyeto = plt.figure(figsize=(16, 9))
        plt.bar(self.time, self.hyetograph, align='edge', width=w)
         
        if title == "":
            title = "Synthetic rainfall hyetograph"
        plt.title(title)
        plt.xlabel("Time (hours)")
        plt.ylabel("Rainfall (" + self.rainunits + ")")
        
        if filename != "":
            plt.savefig(filename, bbox_inches='tight', dpi=300, transparent=True)
        fig_hyeto.show()
    
    def save_hyetograp(self, filename):
        with open(filename, 'w') as f:
            write = csv.writer(f)
            write.writerow(self.headers)
            for (t, p, cr, r) in zip(self.time, self.pt, self.cumulative_rain, self.hyetograph):
                write.writerow([t, p, cr, r])
   
if __name__ == "__main__":
    #  Create a new storm, example 3.5
    PD = 6.8  # inches of rain, 25-yr return period
    D = 3  # duration in hours
    ts = 0.25  # time step of hyetograph 

    # #  Create a new storm, example 3.5
    # PD = 4.55  # inches of rain, 25-yr return period
    # D = 6  # duration in hours
    # ts = 1  # time step of hyetograph 
    
#    # Storm from HW#1 Problem 1
#    PD = 3.27  # inches of rain, 25-yr return period
#    D = 5  # duration in hours
#    ts = 0.5  # time step of hyetograph
    
#    # Storm x
#    PD = 3.27  # inches of rain, 25-yr return period
#    D = 24  # duration in hours
#    ts = 0.25  # time step of hyetograph
    
    storm = SCSStorm(PD, D, ts, SI=False)
    storm.plot_curve()
    storm.plot_hyetograph("Hyetograph {0}")
    storm.save_hyetograp("../examples/scs_example.csv")
    print(storm)


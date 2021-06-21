#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 01:09:48 2021
@author: eduardo

lateral: Design of laterals for sprinkler irrigation 

This program is aimed for designing a single lateral for sprinkler irrigation
systems. It was developed using the class notes from the Irrigation Department
of Universidad Autonoma Chapingo, Mexico.
"""

from math import sqrt

class Lateral:
    def __init__(self, sprinkler_flow, sprinkler_pressure, 
                 sprinkler_wet_diameter, length, slope, sprinkler_separation,
                 lateral_separation, first_sprinkler, inclination, equation,
                 coefficient):
        """
        Design of laterals for sprinkler irrigation.

        Parameters
        ----------
        sprinkler_flow : TYPE
            Operational flow rate of the sprinkler, liters per second.
        sprinkler_pressure : TYPE
            Operational pressure of the sprinkler, kg/cm2.
        sprinkler_wet_diameter : TYPE
            Wet diameter of the sprinkler, meters.
        length : TYPE
            Length that the lateral should cover, meters.
        slope : TYPE
            Slope in lateral direction, m/m (dimensionless).
        sprinkler_separation : TYPE
            Separation between sprinkerls in the lateral, meters.
        lateral_separation : TYPE
            Separation between laterals, meters.
        first_sprinkler : TYPE
            Condition if first sprinker is at same or half separation than
            others, 'True' = half separation and 'False' = normal separation.
        inclination : TYPE
            Inclination of the slope in the direction of the lateral, 
            0 = flat, 1 = upward, 2 = downward
        equation : int
            The selected equation for hidraulic head loss calculation
            0 = Hazen-Williams, 1 = Manning, 2 = Scobey
        coefficient : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        # self.F = 0.365
#        self.ks = 0.4
#        self.C = 130
#        self.n = 0.009
        
        # initialize all the coefficients
        self.ks = coefficient # Scobey coefficient
        self.C = coefficient  # Hazen-Williams coefficient
        self.n = coefficient  # Manning roughtness coefficient
        self.he = 1 
        
        # Asignar las variables de inicio para realizar calculos
        self.q = sprinkler_flow
        self.ho = 10 * sprinkler_pressure # Para convertir y trabajar en mca
        self.lt = length
        self.s = slope
        self.sa = sprinkler_separation
        self.sl = lateral_separation
        self.dm = sprinkler_wet_diameter
        self.fsep = first_sprinkler     # First sprinkler separation
        self.inc = inclination
        self.eq = equation

        self.diametros = [2, 3, 4, 5, 6, 8, 10, 12]
    
    def design_lateral(self):
        
        # Calcular el traslape
        #traslape = 100 * (self.sa / self.dm)
        
        # Numero de aspersores
        if self.fsep is True:
            # Primer aspersor a la mitad de la separacion entre aspersores
            self.Nasp = int((self.lt - self.sa/2) / self.sa) + 1
        elif self.fsep is False:
            # Primer aspersor a la misma separacion entre aspersores
            self.Nasp = int((self.lt - self.sa/2) / self.sa)
        
        # Obtener pérdida por fricción permisible
        if self.inc == 0:
            # Flat slope
            hf_perm = 0.2 * self.ho
        elif self.inc == 1:
            # Upward slope
            hf_perm = (0.2 * self.ho) - (self.s * self.lt)/100
        elif self.inc == 2:
            # Downward slope
            hf_perm = (0.2 * self.ho) + (self.s * self.lt)/100
            
        # Obtener el gasto del lateral (lps) --> m3/s
        Q = (self.q * self.Nasp)/1000
        self.Ql = self.q * self.Nasp
            
        # Para cada diámetro obtener las pérdidas y comparar con HF permisible
        # Parar hasta que HF < HF permisible
        J = 0.
        #d = 0.
        i = 0
        self.hf = 2000
        while (self.hf > hf_perm):
            d = (self.diametros[i] * 0.0254)
            
            # Calcular las pérdidas por fricción
            # Usando la ecuación que seleccionada

            if self.eq == 0:
                # wx.MessageBox('Hazen-Williams seleccionado')
                J = 10.648 * pow(( 1. / self.C), 1.852) * ( pow( Q, 1.852) / pow( d, 4.871))
                m = 1.852
            elif self.eq == 1:
                # wx.MessageBox('Manning seleccionado')
                J = 10.29 * pow( self.n, 2.) * ( pow( Q, 2.) / pow( d, (16. / 3.) ) )
                m = 2.0
            elif self.eq == 2:
                # wx.MessageBox('Scobey seleccionado')
                J = 0.00409379 * self.ks * pow(d,-4.9)* pow(Q, 1.9)
                m = 1.9

            # Calculo de F de Christiansen
            if self.fsep is True:
                # wx.MessageBox('Primer aspersor a la mitad de separación que Sa')
                for j in range(self.Nasp):
                    suma = pow((self.Nasp - (j + 1)), m)
                self.F = 1. / (2. * self.Nasp - 1.) + 2. / ((2.* self.Nasp - 1) * pow(self.Nasp, m)) * suma
                self.Llat = (self.Nasp - 1) * self.sa + (self.sa / 2)
                
            elif self.fsep is False:
                # wx.MessageBox('Primer aspersor a la misma separación que Sa')
                self.F = (1. / (m + 1.)) + (1. / (2. * self.Nasp)) + (sqrt(m - 1.) / (6. * pow(self.Nasp, 2.)))
                # Longitud real del lateral para este caso
                self.Llat = self.Nasp * self.sa
            
            # Calculate pressure drop
            self.hf = J * self.F * self.Llat
            i += 1
            
        self.d_in = self.diametros[i]
        
        # Obtener la carga de entrada del lateral
        self.Hl = self.ho + (0.75 * self.hf) + self.he + ((0.5 * self.s * self.Llat) / 100) + (0.1 * self.ho)
        
    def get_diameter(self):
        
        return self.d_in
        
    def get_pressure(self):
        
        return self.Hl
        
    def get_flow(self):
        
        return self.Ql
        
    def get_lenght(self):
        
        return self.Llat
        
    def get_number_sprinklers(self):
        
        return self.Nasp
        
    def get_pressure_drop(self):
        
        return self.hf
        
    def get_permisive_drop(self):
        
        return self.F
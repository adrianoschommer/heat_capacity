# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 09:55:43 2021

@author: Adriano Schommer
"""

from DataParse import *
from DataSection import *
import pandas as pd


from scipy.optimize import least_squares
import numpy as np

#-----------------------------NO_FAN----------------------------------

raw_data = pd.DataFrame(DataParse().read_file(0))
raw_data = DataParse().add_temperature_channels(raw_data, 151, 1)
#INITIAL_CUTOFF = 27840
# File 0:
#INITIAL_CUTOFF = 24150
test_data = DataParse().set_test_data(raw_data, 20)
DataParse().plot_test_data(test_data)
AVG_Q_GEN = DataParse().calculate_AVG_Q_GEN(test_data, 3.82)
final_section_data = DataSection().set_final_section(test_data, 0.3)
R_OUT_no_fan = DataSection().calculate_R_OUT(final_section_data, AVG_Q_GEN)
DataSection().plot_final_section(final_section_data)
AVG_SURFACE_TEMP = DataSection().calculate_AVG_SURFACE_TEMP(final_section_data)
## if you calculate AVG_Q_GEN only from the final data you get lower values
AVG_Q_GEN = DataParse().calculate_AVG_Q_GEN(final_section_data, 3.82)
initial_section_data = DataSection().set_initial_section(
    test_data, 0.93, AVG_SURFACE_TEMP)
DataSection().plot_initial_section(initial_section_data)
ys = initial_section_data['surface_temp_filtered']
#ys = initial_section_data['Aux_Temperature_1(C)']
opt_result_no_fan = DataSection().optimize_equation(ys, initial_section_data,
                           AVG_Q_GEN, R_OUT_no_fan, plot=True)
DENOMINATOR = 360  # Cp(RIN + ROUT)
calculated_surface_temp = DataSection().calculate_surface_temp(
    DENOMINATOR, initial_section_data, AVG_Q_GEN, R_OUT_no_fan)

#-----------------------------FAN-----------------------------------

raw_data = pd.DataFrame(DataParse().read_file(1))
raw_data = DataParse().add_temperature_channels(raw_data, 151, 1)
#INITIAL_CUTOFF = 27840
# File 0:
#INITIAL_CUTOFF = 24150
test_data = DataParse().set_test_data(raw_data, 20)
DataParse().plot_test_data(test_data)
AVG_Q_GEN = DataParse().calculate_AVG_Q_GEN(test_data, 3.82)
final_section_data = DataSection().set_final_section(test_data, 0.3)
R_OUT_fan = DataSection().calculate_R_OUT(final_section_data, AVG_Q_GEN)
DataSection().plot_final_section(final_section_data)
AVG_SURFACE_TEMP = DataSection().calculate_AVG_SURFACE_TEMP(final_section_data)
## if you calculate AVG_Q_GEN only from the final data you get lower values
AVG_Q_GEN = DataParse().calculate_AVG_Q_GEN(final_section_data, 3.82)
initial_section_data = DataSection().set_initial_section(
    test_data, 0.93, AVG_SURFACE_TEMP)
DataSection().plot_initial_section(initial_section_data)
ys = initial_section_data['surface_temp_filtered']
#ys = initial_section_data['Aux_Temperature_1(C)']
opt_result_fan = DataSection().optimize_equation(ys, initial_section_data,
                           AVG_Q_GEN, R_OUT_fan, plot=True)



R_OUT = [R_OUT_no_fan, R_OUT_fan]
optimized_parameters = [opt_result_no_fan, opt_result_fan]

heat_capacity = DataSection().calculate_heat_capacity(R_OUT, optimized_parameters)
specific_heat_capacity = heat_capacity[0][0]/0.114
print(specific_heat_capacity)
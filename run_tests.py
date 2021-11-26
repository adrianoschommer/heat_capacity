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

raw_data = pd.DataFrame(DataParse().read_file(0))
raw_data = DataParse().add_filtered_temp(raw_data, 131, 1)
#INITIAL_CUTOFF = 27840
# File 0:
#INITIAL_CUTOFF = 24150

test_data = DataParse().set_test_data(raw_data, 24150)
#DataParse().plot_test_data(test_data)

AVG_Q_GEN = DataParse().calculate_AVG_Q_GEN(test_data, 3.82)
final_section_data = DataSection().set_final_section(test_data, 0.3)
R_OUT = DataSection().calculate_R_OUT(final_section_data, AVG_Q_GEN)
#DataSection().plot_final_section(final_section_data)
AVG_SURFACE_TEMP = DataSection().calculate_AVG_SURFACE_TEMP(final_section_data)

## if you calculate AVG_Q_GEN only from the final data you get lower values
AVG_Q_GEN = DataParse().calculate_AVG_Q_GEN(final_section_data, 3.82)


initial_section_data = DataSection().set_initial_section(
    test_data, 0.95, AVG_SURFACE_TEMP)
DataSection().plot_initial_section(initial_section_data)
ys = initial_section_data['surface_temp_filtered']
#ys = initial_section_data['Aux_Temperature_1(C)']
#time_data = initial_section_data['Test_Time(s)']
opt_result = DataSection().optimize_equation(ys, initial_section_data,
                           AVG_Q_GEN, R_OUT)


DENOMINATOR = 360  # Cp(RIN + ROUT)

calculated_surface_temp = DataSection().calculate_surface_temp(
    DENOMINATOR, ys, initial_section_data, AVG_Q_GEN, R_OUT)

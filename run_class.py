# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 09:55:43 2021

@author: Adriano Schommer
"""


from class_helpers import DataParse, DataSection
import pandas as pd


from scipy.optimize import least_squares
import numpy as np

raw_data = pd.DataFrame(DataParse().read_file(0))

#INITIAL_CUTOFF = 27840
# File 0:
#INITIAL_CUTOFF = 24150

test_data = DataParse().set_test_data(raw_data, 24150)
#DataParse().plot_test_data(test_data)
test_data = DataParse().add_filtered_data(test_data, 131, 1)
AVG_Q_GEN = DataParse().calculate_AVG_Q_GEN(test_data, 3.82)
final_section_data = DataSection().set_final_section(test_data, 0.3)
R_OUT, AVG_SURFACE_TEMP, AVG_AMBIENT_TEMP = DataSection(
    ).calculate_section_final(final_section_data, AVG_Q_GEN)
#DataSection().plot_final_section(section_final_data)


## if you calculate AVG_Q_GEN only from the final data you get lower values
AVG_Q_GEN = DataParse().calculate_AVG_Q_GEN(final_section_data, 3.82)


initial_section_data = DataSection().set_initial_section(
    test_data, 0.95, AVG_SURFACE_TEMP, AVG_AMBIENT_TEMP)
#DataSection().plot_initial_section(initial_section_data)

DataSection().least_squares_optimization(initial_section_data,
                           AVG_Q_GEN, R_OUT, AVG_AMBIENT_TEMP)

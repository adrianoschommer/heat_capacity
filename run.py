# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 09:05:51 2021

@author: Adriano Schommer
"""




from helpers import *

data = read_file(0)

data = select_test_data(data, True)

data = add_filtered_data(data, 631, 1)

data['Q_gen'] = Q_gen(data, True)

data_section_final, Ts_mean, R_out = section_final(data, True)

data_section_initial = section_initial(data, 0.95, Ts_mean, True)

optimize(data_section_initial, R_out)
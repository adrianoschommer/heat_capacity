# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 09:55:19 2021

@author: Adriano Schommer
"""

import glob
import pandas as pd
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import numpy as np

class TestData():

    def __init__(self):
        self.files = glob.glob('data\\*.xlsx')

    def read_file(self, *select_file):
        if isinstance(self.select_file, int):
            self.select_file = select_file 
        else:
            for i in range(len(self.files)):
                print('file ' + str(i) + ' ' + str(self.files[i]))
            select_file = input('enter the number of the file you want to load: \n')
        data = pd.read_excel(self.files[int(select_file)], sheet_name=1)
        print(str(self.files[int(select_file)]) + ' successfully loaded')
        return data
            
        
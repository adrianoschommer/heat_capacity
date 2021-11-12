# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 10:32:07 2021

@author: Adriano Schommer
"""

import glob
import pandas as pd
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import numpy as np


def read_file(index):

    files = glob.glob('data\\*.xlsx')
    if index == index:
        select_file = index
    else:
        for i in range(len(files)):
            print('file ' + str(i) + ' ' + str(files[i]))
            select_file = input('enter the number of the file you want to load: \n')
    data = pd.read_excel(files[int(select_file)], sheet_name=1)
    print(str(files[int(select_file)]) + ' successfully loaded')
    return data


def select_test_data(data, plot):

    # data = data[(data['Test_Time(s)'] > 27840)]
    data = data[(data['Test_Time(s)'] > 24150)]
    if plot:
        fig, ax1 = plt.subplots(figsize=(7,4))
        ax1.plot(data['Test_Time(s)'], data['Voltage(V)'], 
                 label='Voltage [V]')
        ax2=ax1.twinx()
        ax2.plot(data['Test_Time(s)'], data['Current(A)'], 
                 label='Current [A]', color='r')
        ax2.set_ylim([35,-50])
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)
        ax1.set_ylabel('Voltage [V]')
        ax2.set_ylabel('Current [A]')
        ax1.set_xlabel('Running test time [s]')
        ax1.grid()
    else:
        return       
    return data


def add_filtered_data(data, rolling_window, poly_fit):

    Ts_1 = data['Aux_Temperature_1(C)']
    Ts_2 = data['Aux_Temperature_2(C)']
    Ta = data['Aux_Temperature_3(C)']
    data['Ts_filtered'] = savgol_filter((Ts_1 + Ts_2)/2,
                                        rolling_window, poly_fit)
    data['Ta_filtered'] = savgol_filter(Ta, rolling_window, poly_fit)
    return data


def Q_gen(data, plot):

    OCV = 3.82
    df = pd.DataFrame()
    df['Q_gen'] = abs((data['Voltage(V)'] - OCV) * data['Current(A)'])
    df['Q_gen_mean'] = df['Q_gen'].mean()
    print('average_Qgen =', round(df['Q_gen'].mean(),3))
    if plot:
        fig, ax1 = plt.subplots(figsize=(7,4))
        ax1.plot(data['Test_Time(s)'], df['Q_gen'], 
                 label='Calculated $\dot{Q}_{gen}$')
        ax1.set_ylabel('$\dot{Q}_{gen} [W]$')
        ax1.set_xlabel('$Running test time [s]$')
        ax1.plot(data['Test_Time(s)'], df['Q_gen_mean'], 
                 label='Average $\dot{Q}_{gen}=$'+ str(round(df['Q_gen'].mean(),2)) + 'W')
        plt.legend(loc = 'upper right')
        ax1.grid()
    else:
        return       
    return df['Q_gen']


def section_final(data, plot):
    data_section_final = data.copy()
    sample_size = int(len(data)/3)
    data_section_final = data_section_final.iloc[-sample_size:]
    
    Ts_1 = data_section_final['Aux_Temperature_1(C)']
    Ts_2 = data_section_final['Aux_Temperature_2(C)']
    Ta = data_section_final['Aux_Temperature_3(C)']
    Test_Time = data_section_final['Test_Time(s)']
    
    data_section_final['Ts_mean'] = ((Ts_1 + Ts_2)/2).mean()
    data_section_final['Ta_mean'] = Ta.mean()
    Ts_mean = data_section_final['Ts_mean']
    Ta_mean = data_section_final['Ta_mean']
    Ts_filtered = data_section_final['Ts_filtered']
    Ta_filtered = data_section_final['Ta_filtered']
    
    #data_section_final['R_out'] = ((Ts_1 + Ts_2)/2 - Ta) / data['Q_gen']
    R_out = ((Ts_mean - Ta.mean()) / data['Q_gen'].mean()).iloc[0]
    #R_out = data_section_final['R_out'].mean()
    print('R_out = ' + str(round(R_out,2)))
    
    if plot:
        fig, ax1 = plt.subplots(figsize=(7,7))
    
        scatter_size = 0.5
        ax1.scatter(Test_Time, Ts_1, label='Surface (Thermocouple 1)', s=scatter_size)
        ax1.scatter(Test_Time, Ts_2, label='Surface (Thermocouple 2)', s=scatter_size)
        ax1.scatter(Test_Time, Ta, label='Ambient Temperature', s=scatter_size)
        
        ax1.plot(Test_Time, Ts_mean, label='Average Surface Temp =' + str(round(Ts_mean.mean(),2)))
        ax1.plot(Test_Time, Ta_mean, label='Average Ambient Temp =' + str(round(Ta_mean.mean(),2)))
        ax1.plot(Test_Time, Ts_filtered, label='Filtered Surface Temp (Savitzky–Golay)')
        ax1.plot(Test_Time, Ta_filtered, label='Filtered Ambient Temp (Savitzky–Golay)')
        
        print('Average Surface Temp = ' + str(round(Ts_mean.mean(),2)))
        print('Average Ambient Temp = ' + str(round(Ta_mean.mean(),2)))
  
        ax1.legend(loc=0)
        ax1.set_ylabel('Temperature [°C]')
        ax1.set_xlabel('Time [s]')
        ax1.grid()
    else:
        return       
    return data_section_final, Ts_mean, R_out


def section_initial(data, cutoff_factor, Ts_mean, plot):
    data_section_initial = data.copy()
    Ts_1 = data_section_initial['Aux_Temperature_1(C)']
    Ts_2 = data_section_initial['Aux_Temperature_2(C)']
    Ta = data_section_initial['Aux_Temperature_3(C)']
    cutoff = Ta.mean() + cutoff_factor*(Ts_mean - Ta.mean()).iloc[0]
    data_section_initial = data_section_initial[(data_section_initial['Ts_filtered']<cutoff)]
    print('cutoff temperature = ' + str(round(cutoff,3)))
    
    if plot:
        fig, ax1 = plt.subplots(figsize=(7,4))
        ax1.plot(data_section_initial['Test_Time(s)'], data_section_initial['Aux_Temperature_3(C)'], 
                 label='Ambient', color='r')
        ax1.plot(data_section_initial['Test_Time(s)'], data_section_initial['Aux_Temperature_1(C)'],
                 label='Surface (Thermocouple 1)')
        ax1.plot(data_section_initial['Test_Time(s)'], data_section_initial['Aux_Temperature_2(C)'],
                 label='Surface (Thermocouple 2)')
        ax1.plot(data_section_initial['Test_Time(s)'], data_section_initial['Ts_filtered'],
                 label='Filtered Surface Temp (Savitzky–Golay)')       
        ax1.legend(loc=0)
        ax1.set_ylabel('Temperature [°C]')
        ax1.set_xlabel('Test_Time(s)')
        ax1.grid()
    else:
        return
    return data_section_initial
    
def optimize(data, R_out):
    Q_gen = data['Q_gen'].mean()
    Ta = data['Aux_Temperature_3(C)'].mean()
    time_data = data['Test_Time(s)']

    def y(t, Ts_initial, theta):
        Ts = []
        Ts.append(Ts_initial)
        for i in range(len(t)-1):  
                 
            Ts_n = (((Q_gen*R_out + Ta - Ts[-1])*(time_data.iloc[i+1] - time_data.iloc[i]))/
                    (theta[0])) + Ts[-1]
                   
            Ts.append(Ts_n)
        return Ts

    ts = np.array(data['Test_Time(s)'])
    #ys = data_section_initial['Aux_Temperature_1(C)']
    ys = data['Ts_filtered']
    
    def fun(theta):
        return y(ts, Ts_initial, theta) - ys
    
    theta0 = [106]
    Ts_initial = data['Ts_filtered'].iloc[0]
    res1 = least_squares(fun, theta0)
    
    fig, ax1 = plt.subplots(figsize=(7,4))
    ax1.plot(ts, res1.fun+ys, label = 'fitted least squares')
    ax1.plot(ts, ys, label = 'surface temp (filtered) \n' +
             str('Cp(Rin + Rout) = ' + str(round(res1.x[0], 2))))
    ax1.set_ylabel('Temperature [°C]')
    ax1.set_xlabel('Time (s)')
    ax1.legend()
    ax1.grid()
    
    print('Cp(Rin + Rout) = ' + str(round(res1.x[0], 2)))
    #print('Rin = ' + str(round(res1.x[1], 2)))
    #print('Cp(Rin + Rout)= ' + str(round(res1.x[0] * (res1.x[1] + Rout), 2)))
    print('Ta = ' + str(round(Ta,2)))
    print('Qgen = ' + str(round(Q_gen,2)))
    print('Rout = ' + str(round(R_out,2)))
    print('TS_initial_guess = ' + str(round(Ts_initial,2)))

    

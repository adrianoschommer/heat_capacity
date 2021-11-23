# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 09:05:51 2021

@author: Adriano Schommer
"""




from helpers import *

# =============================================================================
# data = read_file(0)
# 
# data = select_test_data(data, True)
# 
# data = add_filtered_data(data, 631, 1)
# 
# data['Q_gen'] = Q_gen(data, True)
# 
# data_section_final, Ts_mean, R_out = section_final(data, True)
# 
# data_section_initial = section_initial(data, 0.95, Ts_mean, True)
# 
# optimize(data_section_initial, R_out)
# =============================================================================



def RMSE():
    A = []
    i = -1
    for k in range(100,800,500):
        i = i+1
        data = read_file(0)
        data = select_test_data(data, True)
        data = add_filtered_data(data, k+1, 1)
        data['Q_gen'] = Q_gen(data, True)
        data_section_final, Ts_mean, R_out = section_final(data, True)
        data_section_initial = section_initial(data, 0.95, Ts_mean, True)
        A.append(optimize(data_section_initial, R_out))
        #RMSE.append(np.sqrt(np.mean((A - data_section_initial)**2)))
        #if RMSE[i] < RMSE[i-1]:
        #    info.append('min RMSE = ' + str(round(RMSE[i],4)) + '\n' + 'A = ' + str(A))
    return A, data_section_initial
A, data_section_initial = RMSE()


def Ts(A, Ta, Ts_initial, Qgen, Rout, t):
    Ts = []
    Ts.append(Ts_initial)
    for i in range(len(t)-1):      
        Ts_n = (((Qgen*Rout + Ta - Ts[-1])*(time_data.iloc[i+1] - time_data.iloc[i]))/(A) + Ts[-1])
        Ts.append(Ts_n)
    return Ts

Ts_data = data_section_initial['Aux_Temperature_1(C)'] 
Ts_data = data_section_initial['Ts_filtered']
time_data = data_section_initial['Test_Time(s)']
time = range(len(Ts_data))    

Ta = 25.55
Ts_initial = Ts_data.iloc[0]
Qgen = 1.33
Rout = 2.77
RMSE = []
info = []
i = -1

for k in A:
    i = i+1
    x = Ts(k, Ta, Ts_initial, Qgen, Rout, time_data)
    RMSE.append(np.sqrt(np.mean((x - Ts_data)**2)))
    if RMSE[i] < RMSE[i-1]:
        info.append('min RMSE = ' + str(round(RMSE[i],4)) + '\n' + 'A = ' + str(A))
    plt.plot(time_data, x, color='grey')
    plt.plot(time_data, Ts_data, color='r')
plt.ylabel('Surface Temp [°C]')
plt.xlabel('Time [s]')
    
#print(info[-1])



















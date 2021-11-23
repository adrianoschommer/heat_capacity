# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 09:55:19 2021

@author: Adriano Schommer
"""

class DataParse():
        
    def __init__(self):
        import glob
        self.files = glob.glob('data\\*.xlsx')

    def read_file(self, select_file=None):
        """
        Loads .xlsx ARBIN LBT21084 cell tester data to a pd.DataFrame

        Parameters
        ----------
        select_file : int, optional
            index of the file to read. If none is given, it prompts the user
            to select a file from the target foler 'data'.

        Returns
        -------
        data : pd.DataFrame
            raw data from the ARBIN .xlxs
        """
        import pandas as pd
        self.select_file = select_file
        if isinstance(select_file, int):
            select_file = select_file
        else:
            print('else loop')
            for i in range(len(self.files)):
                print('file ' + str(i) + ' ' + str(self.files[i]))
            select_file = input('enter the number of the file '
                                + 'you want to load: \n')
        data = pd.read_excel(self.files[int(select_file)], sheet_name=1)
        print(str(self.files[int(select_file)]) + ' successfully loaded')
        return data

    def set_test_data(self, raw_data, INITIAL_CUTOFF):
        """
        Cut raw data from the beggining of the test to the end of raw data

        Parameters
        ----------
        raw_data : pd.DataFrame
            data from read_file method
        INITIAL_CUTOFF : int
            Test_time(s) from which the data is cut

        Returns
        -------
        test_data : pd.DataFrame
            cycle test window from the cutoff time to the end of raw data

        """
        self.raw_data = raw_data
        self.INITIAL_CUTOFF = INITIAL_CUTOFF
        test_data = raw_data[(raw_data['Test_Time(s)'] > INITIAL_CUTOFF)]
        test_data.reset_index(drop=True, inplace=True)  # Reset index
        return test_data

    def plot_test_data(self, test_data):
        """
        Plots voltage and current vs test time

        Parameters
        ----------
        test_data : pd.DataFrame
            cycle test window from set_test_data method

        """
        import matplotlib.pyplot as plt
        self.test_data = test_data
        fig, ax1 = plt.subplots(figsize=(7, 4))
        ax1.plot(test_data['Test_Time(s)'], test_data['Voltage(V)'],
                 label='Voltage [V]')
        ax2 = ax1.twinx()
        ax2.plot(test_data['Test_Time(s)'], test_data['Current(A)'],
                 label='Current [A]', color='r')
        ax2.set_ylim([35, -50])
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)
        ax1.set_ylabel('Voltage [V]')
        ax2.set_ylabel('Current [A]')
        ax1.set_xlabel('Running test time [s]')
        ax1.grid()

    def add_filtered_data(self, test_data, rolling_window, poly_fit):
        """
        Adds two columns to test_data containing surface
        and ambient temperatures filtered by a Savitzky–Golay filter

        Parameters
        ----------
        test_data : pd.DataFrame
            test_data from set_test_data method
        rolling_window : int
            must be odd, rolling window for the Savitzky–Golay filter
        poly_fit : int
            polynomial order for the Savitzky–Golay filter

        Returns
        -------
        test_data : pd.DataFrame
            test_data with two columns added:
            - surface_temp_filtered
            - ambient_temp_filtered

        """
        from scipy.signal import savgol_filter
        self.test_data = test_data
        #  avoid SettingWithCopyWarning by making it indepent:
        test_data = test_data.copy()
        surface_temp_1 = test_data['Aux_Temperature_1(C)']  # Thermocouple 01
        surface_temp_2 = test_data['Aux_Temperature_2(C)']  # Thermocouple 02
        ambient_temp = test_data['Aux_Temperature_3(C)']    # Thermocouple 03
        test_data['surface_temp_filtered'] = savgol_filter(
            (surface_temp_1 + surface_temp_2) / 2, rolling_window, poly_fit)
        test_data['ambient_temp_filtered'] = savgol_filter(
            ambient_temp, rolling_window, poly_fit)
        return test_data

    def calculate_AVG_Q_GEN(self, data, OCV):
        """
        Calculates the averaged heat generated in a given charge/discharge
        cycle in [W]

        Parameters
        ----------
        data : pd.DataFrame
            voltage and current data from a charge/discharge cycle
        OCV : int
            open-circuit voltage in volts

        Returns
        -------
        Q_GEN : float
            Average heat generated Q_GEN [W]

        """
        self.data = data
        self.OCV = OCV
        AVG_Q_GEN = abs((data['Voltage(V)'] - OCV) * data['Current(A)']).mean()
        print('average Q_GEN =', round(AVG_Q_GEN, 3))
        return AVG_Q_GEN


class DataSection():

    def set_final_section(self, test_data, PROPORTIONAL_CUTOFF):
        """
        Defines final section length as a proportion of test_data length.
        E.g. if PROPORTIONAL_CUTOFF = 0.33, the last 1/3 of data
        will be the final section considered. If it was 0.5, 1/2 of test-data
        would be set as final section.

        Parameters
        ----------
        test_data : pd.DataFrame
            test_data from set_test_data method
        PROPORTIONAL_CUTOFF : int
            proportional length of final_section in relation to test_data

        Returns
        -------
        final_section_data : pd.DataFrame
            final section of test_data

        """
        self.test_data = test_data
        self.PROPORTIONAL_CUTOFF = PROPORTIONAL_CUTOFF
        #  avoid SettingWithCopyWarning by making it indepent:
        final_section_data = test_data.copy()
        SAMPLE_SIZE = int(len(test_data)*PROPORTIONAL_CUTOFF)
        final_section_data = final_section_data.iloc[-SAMPLE_SIZE:]
        return final_section_data

    def plot_final_section(self, section_final_data):
        """
        Plots a scatter of raw thermocouple data and a solid line of
        average ambient and surface temperatures

        Parameters
        ----------
        section_final_data : pd.DataFrame
            pd from set_final_section method

        """
        import matplotlib.pyplot as plt
        self.section_final_data = section_final_data
        fig, ax1 = plt.subplots(figsize=(7, 7))
        scatter_size = 0.5
        # Thermocouple 01:
        surface_temp_1 = section_final_data['Aux_Temperature_1(C)']
        # Thermocouple 02:
        surface_temp_2 = section_final_data['Aux_Temperature_2(C)']
        # Thermocouple 03:
        ambient_temp = section_final_data['Aux_Temperature_3(C)']
        Test_Time = section_final_data['Test_Time(s)']
        section_final_data['avg_surface_temp'] = (
            (surface_temp_1 + surface_temp_2)/2).mean()
        AVG_SURFACE_TEMP = section_final_data['avg_surface_temp']
        section_final_data['avg_ambient_temp'] = ambient_temp.mean()
        AVG_AMBIENT_TEMP = section_final_data['avg_ambient_temp']
        ax1.scatter(Test_Time, surface_temp_1,
                    label='Surface (Thermocouple 1)', s=scatter_size)
        ax1.scatter(Test_Time, surface_temp_2,
                    label='Surface (Thermocouple 2)', s=scatter_size)
        ax1.scatter(Test_Time, ambient_temp,
                    label='Ambient Temperature', s=scatter_size)
        ax1.plot(Test_Time, AVG_SURFACE_TEMP,
                 label='Average Surface Temp ='
                 + str(round(AVG_SURFACE_TEMP.mean(), 2)))
        ax1.plot(Test_Time, AVG_AMBIENT_TEMP,
                 label='Average Ambient Temp ='
                 + str(round(AVG_AMBIENT_TEMP.mean(), 2)))
        ax1.legend(loc=0)
        ax1.set_ylabel('Temperature [°C]')
        ax1.set_xlabel('Time [s]')
        ax1.grid()

    def calculate_section_final(self, final_section_data, AVG_Q_GEN):
        """
        Calculates external thermal resistance and average surface and
        ambient temperatures.

        Parameters
        ----------
        final_section_data : pd.DataFrame
            pd from set_final_section method
        AVG_Q_GEN : int
            AVG_Q_GEN from calculate_AVG_Q_GEN method

        Returns
        -------
        R_OUT : int
            External thermal resistance [K/W]
        AVG_SURFACE_TEMP : int
            average surface temperature [K]
        AVG_SURFACE_TEMP : int
            average ambient temperature [K]

        """
        self.final_section_data = final_section_data
        self.AVG_Q_GEN = AVG_Q_GEN
        # Thermocouple 01:
        surface_temp_1 = final_section_data['Aux_Temperature_1(C)']
        # Thermocouple 02:
        surface_temp_2 = final_section_data['Aux_Temperature_2(C)']
        # Thermocouple 03:
        ambient_temp = final_section_data['Aux_Temperature_3(C)']
        AVG_SURFACE_TEMP = ((surface_temp_1 + surface_temp_2)/2).mean()
        AVG_AMBIENT_TEMP = ambient_temp.mean()
        R_OUT = (AVG_SURFACE_TEMP - AVG_AMBIENT_TEMP) / AVG_Q_GEN
        print('R_OUT = ' + str(round(R_OUT, 3)))
        print('AVG_SURFACE_TEMP = ' + str(round(AVG_SURFACE_TEMP, 3)))
        print('AVG_AMBIENT_TEMP = ' + str(round(AVG_AMBIENT_TEMP, 3)))
        return R_OUT, AVG_SURFACE_TEMP, AVG_AMBIENT_TEMP

    def set_initial_section(self, test_data, CUTOFF_FACTOR, AVG_SURFACE_TEMP,
                            AVG_AMBIENT_TEMP):
        """
        Defines initial section as function of a roof value set by
        CUTOFF_FACTOR. E.g. CUTOFF_FACTOR = 0.95 means that the initial
        section contains data from the beggining of the test cycle until
        the surface temperature reaches 95% of the steady-state surface
        temperature calculated from calculate_section_final method.
        To avoid false triggers it uses the filtered surface temperature
        from add_filtered_data method

        Parameters
        ----------
        test_data : pd.DataFrame
            test_data from set_test_data method
        CUTOFF_FACTOR : int (0.8 to 0.99)
            roof value for the surface tempertature
        AVG_SURFACE_TEMP : int
            from calculate_section_final method
        AVG_AMBIENT_TEMP : int
            from calculate_section_final method

        Returns
        -------
        initial_section_data : pd.DataFrame
            initial section of test_data

        """
        self.test_data = test_data
        self.CUTOFF_FACTOR = CUTOFF_FACTOR
        self.AVG_SURFACE_TEMP = AVG_SURFACE_TEMP
        self.AVG_AMBIENT_TEMP = AVG_AMBIENT_TEMP
        #  avoid SettingWithCopyWarning by making it indepent:
        initial_section_data = test_data.copy()
        CUTOFF = AVG_AMBIENT_TEMP + CUTOFF_FACTOR*(
            AVG_SURFACE_TEMP - AVG_AMBIENT_TEMP)

        initial_section_data = initial_section_data[(
            initial_section_data['surface_temp_filtered'] < CUTOFF)]
        print('cutoff temperature = ' + str(round(CUTOFF, 3)))
        return initial_section_data

    def plot_initial_section(self, initial_section_data):
        """
        Plots surface and ambient temperatures for initial section

        Parameters
        ----------
        initial_section_data : pd.DataFrame
            initial section from set_inital_section method

        """
        import matplotlib.pyplot as plt
        self.initial_section_data = initial_section_data
        fig, ax1 = plt.subplots(figsize=(7, 4))
        ax1.plot(initial_section_data['Test_Time(s)'],
                 initial_section_data['Aux_Temperature_3(C)'],
                 label='Ambient', color='r')
        ax1.plot(initial_section_data['Test_Time(s)'],
                 initial_section_data['Aux_Temperature_1(C)'],
                 label='Surface (Thermocouple 1)')
        ax1.plot(initial_section_data['Test_Time(s)'],
                 initial_section_data['Aux_Temperature_2(C)'],
                 label='Surface (Thermocouple 2)')
        ax1.plot(initial_section_data['Test_Time(s)'],
                 initial_section_data['surface_temp_filtered'],
                 label='Filtered Surface Temp (Savitzky–Golay)')
        ax1.legend(loc=0)
        ax1.set_ylabel('Temperature [°C]')
        ax1.set_xlabel('Test_Time(s)')
        ax1.grid()

    def least_squares_optimization(self, initial_section_data, AVG_Q_GEN,
                                   R_OUT, AVG_AMBIENT_TEMP):

        import numpy as np
        from scipy.optimize import least_squares
        import matplotlib.pyplot as plt
        self.initial_section_data = initial_section_data
        self.AVG_Q_GEN = AVG_Q_GEN
        self.R_OUT = R_OUT
        self.AVG_AMBIENT_TEMP = AVG_AMBIENT_TEMP

        A = []  # Target of the optimization: Cp(ROUT + RIN) = A
        Ta = AVG_AMBIENT_TEMP
        time_data = initial_section_data['Test_Time(s)']

        def y(t, SURFACE_TEMP_INITIAL_GUESS, theta):
            Ts = []
            Ts.append(SURFACE_TEMP_INITIAL_GUESS)
            for i in range(len(t)-1):  
                     
                Ts_n = (((AVG_Q_GEN * R_OUT + Ta - Ts[-1])*(time_data.iloc[i+1] - time_data.iloc[i]))/
                        (theta[0])) + Ts[-1]
                       
                Ts.append(Ts_n)
            return Ts
    
        ts = np.array(initial_section_data['Test_Time(s)'])
        #ys = data_section_initial['Aux_Temperature_1(C)']
        ys = initial_section_data['surface_temp_filtered']
        
        def fun(theta):
            return y(ts, SURFACE_TEMP_INITIAL_GUESS, theta) - ys
        
        theta0 = [106]
        SURFACE_TEMP_INITIAL_GUESS = initial_section_data['surface_temp_filtered'].iloc[0]
        res1 = least_squares(fun, theta0)
        A.append(res1.x[0])        
        
        fig, ax1 = plt.subplots(figsize=(7,4))
        ax1.plot(ts, res1.fun+ys, label = 'fitted least squares')
        ax1.plot(ts, ys, label = 'surface temp (filtered) \n' +
                 str('Cp(Rin + Rout) = ' + str(round(res1.x[0], 2))))
        ax1.set_ylabel('Temperature [°C]')
        ax1.set_xlabel('Time (s)')
        ax1.legend()
        ax1.grid()
        print('\n-----------------------------------------------------------')
        print('Least Squares optimization inputs:')
        print('Ambient Temperature = ' + str(round(Ta, 3)))
        print('AVG_Q_GEN = ' + str(round(AVG_Q_GEN, 3)))
        print('R_OUT = ' + str(round(R_OUT, 3)))
        print('Surface temperature initial guess = ' + str(round(
            SURFACE_TEMP_INITIAL_GUESS, 2)))
        print('\n' + '-----> Least Squares optimization output:')
        print('Cp(Rin + Rout) = ' + str(round(res1.x[0], 2))) 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
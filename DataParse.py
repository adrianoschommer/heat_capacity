# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 09:55:19 2021

@author: Adriano Schommer
"""


class DataParse():
    """
    This class contains methods to deal with raw test data for the heat
    capacity experiment.
    """

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
        OCV : float
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

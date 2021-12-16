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
        print('\n')
        print(str(self.files[int(select_file)]) + ' successfully loaded')
        print('\n')
        return data

    def set_test_data(self, raw_data, HOLD_FACTOR):
        """
        Cut raw data from the beggining of the test to the end of raw data

        Parameters
        ----------
        raw_data : pd.DataFrame
            data from read_file method
        HOLD_FACTOR : int
            How many data points of Current = 0 is hold until it is True

        Returns
        -------
        test_data : pd.DataFrame
            cycle test window from the cutoff time to the end of raw data

        """
        import numpy as np
        self.raw_data = raw_data
        self.HOLD_FACTOR = HOLD_FACTOR
        trigger_counter = 0
        for i in range(0, len(raw_data)):
            trigger_condition = np.mean(
                raw_data['Current(A)'].iloc[-i]
                + raw_data['Current(A)'].iloc[-(i + 1)])
            if round(trigger_condition, 0) == 0:
                trigger_counter += 1
                if trigger_counter >= HOLD_FACTOR:
                    CUTOFF_INDEX = (
                        raw_data['Test_Time(s)'].iloc[HOLD_FACTOR - i])
                    break
        test_data = raw_data[(raw_data['Test_Time(s)'] > CUTOFF_INDEX)]
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

    def filter_temperature_channels(self, data, rolling_window, poly_fit):
        """
        Adds columns to data containing surface and ambient temperatures
        filtered by a Savitzky–Golay filter.

        Parameters
        ----------
        data : pd.DataFrame
            data from read_file or set_test_data method
        rolling_window : int
            must be odd, rolling window for the Savitzky–Golay filter
        poly_fit : int
            polynomial order for the Savitzky–Golay filter

        Returns
        -------
        data : pd.DataFrame
            data with columns added:
            - surface_temp_filtered
            - ambient_temp_filtered

        """
        from scipy.signal import savgol_filter
        self.data = data
        #  avoid SettingWithCopyWarning by making it indepent:
        data = data.copy()
        ambient_temp = data['Aux_Temperature_3(C)']    # Thermocouple 03
        data['surface_temp_filtered'] = savgol_filter(
            data['surface_temp_average'], rolling_window, poly_fit)
        data['ambient_temp_filtered'] = savgol_filter(
            ambient_temp, rolling_window, poly_fit)
        return data

    def add_average_surface_temp(self, raw_data,
                                 total_number_of_thermocouples, 
                                 ambient_thermocouple_index):
        """
        Adds to raw_data the average surface temperature values of all 
        thermocouples used in the test.

        Parameters
        ----------
        raw_data : Tpd.DataFrame
            data from read_file
        total_number_of_thermocouples : int
            How many thermocouples in total were used in the test including
            the ambient temperature thermocouple, which is assumed to be only 
            one.
        ambient_thermocouple_index : int
            the index of the ambient temp thermocouple. It is needed to skip
            this thermocouple while averaging data.

        Returns
        -------
        raw_data : Tpd.DataFrame
            raw_data with columns added:
            - surface_temp_average

        """
        import pandas as pd
        import numpy as np
        self.raw_data = raw_data
        self.total_number_of_thermocouples = total_number_of_thermocouples
        self.ambient_thermocouple_index = ambient_thermocouple_index
        #  avoid SettingWithCopyWarning by making it indepent:
        raw_data = raw_data.copy()
        surface_temp = pd.Series(np.zeros(len(raw_data)))
        for i in range(1, total_number_of_thermocouples + 1):
            if i == ambient_thermocouple_index:
                pass
            else:
                surface_temp = surface_temp.add(raw_data['Aux_Temperature_' 
                                                         + str(i) + '(C)'])
        surface_temp = surface_temp / (total_number_of_thermocouples - 1)
        raw_data['surface_temp_average'] = surface_temp
        return raw_data

    def add_SOC_channel(self, raw_data):
        """
        This method takes raw data and adds SOC channel

        Parameters
        ----------
        raw_data : pd.DataFrame
            data from read_file method.

        Returns
        -------
        raw_data : pd.DataFrame
            data with columns added:
            - SOC

        """
        import numpy as np
        self.raw_data = raw_data
        #  avoid SettingWithCopyWarning by making it indepent:
        raw_data = raw_data.copy()
        HOLD_FACTOR = 20
        trigger_counter = 0
        for i in range(0, len(raw_data)):
            trigger_condition = np.mean(
                raw_data['Current(A)'].iloc[-i]
                + raw_data['Current(A)'].iloc[-(i + 1)])
            if round(trigger_condition, 0) == 0:
                trigger_counter += 1
                if trigger_counter >= HOLD_FACTOR:
                    CUTOFF_INDEX = (raw_data['Test_Time(s)'].iloc[- i])
                    break
        pre_test_data = raw_data[(raw_data['Test_Time(s)'] > CUTOFF_INDEX)]
        discharge_capacity_100_SOC = max(raw_data['Discharge_Capacity(Ah)'])
        discharge_capacity_initial_SOC = max(
            pre_test_data['Discharge_Capacity(Ah)'])
        # finds what is the SOC at the begining of the test
        initial_SOC = (discharge_capacity_initial_SOC
                       / discharge_capacity_100_SOC)
        raw_data['SOC'] = ((raw_data['Discharge_Capacity(Ah)']
                            / discharge_capacity_100_SOC) + initial_SOC) * 100
        return raw_data

    def add_OCV_channel(self, raw_data, file):
        """
        This method takes raw data and adds OCV channel based on OCV(SOC) data

        Parameters
        ----------
        raw_data : pd.DataFrame
            data from read_file method.

        Returns
        -------
        raw_data : pd.DataFrame
            data with columns added:
            - OCV

        """
        import pandas as pd
        self.raw_data = raw_data
        self.file = file
        #  avoid SettingWithCopyWarning by making it indepent:
        raw_data = raw_data.copy()
        OCV_data = pd.read_csv(file)
        df = pd.DataFrame(raw_data['SOC'])
        df = pd.concat([df, OCV_data]).sort_values('SOC')
        df = df.interpolate()
        df = df[df['SOC'].isin(raw_data['SOC'])].sort_index()
        raw_data['OCV'] = df['OCV']
        return raw_data

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
        print('average Q_GEN = ' + str(round(AVG_Q_GEN, 3)) + ' [W]')
        return AVG_Q_GEN

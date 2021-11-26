# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 11:19:47 2021

@author: Adriano Schommer
"""


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

    def calculate_R_OUT(self, final_section_data, AVG_Q_GEN):
        """
        Calculates external thermal resistance from the final section
        of the data.

        Parameters
        ----------
        final_section_data : pd.DataFrame
            pd from set_final_section method
        AVG_Q_GEN : float
            AVG_Q_GEN from calculate_AVG_Q_GEN method

        Returns
        -------
        R_OUT : float
            External thermal resistance [K/W]

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
        print('R_OUT = ' + str(round(R_OUT, 3)) + ' [K/W]')
        return R_OUT

    def calculate_AVG_SURFACE_TEMP(self, final_section_data):
        """
        Calculates average surface temperature from the final section
        of the data.

        Parameters
        ----------
        final_section_data : pd.DataFrame
            pd from set_final_section method

        Returns
        -------
        AVG_SURFACE_TEMP : float
            average surface temperature [K]

        """
        self.final_section_data = final_section_data
        # Thermocouple 01:
        surface_temp_1 = final_section_data['Aux_Temperature_1(C)']
        # Thermocouple 02:
        surface_temp_2 = final_section_data['Aux_Temperature_2(C)']
        AVG_SURFACE_TEMP = ((surface_temp_1 + surface_temp_2)/2).mean()
        print('AVG_SURFACE_TEMP = ' + str(round(AVG_SURFACE_TEMP, 3)))
        return AVG_SURFACE_TEMP

    def set_initial_section(self, test_data, CUTOFF_FACTOR, AVG_SURFACE_TEMP):
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
        AVG_SURFACE_TEMP : float
            from calculate_section_final method

        Returns
        -------
        initial_section_data : pd.DataFrame
            initial section of test_data

        """
        self.test_data = test_data
        self.CUTOFF_FACTOR = CUTOFF_FACTOR
        self.AVG_SURFACE_TEMP = AVG_SURFACE_TEMP

        # Thermocouple 03:
        ambient_temp = test_data['Aux_Temperature_3(C)']
        # Calculates the average surface temperature before set initial data
        AVG_AMBIENT_TEMP = ambient_temp.mean()
        # Avoid SettingWithCopyWarning by making it indepent:
        initial_section_data = test_data.copy()
        CUTOFF = AVG_AMBIENT_TEMP + CUTOFF_FACTOR*(
            AVG_SURFACE_TEMP - AVG_AMBIENT_TEMP)
        initial_section_data = initial_section_data[(
            initial_section_data['surface_temp_filtered'] < CUTOFF)]
        print('cutoff temperature = ' + str(round(CUTOFF, 3)))
        return initial_section_data

    def plot_initial_section(self, initial_section_data):
        """
        Plots surface and ambient temperatures for initial section of the data.

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

    def optimize_equation(self, ys, initial_section_data, AVG_Q_GEN, R_OUT,
                          plot=False):
        """
        Performs a least square regression optimizing Cp(ROUT + RIN) of the
        Equation 4 (Bryden, 2018).

        Note: forward Euler was used instead of backward Euler for easy
              code implementation.

        Bryden, T. S., et al.(2018). Methodology to determine the heat
        capacity of lithium-ion cells. Journal of Power Sources,
        https://doi.org/10.1016/j.jpowsour.2018.05.084

        Parameters
        ----------
        ys : pd.DataFrame
            surface temperature input from initial_section_data. Could be:
            - any of the thermocouples. i.e. 'Aux_Temperature_1(C)'
            - filtered surface temperature. i.e. 'surface_temp_filtered'
        initial_section_data : pd.DataFrame
            from set_initial_section_data method
        AVG_Q_GEN : float
            average heat generated from calculate_AVG_Q_GEN method
        R_OUT : float
            external thermal resistance from calculate_section_final method

        Returns
        -------
        optimized_parameter : float
            optimized Cp(ROUT + RIN) parameter

        """
        from scipy.optimize import least_squares
        import matplotlib.pyplot as plt
        import numpy as np
        self.ys = ys
        self.initial_section_data = initial_section_data
        self.AVG_Q_GEN = AVG_Q_GEN
        self.R_OUT = R_OUT

        time_data = initial_section_data['Test_Time(s)']
        # Thermocouple 03:
        ambient_temp = initial_section_data['Aux_Temperature_3(C)']
        # Calculates the average surface temperature for initial section
        AVG_AMBIENT_TEMP = ambient_temp.mean()
        Ta = AVG_AMBIENT_TEMP

        def target_equation(t, SURFACE_TEMP_INITIAL_GUESS, INITIAL_GUESS):
            """
            Target equation for the optimization process

            Parameters
            ----------
            t : np.array
                time array, should be the same length as initial_section_data
                time column
            SURFACE_TEMP_INITIAL_GUESS : float
                initial guess for surface temperature [K], should be the first
                value of the surface temp data used for the optimization
            INITIAL_GUESS : float
                initial guess for Cp(ROUT + RIN) parameter
            plot : bool (default False)
                if plot=True it plots fitted curve vs raw data

            Returns
            -------
            Ts : np.array
                calculated surface temperature

            """
            Ts = []  # surface temperature
            Ts.append(SURFACE_TEMP_INITIAL_GUESS)
            for i in range(len(t) - 1):
                Ts_n = (((AVG_Q_GEN * R_OUT + Ta - Ts[-1])
                         * (time_data.iloc[i + 1] - time_data.iloc[i]))
                        / (INITIAL_GUESS[0])) + Ts[-1]
                Ts.append(Ts_n)
            return Ts
        ts = np.array(time_data)

        def fun(INITIAL_GUESS):
            return target_equation(ts, SURFACE_TEMP_INITIAL_GUESS,
                                   INITIAL_GUESS) - ys
        INITIAL_GUESS = 106
        SURFACE_TEMP_INITIAL_GUESS = ys.iloc[0]
        # Here is where the optimization actually happens using least squares
        # SciPy module:
        result = least_squares(fun, INITIAL_GUESS)
        optimized_parameter = result.x[0]  # Cp(ROUT + RIN)
        if plot:
            fig, ax1 = plt.subplots(figsize=(7, 4))
            ax1.plot(ts, ys, label='surface temp (filtered) \n' +
                     str('Cp(Rin + Rout) = ' + str(round(result.x[0], 2))))
            ax1.plot(ts, result.fun + ys, label='fitted least squares')
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
            print('Cp(Rin + Rout) = ' + str(round(optimized_parameter, 2)))
        else:
            pass
        return optimized_parameter

    def calculate_surface_temp(self, DENOMINATOR, ys, initial_section_data,
                               AVG_Q_GEN, R_OUT):
        """
        Gets DENOMINATOR = Cp(ROUT + RIN) as input and evaluates Equation 4
        (Bryden, 2018) to calculate surface temperature.

        Note: although surface temp is purely calculated, this function gets
              time and surface temperature as input for easy plot with test
              data afterwards.

        Bryden, T. S., et al.(2018). Methodology to determine the heat
        capacity of lithium-ion cells. Journal of Power Sources,
        https://doi.org/10.1016/j.jpowsour.2018.05.084

        Parameters
        ----------
        DENOMINATOR : float
            Cp(ROUT + RIN) for which the equation will be evaluated
        ys : pd.DataFrame
            surface temperature input from initial_section_data. Could be:
            - any of the thermocouples. i.e. 'Aux_Temperature_1(C)'
            - filtered surface temperature. i.e. 'surface_temp_filtered'
        initial_section_data : pd.DataFrame
            from set_initial_section_data method
        AVG_Q_GEN : float
            average heat generated from calculate_AVG_Q_GEN method
        R_OUT : float
            external thermal resistance from calculate_section_final method

        Returns
        -------
        Ts : list
            calculated temperature surface

        """
        self.DENOMINATOR = DENOMINATOR
        self.ys = ys
        self.initial_section_data = initial_section_data
        self.AVG_Q_GEN = AVG_Q_GEN
        self.R_OUT = R_OUT

        time_data = initial_section_data['Test_Time(s)']
        # Thermocouple 03:
        ambient_temp = initial_section_data['Aux_Temperature_3(C)']
        # Calculates the average surface temperature for initial section
        AVG_AMBIENT_TEMP = ambient_temp.mean()

        SURFACE_TEMP_INITIAL_GUESS = ys.iloc[0]
        Ts = []
        Ts.append(SURFACE_TEMP_INITIAL_GUESS)

        for i in range(len(time_data) - 1):
            Ts_n = (((AVG_Q_GEN * R_OUT + AVG_AMBIENT_TEMP - Ts[-1])
                     * (time_data.iloc[i + 1] - time_data.iloc[i]))
                    / (DENOMINATOR)) + Ts[-1]
            Ts.append(Ts_n)
        return Ts

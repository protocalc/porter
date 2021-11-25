#https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython
#https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15
#https://www.adafruit.com/product/1085


import time
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode 

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input. """
    errors = {1001: 'Choosen input not available'}

class ads1115:
    
    '''
    Interface for the ADS1x15 series of analog-to-digital converters
    '''

    def __init__(self, chan_input, **kwargs):

        '''
        Create a connection using I2C protocol to the ADS1115. 
        Requires:
        - chan_input: a list or an int. The channel number input cannot be bigger than 3.
                      If the input is an int, the mode is automatically switched to single. 
                      For differential mode the input list needs to have a shape Nx2 where N
                      are the number of differential measurements and each one needs to have 2
                      channels for the differential measurement e.g. [[0,1],[2,3]] creates two 
                      differential measurments, one between the 0 and 1 channel and the other 
                      between the 2 and 3
        Optional:
        - mode: possible between differential or single. Check the manual for the difference 
        '''

        ### Check that the mode choosen is available
        availables_modes = ['differential', 'single']

        mode = kwargs.get('mode', 'differential')

        try:
            if mode in availables_modes:
                pass
            else:
                raise InputError(1001)
        except InputError as err:
            print("Error %d: %s, availables modes %s" % (err.args[0], err.errors[err.args[0]], availables_modes))

        ### Connect to the ADC
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)

        ### Check the channel number and convert them to an object input for the ads object
        available_input = [ADS.P0, ADS.P1, ADS.P2, ADS.P3]

        try:
            if isinstance(chan_input, int) or isinstance(chan_input, float):
                if len(chan_input) < 4:
                    pass
                else:
                    raise InputError(1001)
            else:
                if np.any(len(chan_input)< 4):
                    pass
                else:
                    raise InputError(1001)
        except InputError as err:
            print("Error %d: %s, availables channels %s" % \
                  (err.args[0], err.errors[err.args[0]], np.arange(4, dtype=int)))

        if isinstance(chan_input, int) or isinstance(chan_input, float):
            chan_input = [int(chan_input)]
            mode = 'single'

        if isinstance(chan_input, np.ndarray):
            chan_input = list(chan_input)

        for i in range(4):
            idx, = np.where(chan_input == i)
            if len(idx) != 0:
                chan_input[idx] = available_input[i]

        self.chan = []

        if mode == 'single':
            for i in range(len(chan_input)):
                self.chan.append(AnalogIn(self.ads, available_input[chan_input[i]]))
        else:
            for i in range(int(np.size(chan_input)/2)):
                if np.size(chan_input)==2:
                    p0 = chan_input[0]
                    p1 = chan_input[1]
                else:
                    p0 = chan_input[i][0]
                    p1 = chan_input[i][1]


                self.chan.append(AnalogIn(self.ads, p0, p1))

    def get_value(self):

        '''
        Get the RAW value from the ADC
        '''
        if len(self.chan) > 1:
            value=[]
            for i in range(len(self.chan)):
                value.append(self.chan[i].value)
        else:
            value = [self.chan[0].value]
        return value
  
    def get_voltage(self):

        '''
        Get the converted voltage from the ADC
        ''' 
        if len(self.chan) > 1:
            voltage=[]
            for i in range(len(self.chan)):
                voltage.append(self.chan[i].voltage)
        else:
            voltage = self.chan[0].voltage
        return voltage

    def set_data_rate(self, data_rate):

        '''
        Set the data rate of the ADC in Sample per Seconds.
        Available rates: 8, 16, 32, 64, 128, 250, 475, 860
        Requires:
        - data_rates: an integer value to be choosen between the availables one
                      If the choosen value is not available, the closest values 
                      is automatically set
        '''

        available_rates = [8, 16, 32, 64, 128, 250, 475, 860]

        data_rate = int(data_rate)

        if data_rate not in available_rates:
            idx, = np.where(np.abs(available_rates-data_rate) == \
                            np.amin(np.abs(available_rates-data_rate)))

            data_rate = available_rates[idx]
        
        self.ads.mode = Mode.CONTINUOUS
        self.ads.data_rate = data_rate

    def stream_data(self, samples=None, save=False, filename='adc_values.txt', \
                    update_time=None):

        '''
        stream and optionally save the data from the adc
        Optional:
        - samples: int, number of values read from the ADC. 
                   if None the cycle continues unless is stopped using CTRL+C
        - save: if true data are saved on file
        - filename: name of the file where the data are saved. It is necessary 
                    to include path if you want to save the file in a different 
                    directory than the working one
        - update_time: float number in ms. if None the data are updated as fast as possible
        '''

        def list_sum(data):
            flat_data = [y for x in data for y in (x if isinstance(x, list) else [x])]
            my_sum = flat_data[0]   
            for v in flat_data[1:]:
                my_sum+= v
            return my_sum

        if update_time is not None:
            update_time = update_time*1e-3

        count = 0
        
        adc_count = self.get_value()
        voltage = self.get_voltage()
        t = time.time()
        
        col_0='{:15s}  | '. format('CTime (s)' ) 
        col_1=[]
        col_2=[]
        
        for k in range(int( np.size(adc_count) )):
            if k==int( np.size(adc_count) -1):
                if self.ads.gain  > 8:
                    col_2= '{:15s}  |  {:15s}  | \n '. format('ADC Count '+ str(int(k)), 'Voltage '+ str(int(k)) +' (mV)')
                    fact = 1e3
                else:
                    col_2= '{:15s}  |  {:15s}  | \n '. format('ADC Count '+ str(int(k)), 'Voltage '+ str(int(k)) +' (V)')  
                    fact = 1
            else:
                if self.ads.gain  > 8:
                    col_1.append( '{:15s}  |  {:15s}  | '. format('ADC Count '+ str(int(k)), 'Voltage '+ str(int(k)) +' (mV)'))
                    fact = 1e3
                else:
                    col_1.append('{:15s}  |  {:15s}  | '. format('ADC Count '+ str(int(k)), 'Voltage '+ str(int(k)) +' (V)')  )
                    fact = 1


        if len(col_1)>1:
            col_1=list_sum(col_1)
            colums_name=col_0+col_1+col_2

        elif len(col_1)==1:
            col_1=str(col_1[0])
            colums_name=col_0+col_1+col_2
        else:
            colums_name=col_0+col_2
     
        if save:
            with open(filename, 'a') as f:
                f.write(colums_name)

        t = -np.inf

        while True:
            if update_time is not None:
                if time.time()-t < update_time:
                    time.sleep(update_time-time.time()+t)

            adc_count = np.array(self.get_value())
            voltage = np.array(self.get_voltage())*fact
            t = time.time()
            
            
            x='{:15.0f} |'.format(t)
            y=[]
            z=[ ]
            for i in range(int(np.size(adc_count))):
                if i==int( np.size(adc_count) -1):
                    z='{:15.4f} | {:15.9f} \n'.format(adc_count[i], voltage[i]) 
                else:
                    y.append('{:15.4f} | {:15.9f} |'.format(adc_count[i], voltage[i]) )

            if np.size(y)>1:
                y=list_sum(y)
                x=x+y+z
            elif np.size(y)==1:
                y=str(y)
                x=x+y+z
            else:
                x=x+z
            print(x)

            if save:
                with open(filename, 'a') as f:
                    f.write(x)

            if samples is not None:
                count += 1
                if count > samples:
                    break
        
    def set_gain(self, gain):

        '''
         The ADS1115 has the these gain options.
            
                    GAIN    RANGE (V)
                   ----    ---------
                    2/3    +/- 6.144
                    1      +/- 4.096
                    2      +/- 2.048
                    4      +/- 1.024
                    8      +/- 0.512
                    16     +/- 0.256
        
            
        '''
        
        self.ads.gain=gain

        return gain

    def set_params(self, cat, value):

        '''
        Wrapper function to set parameters of one of the *set* methods of this class
        Paramters:
        - cat: str, category of the value that needs to be changed
        - value: float, new value to be set
        '''

        if cat.lower() == 'gain':
            msg = self.set_gain(value)
        elif cat.lower() == 'rate':
            msg = self.set_data_rate(value)

        del msg
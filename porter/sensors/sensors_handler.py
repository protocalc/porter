import sensors.ublox as ubx
import sensors.KERNEL as KERNEL
import sensors.FakeSensor as fake

try:
    import sensors.ads1115 as ads
except ModuleNotFoundError:
    pass



class Handler:

    def __init__(self, sensor_params, local=False):

        self.sensor_params = sensor_params
        self.local = local

        self._connection()

        if not local:
            if 'configuration' in self.sensor_params.keys():
                self._configuration()

    
    def _connection(self):

        if self.local:
            self.conn = fake.FakeConnection(self.sensor_params['name'])
        
        else:
            if self.sensor_params['sensor_info']['manufacturer'].lower() == 'ublox':

                temp = ubx.UBX(
                    port = self.sensor_params['connection']['paramters']['port'],
                    baudrate = self.sensor_params['connection']['paramters']['baudrate'],
                    name = self.sensor_params['name']
                )

                self.conn = temp
            
            elif self.sensor_params['sensor_info']['manufacturer'].lower() == 'ads':

                self.conn = ads.ads1115(
                    self.sensor_params['connection']['paramters']['channels'],
                    mode = self.sensor_params['connection']['paramters']['mode'],
                    name = self.sensor_params['name'],
                    output_mode = self.sensor_params['connection']['paramters']['output']
                    )

            elif self.sensor_params['sensor_info']['manufacturer'].lower() == 'inertial_labs':

                temp = KERNEL.KernelInertial(
                    self.sensor_params['connection']['paramters']['port'],
                    self.sensor_params['connection']['paramters']['baudrate'], \
                    name = self.sensor_params['name']
                    )

                self.conn = temp.conn

    def _configuration(self):

        if self.sensor_params['sensor_info']['manufacturer'].lower() == 'ublox':

            config = ubx.UBXconfig(
                serial_connection=self.conn,
                name = self.sensor_params['connection']['paramters']['name']
                )
            
            config.configure(self.sensor_params['configuration'])
        
        elif self.sensor_params['sensor_info']['manufacturer'].lower() == 'ads':

            self.conn.configure(self.sensor_param['configuration'])

        elif self.sensor_params['sensor_info']['manufacturer'].lower() == 'inertial_labs':

            self.conn.configure(self.sensor_params['configuration'])

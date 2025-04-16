import porter.sensors.FakeSensor as fake
import porter.sensors.KERNEL as KERNEL
import porter.sensors.ubx as ubx

import porter.sensors.ads1015 as ads
import porter.sensors.inertial as inertial
#import porter.sensors.ads1x15 as ads

try:
    import porter.sensors.ads1015 as ads
except ModuleNotFoundError:
    pass

import porter.sensors.mcp4725 as mcp


class Handler:

    def __init__(self, sensor_params, local=False):

        self.sensor_params = sensor_params
        self.local = local

    def _connection(self):
        

        # For local development, set up a fake connection.
        if self.local:
            self.obj = fake.FakeConnection(self.sensor_params["name"])

        else:
            if self.sensor_params["sensor_info"]["type"].lower() == "gps":
                # Set up GPS with output port, baudrate, GPS name, and output file name options.
                self.obj = ubx.UBX(
                    port=self.sensor_params["connection"]["parameters"]["port"],
                    baudrate=self.sensor_params["connection"]["parameters"]["baudrate"],
                    name=self.sensor_params["name"],
                )


            elif self.sensor_params["sensor_info"]["type"].lower() == "adc":
                # Set up ADC with name and I2C bus specifications.
                self.obj = ads.ADS1015(
                    name=self.sensor_params["name"],
                    bus=self.sensor_params["connection"]["parameters"]["bus"],
                    sensor_core=self.sensor_params["sensor_core"]
                )

            elif self.sensor_params["sensor_info"]["type"].lower() == "inertial":
                # Set up inertial sensors with name and I2C bus specifications
                self.obj = inertial.Inertial(
                    name=self.sensor_params["name"],
                    bus=self.sensor_params["connection"]["parameters"]["bus"],
                    sensor_core=self.sensor_params["sensor_core"]
                )

            elif self.sensor_params["sensor_info"]["type"].lower() == "dac":
                # Set up DAC with address specification.
                self.obj = mcp.MCP4725(
                    self.sensor_params["connection"]["parameters"]["address"],
                )

            elif self.sensor_params["sensor_info"]["type"].lower() == "inclinometer":
                if (
                    self.sensor_params["sensor_info"]["manufacturer"].lower()
                    == "inertial_labs"
                ):
                    # Set up inclinometer with port, baudrate, and sensor name.
                    self.obj = KERNEL.KernelInertial(
                        self.sensor_params["connection"]["parameters"]["port"],
                        self.sensor_params["connection"]["parameters"]["baudrate"],
                        name=self.sensor_params["name"],
                    )

    def _configuration(self):
        if "configuration" in self.sensor_params.keys():
            self.obj.configure(self.sensor_params["configuration"])
        else:
            pass

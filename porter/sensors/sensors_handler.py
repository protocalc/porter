import porter.sensors.ubx as ubx
import porter.sensors.KERNEL as KERNEL
import porter.sensors.FakeSensor as fake

try:
    import porter.sensors.ads1115 as ads
except ModuleNotFoundError:
    pass

import porter.sensors.mcp4725 as mcp


class Handler:

    def __init__(self, sensor_params, local=False):

        self.sensor_params = sensor_params
        self.local = local

        self._connection()

        if not local:
            if "configuration" in self.sensor_params.keys():
                self._configuration()

    def _connection(self):

        if self.local:
            self.obj = fake.FakeConnection(self.sensor_params["name"])

        else:
            if self.sensor_params["sensor_info"]["type"].lower() == "gps":

                self.obj = ubx.UBX(
                    port=self.sensor_params["connection"]["parameters"]["port"],
                    baudrate=self.sensor_params["connection"]["parameters"]["baudrate"],
                    name=self.sensor_params["name"],
                )

                self.conn = self.obj.conn

            elif self.sensor_params["sensor_info"]["type"].lower() == "adc":

                self.obj = ads.ads1115(
                    self.sensor_params["connection"]["parameters"]["channels"],
                    mode=self.sensor_params["connection"]["parameters"]["mode"],
                    name=self.sensor_params["name"],
                    output_mode=self.sensor_params["connection"]["parameters"][
                        "output"
                    ],
                )

            elif self.sensor_params["sensor_info"]["type"].lower() == "dac":

                self.obj = mcp.MCP4725(
                    self.sensor_params["connection"]["parameters"]["address"],
                )

            elif self.sensor_params["sensor_info"]["type"].lower() == "inclinometer":
                if (
                    self.sensor_params["sensor_info"]["manufacturer"].lower()
                    == "inertial_labs"
                ):

                    self.obj = KERNEL.KernelInertial(
                        self.sensor_params["connection"]["parameters"]["port"],
                        self.sensor_params["connection"]["parameters"]["baudrate"],
                        name=self.sensor_params["name"],
                    )

                    self.conn = self.obj.conn

    def _configuration(self):

        if self.sensor_params["sensor_info"]["type"].lower() == "gps":

            config = ubx.UBXconfig(
                serial_connection=self.obj, name=self.sensor_params["name"]
            )

            config.configure(self.sensor_params["configuration"])

        else:
            self.obj.configure(self.sensor_params["configuration"])

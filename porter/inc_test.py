import sensors.KERNEL as kn

inc = kn.KernelInertial('/dev/inclinometer', 115200)

cfg = {'mode': 'KERNEL_CalibHR'}
inc.configure(cfg)

import time
time.sleep(2)

while True:
    print(inc.read_single(decode=True))
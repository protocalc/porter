import os

current_dir = os.path.dirname(os.path.abspath(__file__))

print("Installing required modules in the folder ./modules...")

# VmbPy
print(" Installing VmbPy")
try:
    os.system(f"pip install -e {current_dir}/modules/VmbPy/.")
except:
    print("Error installing VmbPy")

# Pyalvium
print(" Installing Pyalvium")
try:
    os.system(f"pip install -e {current_dir}/modules/Alvium-Camera-Module-Python/.")
except:
    print("Error installing Pyalvium")

# SourCore
print(" Installing SourCore")
try:
    os.system(f"pip install -e {current_dir}/modules/sour_core/.")
except:
    print("Error installing SourCore")

# ADS1015
print(" Installing ADS1015")
try:
    # cd to the build_for_pi.sh script to the current directory and run it
    os.system(f"cd {current_dir}/modules/ADS1015-ADC-Module && ./build_for_pi.sh")
except:
    print("Error installing ADS1015")

# Inertial sensor
print(" Installing Inertial-Sensors-Module")
try:
    os.system(f"cd {current_dir}/modules/Inertial-Sensors-Module && ./build_for_pi.sh")
except:
    print("Error installing Inertial-Sensors-Module")

# LM76
print(" Installing LM76-Temperature-Sensor")
try:
    os.system(f"cd {current_dir}/modules/LM76-Temperature-Sensor && ./build_for_pi.sh")
except:
    print("Error installing LM76-Temperature-Sensor")

print("Done")
#!/usr/bin/env python3
import subprocess
import re
import time
import sys
import os

# --- CONFIGURATION FLAGS ---
# WARNING: Setting PROFILE_USB = True will temporarily disconnect all USB devices.
# Only run with True if you are connected via Ethernet or Wi-Fi (NOT USB-tethering or a USB drive).
PROFILE_USB = True

if os.geteuid() != 0:
    print("Error: This diagnostic script requires root privileges to toggle hardware drivers.")
    print("Please run with: sudo python3 <script_name>.py")
    sys.exit(1)

# Exhaustive hardware map of the RPi 5 topology
RAIL_METADATA = {
    "VDD_CORE":    "CPU / GPU Cores (BCM2712 Core Engine Logic)",
    "1V1_SYS":     "HDMI Transmitters, PCIe Controller, AXI System Bus",
    "1V8_SYS":     "GPIO Multiplexers, MIPI CSI/DSI Transceivers",
    "3V3_SYS":     "SD Card Slot, Ethernet PHY, 3.3V Pin Rails",
    "DDR_VDD2":    "LPDDR5/LPDDR4X Memory Array Core",
    "DDR_VDDQ":    "LPDDR5/LPDDR4X I/O Bus Termination Power",
    "0V8_SW":      "Low-Voltage Core Infrastructure Switching Rail",
    "3V7_WL_SW":   "Onboard Wi-Fi and Bluetooth Baseband Radio Switch",
    "3V3_DAC":     "Audio / Video Digital-to-Analog Converters",
    "3V3_ADC":     "Analog-to-Digital Converter Reference Rail",
}

def parse_pmic_snapshot():
    """Parses PMIC ADC and returns raw data structures along with total logic watts."""
    try:
        raw_output = subprocess.check_output(["vcgencmd", "pmic_read_adc"]).decode("utf-8")
    except Exception:
        print("Error: Could not communicate with the PMIC firmware via vcgencmd.")
        sys.exit(1)

    voltages = {}
    currents = {}
    pattern = re.compile(r"([\w_]+)_(volt|current)\(\d+\)=([\d.]+)V?A?")
    
    for line in raw_output.strip().split("\n"):
        clean_line = line.replace(" volt(", "_volt(").replace(" current(", "_current(")
        match = pattern.search(clean_line)
        if match:
            rail, measurement, value = match.groups()
            if measurement == "volt":
                voltages[rail] = float(value)
            elif measurement == "current":
                currents[rail] = float(value)

    logic_watts = 0.0
    rail_data = {}
    
    for rail in voltages.keys():
        if "EXT5V" in rail or rail not in currents:
            continue
        v = voltages[rail]
        i = currents[rail]
        w = v * i
        logic_watts += w
        rail_data[rail] = {"v": v, "i": i, "w": w}
        
    return logic_watts, rail_data, voltages.get("EXT5V", 0.0)

def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

print("==========================================================================")
print("              RASPBERRY PI 5 FULL HARDWARE POWER PROFILER                 ")
print("==========================================================================")
print("Establishing connected baseline status (5 second settling window)...")
time.sleep(5)

baseline_watts, baseline_rails, ext5v_v = parse_pmic_snapshot()
profile_deltas = {}

# Display active baseline infrastructure dump
print("\n--- Current Baseline Telemetry (All Blocks Active) ---")
print(f"{'Silicon Rail / Domain':<20} | {'Voltage':<7} | {'Current':<7} | {'Power':<9} | {'Metadata Description'}")
print("-" * 105)
for rail, data in sorted(baseline_rails.items()):
    desc = RAIL_METADATA.get(rail, "Internal Auxiliary Subsystem")
    print(f"{rail:<20} | {data['v']:>5.2f} V | {data['i']:>5.2f} A | {data['w']*1000:>6.1f} mW | {desc}")
print("-" * 105)
print(f"Total Monitored Logic Baseline Draw: {baseline_watts:.3f} W (Main Supply Line: {ext5v_v:.2f}V)")

# --- RUN DIAGNOSTICS ---
print("\nExecuting differential analysis loops...")

# 1. HDMI Test
run_command("vcgencmd display_power 0")
time.sleep(2)
hdmi_off_watts, _, _ = parse_pmic_snapshot()
profile_deltas["HDMI Transmitter Logic"] = baseline_watts - hdmi_off_watts
run_command("vcgencmd display_power 1")
time.sleep(1)

# 2. Wireless Radio Test
run_command("rfkill block wifi && rfkill block bluetooth")
time.sleep(2)
rf_off_watts, _, _ = parse_pmic_snapshot()
profile_deltas["Wireless Radios (Wi-Fi/BT)"] = hdmi_off_watts - rf_off_watts
run_command("rfkill unblock wifi && rfkill unblock bluetooth")
time.sleep(1)

# 3. USB Subsystem Test (Gate-kept by flag)
if PROFILE_USB:
    print("Isolating USB bus (Unbinding xHCI Host Controller)...")
    usb_unbind_success = run_command('echo "0000:01:00.0" | tee /sys/bus/pci/drivers/xhci_hcd/unbind')
    if usb_unbind_success:
        time.sleep(3)
        usb_off_watts, _, _ = parse_pmic_snapshot()
        profile_deltas["USB Controller & VBUS Ports"] = rf_off_watts - usb_off_watts
        run_command('echo "0000:01:00.0" | tee /sys/bus/pci/drivers/xhci_hcd/bind')
    else:
        print("Warning: USB unbind failed.")
        profile_deltas["USB Controller & VBUS Ports"] = 0.0
else:
    print("Skipping USB hardware profile (PROFILE_USB flag set to False).")
    profile_deltas["USB Controller & VBUS Ports"] = 0.0

# --- FINAL REPORT GENERATION ---
print("\n" + "=" * 75)
print("                       FINAL COMPONENT POWER PROFILE                      ")
print("=" * 75)
print(f"{'Component Domain Block':<35} | {'Isolated Power Footprint':<20}")
print("-" * 75)

total_profiled_deltas = 0.0
for component, delta in profile_deltas.items():
    actual_delta = max(0.0, delta)
    total_profiled_deltas += actual_delta
    print(f"{component:<35} | {actual_delta*1000:>7.1f} mW ({actual_delta:.3f} W)")

print("-" * 75)
core_overhead = max(0.0, baseline_watts - total_profiled_deltas)
print(f"{'Core System Infrastructure (CPU/RAM/Idle)':<35} | {core_overhead*1000:>7.1f} mW ({core_overhead:.3f} W)")
print(f"{'Total Measured Hardware Power Draw':<35} | {baseline_watts*1000:>7.1f} mW ({baseline_watts:.3f} W)")
print("-" * 75)

# Empirical wall-draw estimation equation 
estimated_wall_watts = (baseline_watts * 1.1451) + 0.5879
print(f"ESTIMATED COMPLETE WALL LOAD (Includes missing 5V lines): \033[1;32m{estimated_wall_watts:.3f} Watts\033[0m")
print("=" * 75)
print("Diagnostic run complete. Hardware states safely restored.")
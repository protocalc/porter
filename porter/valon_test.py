
import os
import yaml
import valon
import sensors.ads1115 as ads
import sensors.mcp4725 as mcp

path = os.path.dirname(os.path.realpath(__file__))

cfg_path = path+'/config/rover_config.yml'

with open(cfg_path, 'r') as cfg:
    config = yaml.safe_load(cfg)

synt=valon.valon(config['source']['port'], config['source']['baudrate'])

synt.set_freq(config['source']['freq']/6)
synt.set_pwr(config['source']['power'])
if config['source']['mod_freq'] > 0:
    synt.set_amd(config['source']['mod_amp'],config['source']['mod_freq'])


# adc = ads.ads1115(
#     config['sensors']['ADC_1']['connection']['parameters']['channels'],
#     mode = config['sensors']['ADC_1']['connection']['parameters']['mode'],
#     name = config['sensors']['ADC_1']['name'],
#     output_mode = config['sensors']['ADC_1']['connection']['parameters']['output']
#     )
# 
# 
# adc.configure(config['sensors']['ADC_1']['configuration'])

#dac = mcp.MCP4725(
#    config['sensors']['DAC_1']['connection']['parameters']['address'],
#    )

#dac.configure(config['sensors']['DAC_1']['configuration'])
# d = []
# samples = 10000
# 
# for _ in range(samples):
#     d.append(adc._get_voltage(return_binary=False))

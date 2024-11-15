g = 9.8106

GYRO_SCALE = 1e5
ACC_SCALE = 1e6 * g

WORD = 'H'
SWORD = 'h'
WORD_LONG = 'I'
SWORD_LONG = 'i'
WORD_LONG_LONG = 'Q'


USW_TABLE = {
    'low': [
        'Reserved',
        'Internal Comms',
        'Internal Config',
        'Reserved',
        'Reserved',
        'Reserved',
        'Reserved',
        'Reserved',
        ],
    'high': [
        'Reserved',
        'Reserved',
        'AngRateX',
        'AngRateX',
        'AngRateX',
        'Reserved',
        'Temperature',
        'Reserved'
    ]
}

def extract_USW(USW):

    def check_byte(byte):
        if isinstance(byte, int):
            return bin(byte).lstrip('0b')
        elif isinstance(byte, str):
            return bin(int(byte, base=16)).lstrip('0b')

    def check_values(bits, table):
        count = 0
        tmp = ''
        for i in bits:
            if table[count] == 'reserved':
                tmp = 'RES_'
            else:
                if i == 1:
                    tmp = 'KO_'
                else:
                    tmp = 'OK_'
        
        return tmp[:-1]

    low = check_byte(USW[0])
    high = check_byte(USW[1])

    return check_values(low, USW_TABLE['low']), check_values(high, USW_TABLE['high'])

MODES = {
    'KERNEL_Orientation': {
        'Address': b'\x33',
        'length': 34,
        'Parameters': [
            'Heading',
            'Pitch',
            'Roll',
            'GyroX',
            'GyroY',
            'GyroZ',
            'AccX',
            'AccY',
            'AccZ',
            'MagX',
            'MagY',
            'MagZ',
            'Reserved',
            'USW',
            'Vinp',
            'Temper'
            ],
        'Type': [
            WORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            WORD_LONG,
            WORD,
            WORD,
            SWORD
            ],
        'Scale': [
            100,
            100,
            100,
            10,
            10,
            10,
            2000 * g,
            2000 * g,
            2000 * g,
            0,
            0,
            0,
            1,
            1,
            100,
            10
            ]
        },

    'KERNEL_GAData': {
        'Address': b'\x8F',
        'Length': 32,
        'Parameters': [
            'GyroX',
            'GyroY',
            'GyroZ',
            'AccX',
            'AccY',
            'AccZ',
            'Reserved',
            'USW',
            'Vinp',
            'Temper'
            ],
        'Type': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            WORD,
            WORD,
            WORD,
            SWORD
            ],
        'Scale': [
            1e5,
            1e5,
            1e5,
            1e6,
            1e6,
            1e6,
            1,
            1,
            100,
            10
            ]
        },

    'KERNEL_GAmData' :{
        'Address': b'\x9B',
        'Length': 32,
        'Parameters': [
            'GyroX',
            'GyroY',
            'GyroZ',
            'AccX',
            'AccY',
            'AccZ',
            'Time Flag',
            'Second Fraction',
            'Temper'
            ],
        'Type': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            WORD,
            WORD_LONG,
            SWORD
            ],
        'Scale': [
            1e5,
            1e5,
            1e5,
            1e6,
            1e6,
            1e6,
            1,
            1,
            10
            ]
        },

    'KERNEL_QuatData': {
        'Address': b'\x82',
        'length': 34,
        'Parameters': [
            'Heading',
            'Pitch',
            'Roll',
            'q0',
            'q1',
            'q2',
            'q3',
            'Reserved',
            'USW',
            'Vinp',
            'Temper'
            ],
        'Type': [
            WORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            WORD_LONG*3+WORD,
            WORD,
            WORD,
            SWORD
            ],
        'Scale': [
            100,
            100,
            100,
            10000,
            10000,
            10000,
            10000,
            1,
            1,
            100,
            10
            ]
        },

    'KERNEL_CalibHR': {
        'Address': b'\x81',
        'length': 52,
        'Parameters': [
            'Heading',
            'Pitch',
            'Roll',
            'GyroX',
            'GyroY',
            'GyroZ',
            'AccX',
            'AccY',
            'AccZ',
            'MagX',
            'MagY',
            'MagZ',
            'Counter',
            'Reserved',
            'USW',
            'Vinp',
            'Temper'
            ],
        'Type': [
            WORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            SWORD,
            WORD,
            WORD,
            SWORD
            ],
        'Scale': [
            1000,
            1000,
            1000,
            GYRO_SCALE,
            GYRO_SCALE,
            GYRO_SCALE,
            ACC_SCALE,
            ACC_SCALE,
            ACC_SCALE,
            1,
            1,
            1,
            1,
            1,
            1,
            100,
            10
            ]
        },

    ### ONLY FOR KERNEL-120 and KERNEL-220

    'KERNEL_GAAmData': {
        'Address': b'\xA5',
        'Length': 44,
        'Parameters': [
            'GyroX',
            'GyroY',
            'GyroZ',
            'Acc1X',
            'Acc1Y',
            'Acc1Z',
            'Acc2X',
            'Acc2Y',
            'Acc2Z',
            'Reserved',
            'USW',
            'Vinp',
            'Temper'
            ],
        'Type': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            WORD,
            WORD,
            WORD,
            SWORD
            ],
        'Scale': [
            1e5,
            1e5,
            1e5,
            1e6,
            1e6,
            1e6,
            1e6,
            1e6,
            1e6,
            1,
            1,
            100,
            10
            ]
    },

    'KERNEL_GAAData': {
        'Address': b'\xA6',
        'Length': 44,
        'Parameters': [
            'GyroX',
            'GyroY',
            'GyroZ',
            'Acc1X',
            'Acc1Y',
            'Acc1Z',
            'Acc2X',
            'Acc2Y',
            'Acc2Z',
            'Time Flag',
            'Second Fraction',
            'Temper'
            ],
        'Type': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG,
            WORD,
            WORD_LONG,
            SWORD
            ],
        'Scale': [
            1e5,
            1e5,
            1e5,
            1e6,
            1e6,
            1e6,
            1e6,
            1e6,
            1e6,
            1,
            1,
            10
            ]
        },
    
    'USER_DEFINED_DATA': {
        'Address': b'\x95'
        },

    'USER_DEFINED_DATA_CONFIG': {
        'Address': b'\x96'
        },
    
    'STOP': {
        'Address': b'\xFE'
        }
    
    }

### USER DEFINED DATA

User_Defined_Data = {
    'Time_Data': {
        'Address': b'\x02',
        'Length': 8,
        'Name': 'Time',
        'Scale': 1e9,
        'Struct': WORD_LONG_LONG
        },
    'Orientation_Angles': {
        'Address': b'\x07',
        'Length': 6,
        'Name': [
            'Heading',
            'Pitch',
            'Roll'
            ],
        'Scale': [
            100,
            100,
            100
            ],
        'Struct': [
            WORD,
            SWORD,
            SWORD
            ]
        },
    'Orientation_Angles_HR': {
        'Address': b'\x08',
        'Length': 12,
        'Name': [
            'Heading',
            'Pitch',
            'Roll'
            ],
        'Scale': [
            1000,
            1000,
            1000
            ],
        'Struct': [
            WORD_LONG,
            SWORD_LONG,
            SWORD_LONG
            ]
        },
    'Quaternions': {
        'Address': b'\x09',
        'Length': 8,
        'Name': [
            'q0',
            'q1',
            'q2',
            'q3'
            ],
        'Scale': [
            10000,
            10000,
            10000,
            10000
            ],
        'Struct': [
            SWORD,
            SWORD,
            SWORD,
            SWORD
            ]
        },
    'Gyro_Data': {
        'Address': b'\x20',
        'Length': 6,
        'Name': [
            'GyroX',
            'GyroY',
            'GyroZ'
            ],
        'Scale': [
            GYRO_SCALE,
            GYRO_SCALE,
            GYRO_SCALE
            ],
        'Struct': [
            SWORD,
            SWORD,
            SWORD
            ]
        },
    'Gyro_Data_HR': {
        'Address': b'\x21',
        'Length': 12,
        'Name': [
            'GyroX',
            'GyroY',
            'GyroZ'
            ],
        'Scale': [
            1e5,
            1e5,
            1e5
            ],
        'Struct': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG
            ]
        },
    'Accelerometer_Data': {
        'Address': b'\x22',
        'Length': 6,
        'Name': [
            'AccX',
            'AccY',
            'AccZ'
            ],
        'Scale': [
            ACC_SCALE,
            ACC_SCALE,
            ACC_SCALE
            ],
        'Struct': [
            SWORD,
            SWORD,
            SWORD
            ]
        },
    'Accelerometer_Data_HR': {
        'Address': b'\x23',
        'Length': 12,
        'Name': [
            'AccX',
            'AccY',
            'AccZ'
            ],
        'Scale': [
            1e6,
            1e6,
            1e6
            ],
        'Struct': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG
            ]
        },
    'Magnetometer_Data': {
        'Address': b'\x24',
        'Length': 6,
        'Name': [
            'MagX',
            'MagY',
            'MagZ'
            ],
        'Scale': [
            0,
            0,
            0
            ],
        'Struct': [
            SWORD,
            SWORD,
            SWORD
            ]
        },
    'Bias-Compensated_Gyro': {
        'Address': b'\x2D',
        'Length': 12,
        'Name': [
            'GyroX',
            'GyroY',
            'GyroZ'
            ],
        'Scale': [
            1e5,
            1e5,
            1e5
            ],
        'Struct': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG
            ]
        },
    'Gyro_Bias': {
        'Address': b'\x2E',
        'Length': 12,
        'Name': [
            'GyroX Bias',
            'GyroY Bias',
            'GyroZ Bias'
            ],
        'Scale': [
            1e5,
            1e5,
            1e5
            ],
        'Struct': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG
            ]
        },
    'Aux_Accelerometer_Data': {
        ### ONLY KERNEL-120 and KERNEL-220
        'Address': b'\x2F',
        'Length': 12,
        'Name': [
            'Aux AccX',
            'Aux AccY',
            'Aux AccZ'
            ],
        'Scale': [
            1e6,
            1e6,
            1e6
            ],
        'Struct': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG
            ]
        },
    'Filtered_low-G_acc_HR': {
        'Address': b'\x91',
        'Length': 12,
        'Name': [
            'AccX',
            'AccY',
            'AccZ'
            ],
        'Scale': [
            1e6,
            1e6,
            1e6
            ],
        'Struct': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG
            ]
        },
    'Filtered_high-G_acc_HR': {
        'Address': b'\x92',
        'Length': 12,
        'Name': [
            'AccX',
            'AccY',
            'AccZ'
            ],
        'Scale': [
            1e6,
            1e6,
            1e6
            ],
        'Struct': [
            SWORD_LONG,
            SWORD_LONG,
            SWORD_LONG
            ]
        },
    'Supply_Voltage': {
        'Address': b'\x50',
        'Length': 2,
        'Name': 'Voltage',
        'Scale': 100,
        'Struct': WORD
        },
    'Temperature': {
        'Address': b'\x52',
        'Length': 2,
        'Name': 'Temperature',
        'Scale': 10,
        'Struct': SWORD
        },
    'Unit_Status_Word': {
        'Address': b'\x53',
        'Length': 2,
        'Name': 'USW',
        'Scale': 1,
        'Struct': WORD
        },
    'Unit_Status_Word_Extended': {
        'Address': b'\x5B',
        'Length': 2,
        'Name': 'USW Extended',
        'Scale': 1,
        'Struct': WORD
        }
    }

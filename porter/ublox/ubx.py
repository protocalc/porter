#### Coversion from UBLOX data types to python struct
U1 = 'B'
I1 = 'b'
U2 = 'H'
I2 = 'h'
U3 = 'BBB'
U4 = 'L'
I4 = 'l'
U5 = 'BBBBB'
R4 = 'f'
R8 = 'd'
CH = 'c'
X1 = 'B'
X2 = 'H' 
X4 = 'I'
U7 = 'BBBBBBB'
X8 = 'II'
U9 = 'BBBBBBBBB'

E1 = U1
E2 = U2
E4 = U4

L = U1


#### UBLOX Payload Type
GET = 0
SET = 1
POLL = 2
PERIODIC = 0
OUTPUT = 0
INPUT = 1


imu_group =  {
    'ref_key': 'dataType',
    '5':{
        'name': 'omega_z',
        'scale': 2**(-12),
        'unit': 'deg/s^2'
    },
    '12':{
        'name': 'gyro_temp',
        'scale': 1e-2,
        'unit': 'C'
    },
    '13':{
        'name': 'omega_y',
        'scale': 2**(-12),
        'unit': 'deg/s^2'
    },
    '14':{
        'name': 'omega_x',
        'scale': 2**(-12),
        'unit': 'deg/s^2'
    },
    '16':{
        'name': 'a_x',
        'scale': 2**(-10),
        'unit': 'm/s^2'
    },
    '17':{
        'name': 'a_y',
        'scale': 2**(-10),
        'unit': 'm/s^2'
    },
    '18':{
        'name': 'a_z',
        'scale': 2**(-10),
        'unit': 'm/s^2'
    }
}

nav_dict = {
    'char': b"\x01",
    'ATT':{
        'name': 'NAV-ATT',
        'type': POLL,
        'char':b'\x05',
        'length': 32,
        'payload':{
            "iTOW": U4,
            "version": U1,
            "reserved0": U3,
            "roll": I4,
            "pitch": I4,
            "heading": I4,
            "accRoll": U4,
            "accPitch": U4,
            "accHeading": U4,
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "version": None,
            "reserved0": None,
            "roll": [1e-5, 'deg'],
            "pitch": [1e-5, 'deg'],
            "heading": [1e-5, 'deg'],
            "accRoll": [1e-5, 'deg'],
            "accPitch": [1e-5, 'deg'],
            "accHeading": [1e-5, 'deg'],
        }
    },
    'CLOCK':{
        'name': 'NAV-CLOCK',
        'type': POLL,
        'char': b'\x01',
        'length': 20,
        'payload': {
            "iTOW": U4, 
            "clkB": I4, 
            "clkD": I4, 
            "tAcc": U4, 
            "fAcc": U4
        },
        'aux': {
            "iTOW": [1, 'ms'], 
            "clkB": [1, 'ns'], 
            "clkD": [1, 'ns/s'], 
            "tAcc": [1, 'ns'], 
            "fAcc": [1, 'ps/s']
        }
    },
    'COV':{
        'name': 'NAV-COV',
        'type': POLL,
        'char': b'\x36',
        'length': 64,
        'payload': {
            "iTOW": U4,
            "version": U1,
            "posCovValid": U1,
            "velCovValid": U1,
            "reserved0": U9,
            "posCovNN": R4,
            "posCovNE": R4,
            "posCovND": R4,
            "posCovEE": R4,
            "posCovED": R4,
            "posCovDD": R4,
            "velCovNN": R4,
            "velCovNE": R4,
            "velCovND": R4,
            "velCovEE": R4,
            "velCovED": R4,
            "velCovDD": R4
        },
        'aux': {
            "iTOW": [1, 'ms'],
            "version": None,
            "posCovValid": None,
            "velCovValid": None,
            "reserved0": None,
            "posCovNN": [1, 'm^2'],
            "posCovNE": [1, 'm^2'],
            "posCovND": [1, 'm^2'],
            "posCovEE": [1, 'm^2'],
            "posCovED": [1, 'm^2'],
            "posCovDD": [1, 'm^2'],
            "velCovNN": [1, 'm^2/s^2'],
            "velCovNE": [1, 'm^2/s^2'],
            "velCovND": [1, 'm^2/s^2'],
            "velCovEE": [1, 'm^2/s^2'],
            "velCovED": [1, 'm^2/s^2'],
            "velCovDD": [1, 'm^2/s^2']
        }
    },
    'DOP': {
        'name': 'NAV-DOP',
        'type': POLL,
        'char': b'\x04',
        'length': 18,
        'payload': {
            "iTOW": U4,
            "gDOP": U2,
            "pDOP": U2,
            "tDOP": U2,
            "vDOP": U2,
            "hDOP": U2,
            "nDOP": U2,
            "eDOP": U2,
        },
        'aux': {
            "iTOW": [1, 'ms'],
            "gDOP": [0.01, None],
            "pDOP": [0.01, None],
            "tDOP": [0.01, None],
            "vDOP": [0.01, None],
            "hDOP": [0.01, None],
            "nDOP": [0.01, None],
            "eDOP": [0.01, None]
        }
    },
    'EELL': {
        'name': 'NAV-EELL',
        'type': POLL,
        'char': b'\x3d',
        'length': 20,
        'payload': {
            "iTOW": U4,
            "version": U1,
            "reserved1": U1,
            "errEllipseOrient": U2,
            "errEllipseMajor": U4,
            "errEllipseMinor": U4,
        },
        'aux': {
            "iTOW": [1, 'ms'],
            "version": None,
            "reserved1": None,
            "errEllipseOrient": [1e-2, 'deg'],
            "errEllipseMajor": [1, 'mm'],
            "errEllipseMinor": [1, 'mm']
        }
    },
    'EOE':{
        'name': 'NAV-EOE',
        'type': PERIODIC,
        'char': b'\x61',
        'length': 4,
        'payload': {
            "iTOW": U4
        },
        'aux': {
            "iTOW": [1, 'ms']
        }
    },
    'GEOFENCE': {
        'name': 'NAV-GEOFENCE',
        'type': POLL,
        'char': b'\x29',
        'length': 'Variable',
        'payload': {
            "iTOW": U4,
            "version": U1,
            "status": U1,
            "numFences": U1,
            "combState": U1,
            "group": (
                "numFences",
                {"state": U1, "reserved1": U1},  # repeating group * numFences
            ),
        },
        'aux': {
            "iTOW": [1, 'ms'],
            "version": None,
            "status": None,
            "numFences": None,
            "combState": None,
            "group": {"state": None, "reserved1": None}
        }
    },
    'HPPOSECEF': {
        'name': 'NAV-HPPOSECEF',
        'type': POLL,
        'char': b'\x13',
        'length': 28,
        'payload': {
            "version": U1,
            "reserved1": U3,
            "iTOW": U4,
            "ecefX": I4,
            "ecefY": I4,
            "ecefZ": I4,
            "ecefXHp": I1,
            "ecefYHp": I1,
            "ecefZHp": I1,
            "flags": (X1, {
                'invalidECEF': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                }
            }),
            "pAcc": U4,
        },
        'aux': {
            "version": None,
            "reserved1": None,
            "iTOW": [1, 'ms'],
            "ecefX": [1, 'cm'],
            "ecefY": [1, 'cm'],
            "ecefZ": [1, 'cm'],
            "ecefXHp": [0.1, 'mm'],
            "ecefYHp": [0.1, 'mm'],
            "ecefZHp": [0.1, 'mm'],
            "flags": None,
            "pAcc": [0.1, 'mm'],
        }
    },
    'HPPOSLLH': {
        'name': 'NAV-HPPOSLLH',
        'type': POLL,
        'char': b'\x14',
        'length': 36,
        'payload': {
            "version": U1,
            "reserved1": U2,
            "flags": (X1, {
                'invalidECEF': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                }
            }),
            "iTOW": U4,
            "lon": I4,
            "lat": I4,
            "height": I4,
            "hMSL": I4,
            "lonHp": I1,
            "latHp": I1,
            "heightHp": I1,
            "hMSLHp": I1,
            "hAcc": U4,
            "vAcc": U4,
        },
        'aux': {
            "version": None,
            "reserved1": None,
            "flags": None,
            "iTOW": [1, None],
            "lon": [1e-7, 'deg'],
            "lat": [1e-7, 'deg'],
            "height": [1, 'mm'],
            "hMSL": [1, 'mm'],
            "lonHp": [1e-9, 'deg'],
            "latHp": [1e-9, 'deg'],
            "heightHp": [0.1, 'mm'],
            "hMSLHp": [0.1, 'mm'],
            "hAcc": [0.1, 'mm'],
            "vAcc": [0.1, 'mm'],
        }
    },
    'ORB':{
        'name': 'NAV-ORB',
        'type': POLL,
        'char': b'\x34',
        'length': 'Variable',
        'payload': {
            "iTOW": U4,
            "version": U1,
            "numSv": U1,
            "reserved1": U2,
            "group": (
                "numSv",
                {  # repeating group * numSv
                    "gnssId": U1,
                    "svId": U1,
                    "svFlag": (X1, {
                        'health': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 2
                        }, 
                        'visibility': {
                            'type': 'unsigned',
                            'start': 2,
                            'length': 2
                        }, 
                    }),
                    "eph": (X1, {
                        'ephUsability': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 5
                        }, 
                        'ephSource': {
                            'type': 'unsigned',
                            'start': 5,
                            'length': 3
                        }
                    }),
                    "alm": (X1, {
                        'almUsability': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 5
                        }, 
                        'almSource': {
                            'type': 'unsigned',
                            'start': 5,
                            'length': 3
                        }
                    }),
                    "otherOrb": (X1, {
                        'anoAopUsability': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 5
                        }, 
                        'type': {
                            'type': 'unsigned',
                            'start': 5,
                            'length': 3
                        }
                    }),
                },
            ),
        }, 
        'aux': {
            "iTOW": [1, 'ms'],
            "version": None,
            "numSv": None,
            "reserved1": None,
            "group": {
                "gnssId": None,
                "svId": None,
                "svFlag": None,
                "eph": None,
                "alm": None,
                "otherOrb": None,
            }
        }
    },
    'POSECEF':{
        'name': 'NAV-POSECEF',
        'type': POLL,
        'char': b'\x01',
        'lenght': 20,
        'payload': {
            "iTOW": U4, 
            "ecefX": I4, 
            "ecefY": I4, 
            "ecefZ": I4, 
            "pAcc": U4
        },
        'aux': {
            "iTOW": [1, 'ms'], 
            "ecefX": [1, 'cm'], 
            "ecefY": [1, 'cm'], 
            "ecefZ": [1, 'cm'], 
            "pAcc": [1, 'cm']
        } 
    },
    'POSLLH': {
        'name': 'NAV-POSLLH',
        'type': POLL,
        'char': b'\x02',
        'lenght': 28,
        'payload':{
            "iTOW": U4,
            "lon": I4,
            "lat": I4,
            "height": I4,
            "hMSL": I4,
            "hAcc": U4,
            "vAcc": U4
        }, 
        'aux':{
            "iTOW": [1, 'ms'],
            "lon": [1e-7, 'deg'],
            "lat": [1e-7, 'deg'],
            "height": [1, 'mm'],
            "hMSL": [1, 'mm'],
            "hAcc": [1, 'mm'],
            "vAcc": [1, 'mm']
        }
    },
    'PVT':{
        'name': 'NAV-PVT',
        'type': POLL,
        'char': b'\x07',
        'lenght': 92,
        'payload':{
            "iTOW": U4,
            "year": U2,
            "month": U1,
            "day": U1,
            "hour": U1,
            "min": U1,
            "second": U1,
            "valid": (X1, {
                'validDate': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'validTime': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'FullyResolved': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                },
                'validMag': {
                    'type': 'unsigned',
                    'start': 3,
                    'length': 1
                }
            }),
            "tAcc": U4,
            "nano": I4,
            "fixType": U1,
            "flags": (X1, {
                'gnssFixOK': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'diffSoln': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'psmState': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 3
                },
                'headVehValid': {
                    'type': 'unsigned',
                    'start': 5,
                    'length': 1
                }, 
                'carrSoln': {
                    'type': 'unsigned',
                    'start': 6,
                    'length': 2
                }
            }),
            "flags2": (X1, {
                'confirmedAvai': {
                    'type': 'unsigned',
                    'start': 5,
                    'length': 1
                },
                'confirmedDate': {
                    'type': 'unsigned',
                    'start': 6,
                    'length': 1
                },
                'confirmedTime': {
                    'type': 'unsigned',
                    'start': 7,
                    'length': 1
                }
            }),
            "numSV": U1,
            "lon": I4,
            "lat": I4,
            "height": I4,
            "hMSL": I4,
            "hAcc": U4,
            "vAcc": U4,
            "velN": I4,
            "velE": I4,
            "velD": I4,
            "gSpeed": I4,
            "headMot": I4,
            "sAcc": U4,
            "headAcc": U4,
            "pDOP": U2,
            "flags3": (X1, {
                'invalidLlh': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                }
            }),
            "reserved1": U5,
            "headVeh": I4,
            "magDec": I2,
            "magAcc": U2,
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "year": [1, 'year'],
            "month": [1, 'month'],
            "day": [1, 'day'],
            "hour": [1, 'h'],
            "min": [1, 'min'],
            "second": [1, 's'],
            "valid": None,
            "tAcc": [1, 'ns'],
            "nano": [1, 'ns'],
            "fixType": None,
            "flags": None,
            "flags2": None,
            "numSV": None,
            "lon": [1e-7, 'deg'],
            "lat": [1e-7, 'deg'],
            "height": [1, 'mm'],
            "hMSL": [1, 'mm'],
            "hAcc": [1, 'mm'],
            "vAcc": [1, 'mm'],
            "velN": [1, 'mm/s'],
            "velE": [1, 'mm/s'],
            "velD": [1, 'mm/s'],
            "gSpeed": [1, 'mm/s'],
            "headMot": [1e-5, 'deg'],
            "sAcc": [1, 'mm/s'],
            "headAcc": [1e-5, 'deg'],
            "pDOP": [0.01, None],
            "flags3": None,
            "reserved1": None,
            "headVeh": [1e-5, 'deg'],
            "magDec": [1e-2, 'deg'],
            "magAcc": [1e-2, 'deg'],
        }
    }, 
    'RELPOSNED':{
        'name': 'NAV-RELPOSNED',
        'type': POLL,
        'char': b'\x3c',
        'lenght': 64,
        'payload':{
            "version": U1,
            "reserved0": U1,
            "refStationID": U2,
            "iTOW": U4,
            "relPosN": I4,
            "relPosE": I4,
            "relPosD": I4,
            "relPosLength": I4,
            "relPosHeading": I4,
            "reserved1": U4,
            "relPosHPN": I1,
            "relPosHPE": I1,
            "relPosHPD": I1,
            "relPosHPLength": I1,
            "accN": U4,
            "accE": U4,
            "accD": U4,
            "accLength": U4,
            "accHeading": U4,
            "reserved2": U4,
            "flags": (X4, {
                'gnssFixOK': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'diffSoln': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'relPosValid': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                },
                'carrSoln': {
                    'type': 'unsigned',
                    'start': 3,
                    'length': 2
                },
                'isMoving': {
                    'type': 'unsigned',
                    'start': 5,
                    'length': 1
                },
                'refPosMiss': {
                    'type': 'unsigned',
                    'start': 6,
                    'length': 1
                },
                'refObsMiss': {
                    'type': 'unsigned',
                    'start': 7,
                    'length': 1
                },
                'relPosHeadingValid': {
                    'type': 'unsigned',
                    'start': 8,
                    'length': 1
                },
                'relPosNormalized': {
                    'type': 'unsigned',
                    'start': 9,
                    'length': 1
                }
            }),
        },
        'aux':{
            "version": None,
            "reserved0": None,
            "refStationID": None,
            "iTOW": [1, 'ms'],
            "relPosN": [1, 'cm'],
            "relPosE": [1, 'cm'],
            "relPosD": [1, 'cm'],
            "relPosLength": [1, 'cm'],
            "relPosHeading": [1e-5, 'deg'],
            "reserved1": None,
            "relPosHPN": [1, 'mm'],
            "relPosHPE": [1, 'mm'],
            "relPosHPD": [1, 'mm'],
            "relPosHPLength": [1, 'mm'],
            "accN": [1, 'mm'],
            "accE": [1, 'mm'],
            "accD": [1, 'mm'],
            "accLength": [1, 'mm'],
            "accHeading": [1e-5, 'deg'],
            "reserved2": None,
            "flags": {
                'gnssFixOK': None,
                'diffSoln': None,
                'relPosValid': None,
                'carrSoln': None,
                'isMoving': None,
                'refPosMiss': None,
                'refObsMiss': None,
                'relPosHeadingValid': None,
                'relPosNormalized': None
            },
        }
    },
    'SAT':{
        'name': 'NAV-SAT',
        'type': POLL, 
        'char': b'\x35',
        'length': 'Variable',
        'payload':{
            "iTOW": U4,
            "version": U1,
            "numCh": U1,
            "reserved1": U2,
            "group": (
                "numCh",
                {
                    "gnssId": U1,
                    "svId": U1,
                    "cno": U1,
                    "elev": I1,
                    "azim": I2,
                    "prRes": I2,
                    "flags": (X4, {
                        'qualityInd': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 3
                        },
                        'svUsed': {
                            'type': 'unsigned',
                            'start': 3,
                            'length': 1
                        },
                        'health': {
                            'type': 'unsigned',
                            'start': 4,
                            'length': 2
                        },
                        'diffCorr': {
                            'type': 'unsigned',
                            'start': 6,
                            'length': 1
                        },
                        'smoothed': {
                            'type': 'unsigned',
                            'start': 7,
                            'length': 1
                        },
                        'orbitSource': {
                            'type': 'unsigned',
                            'start': 8,
                            'length': 3
                        },
                        'ephAvail': {
                            'type': 'unsigned',
                            'start': 11,
                            'length': 1
                        },
                        'almAvail': {
                            'type': 'unsigned',
                            'start': 12,
                            'length': 1
                        },
                        'anoAvail': {
                            'type': 'unsigned',
                            'start': 13,
                            'length': 1
                        },
                        'aopAvail': {
                            'type': 'unsigned',
                            'start': 14,
                            'length': 1
                        },
                        'sbasCorrUsed': {
                            'type': 'unsigned',
                            'start': 16,
                            'length': 1
                        },
                        'rtcmCorrUsed': {
                            'type': 'unsigned',
                            'start': 17,
                            'length': 1
                        },
                        'slasCorrUsed': {
                            'type': 'unsigned',
                            'start': 18,
                            'length': 1
                        },
                        'spartnCorrUsed': {
                            'type': 'unsigned',
                            'start': 19,
                            'length': 1
                        },
                        'prCorrUsed': {
                            'type': 'unsigned',
                            'start': 20,
                            'length': 1
                        },
                        'crCorrUsed': {
                            'type': 'unsigned',
                            'start': 21,
                            'length': 1
                        },
                        'doCorrUsed': {
                            'type': 'unsigned',
                            'start': 22,
                            'length': 1
                        }
                    })
                },
            ),
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "version": None,
            "numCh": None,
            "reserved1": None,
            "group": {
                "gnssId": None,
                "svId": None,
                "cno": [1, 'dBHz'],
                "elev": [1, 'deg'],
                "azim": [1, 'deg'],
                "prRes": [0.1, 'm'],
                "flags": {
                    'qualityInd': None,
                    'svUsed': None,
                    'health': None,
                    'diffCorr': None,
                    'smoothed': None,
                    'orbitSource': None,
                    'ephAvail': None,
                    'almAvail': None,
                    'anoAvail': None,
                    'aopAvail': None,
                    'sbasCorrUsed': None,
                    'rtcmCorrUsed': None,
                    'slasCorrUsed': None,
                    'spartnCorrUsed': None,
                    'prCorrUsed': None,
                    'crCorrUsed': None,
                    'doCorrUsed': None
                }
            },
        },
    },
    'SBAS':{
        'name': 'NAV-SBAS',
        'type': POLL,
        'char': b'\x32',
        'length': 'Variable',
        'payload':{
            "iTOW": U4,
            "geo": U1,
            "mode:": U1,
            "sys": I1,
            "service": (X1, {
                'Ranging': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'Corrections': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'Integrity': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                },
                'Testmode': {
                    'type': 'unsigned',
                    'start': 3,
                    'length': 1
                },
                'Bad': {
                    'type': 'unsigned',
                    'start': 4,
                    'length': 1
                }
            }),
            "cnt": U1,
            "StatusFlags": (X1, {
                'integrityUsed': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 2
                },
            }),
            "reserved0": U3,
            "group": (
                "cnt",
                {
                    "svid": U1,
                    "flags": U1,
                    "udre": U1,
                    "svSys": U1,
                    "svService": U1,
                    "reserved1": U1,
                    "prc": I2,
                    "reserved2": U2,
                    "ic": I2,
                },
            ),
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "geo": None,
            "mode:": None,
            "sys": None,
            "service": {
                'Ranging': None,
                'Corrections': None,
                'Integrity': None,
                'Testmode': None,
                'Bad': None
            },
            "cnt": None,
            "StatusFlags": {
                'integrityUsed': None,
            },
            "reserved0": None,
            "group":{
                "svid": None,
                "flags": None,
                "udre": None,
                "svSys": None,
                "svService": None,
                "reserved1": None,
                "prc": [1, 'cm'],
                "reserved2": None,
                "ic": [1, 'cm'],
            },            
        },
    },
    'SIG':{
        'name': 'NAV-SIG',
        'type': POLL,
        'char': b'\x43',
        'lenght': 'Variable',
        'payload': {
            "iTOW": U4,
            "version": U1,
            "numSigs": U1,
            "reserved0": U2,
            "group": (
                "numSigs",
                {  # repeating group * numSigs
                    "gnssId": U1,
                    "svId": U1,
                    "sigId": U1,
                    "freqId": U1,
                    "prRes": I2,
                    "cno": U1,
                    "qualityInd": U1,
                    "corrSource": U1,
                    "ionoModel": U1,
                    "sigFlags": (X2, {
                        'health': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 2
                        },
                        'prSmoothed': {
                            'type': 'unsigned',
                            'start': 2,
                            'length': 1
                        },
                        'prUsed': {
                            'type': 'unsigned',
                            'start': 3,
                            'length': 1
                        },
                        'crUsed': {
                            'type': 'unsigned',
                            'start': 4,
                            'length': 1
                        },
                        'doUsed': {
                            'type': 'unsigned',
                            'start': 5,
                            'length': 1
                        },
                        'prCorrUsed': {
                            'type': 'unsigned',
                            'start': 6,
                            'length': 1
                        },
                        'crCorrUsed': {
                            'type': 'unsigned',
                            'start': 7,
                            'length': 1
                        },
                        'doCorrUsed': {
                            'type': 'unsigned',
                            'start': 8,
                            'length': 1
                        }
                    }),
                    "reserved1": U4,
                },
            ),
        },
        'aux': {
            "iTOW": [1, 'ms'],
            "version": None,
            "numSigs": None,
            "reserved0": None,
            "group": (
                "numSigs",
                {  # repeating group * numSigs
                    "gnssId": None,
                    "svId": None,
                    "sigId": None,
                    "freqId": None,
                    "prRes": [0.1, 'm'],
                    "cno": [1, 'dBHz'],
                    "qualityInd": None,
                    "corrSource": None,
                    "ionoModel": None,
                    "sigFlags": {
                        'health': None,
                        'prSmoothed': None,
                        'prUsed': None,
                        'crUsed': None,
                        'doUsed': None,
                        'prCorrUsed': None,
                        'crCorrUsed': None,
                        'doCorrUsed': None
                    },
                    "reserved1": None,
                },
            ),
        }
    },
    'SLAS': {
        'name': 'NAV-SLAS',
        'type': POLL,
        'char': b'\x42',
        'length': 'Variable',
        'payload':{
            "iTOW": U4,
            "version": U1,
            "reserved1": U3,
            "gmsLon": I4,
            "gmsLat": I4,
            "gmsCode": U1,
            "qzssSvId": U1,
            "serviceFlags": (X1, {
                'gmsAvailable': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'qzssSvAvailable': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'testMode': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                },
            }),
            "cnt": U1,
            "group": (
                "cnt",
                {  # repeating group * cnt
                    "gnssID": U1,
                    "svId": U1,
                    "reserved2": U1,
                    "reserved3": U3,
                    "prc": I2,
                },
            ),
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "version": None,
            "reserved1": None,
            "gmsLon": [1e-3, 'deg'],
            "gmsLat": [1e-3, 'deg'],
            "gmsCode": None,
            "qzssSvId": None,
            "serviceFlags": {
                'gmsAvailable': None,
                'qzssSvAvailable': None,
                'testMode': None
            },
            "cnt": None,
            "group":{
                "gnssID": None,
                "svId": None,
                "reserved2": None,
                "reserved3": None,
                "prc": [1, 'cm'],
            },
        }
    },
    'STATUS':{
        'name': 'NAV-STATUS',
        'type': POLL,
        'char': b'\x03',
        'length': 16, 
        'payload':{
            "iTOW": U4,
            "gpsFix": U1,
            "flags": (X1, {
                'gpsFixOk': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'diffSolN': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'wknSet': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                },
                'towSet': {
                    'type': 'unsigned',
                    'start': 3,
                    'length': 1
                }
            }),
            "fixStat": (X1, {
                'diffCorr': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'carrSolnValid': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'mapMatching': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 2
                }
            }),
            "flags2": (X1, {
                'psmState': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 2
                },
                'spoofDetState': {
                    'type': 'unsigned',
                    'start': 3,
                    'length': 2
                },
                'carrSoln': {
                    'type': 'unsigned',
                    'start': 6,
                    'length': 2
                }
            }),
            "ttff": U4,
            "msss": U4
        },
        'aux':{    
            "iTOW": [1, 'ms'],
            "gpsFix": None,
            "flags": {
                'gpsFixOk': None,
                'diffSolN': None,
                'wknSet': None,
                'towSet': None
            },
            "fixStat": {
                'diffCorr': None,
                'carrSolnValid': None,
                'mapMatching': None
            },
            "flags2": {
                'psmState': None,
                'spoofDetState': None,
                'carrSoln': None
            },
            "ttff": [1, 'ms'],
            "msss": [1, 'ms']
        },
    },
    'SVIN':{
        'name': 'NAV-SVIN',
        'type': POLL,
        'char':b'\x3b',
        'length': 40,
        'payload':{
            "version": U1,
            "reserved0": U3,
            "iTOW": U4,
            "dur": U4,
            "meanX": I4,
            "meanY": I4,
            "meanZ": I4,
            "meanXHP": I1,
            "meanYHP": I1,
            "meanZHP": I1,
            "reserved1": U1,
            "meanAcc": U4,
            "obs": U4,
            "valid": U1,
            "active": U1,
            "reserved2": U2,
        },
        'aux':{
            "version": None,
            "reserved0": None,
            "iTOW": [1, 'ms'],
            "dur": [1, 's'],
            "meanX": [1, 'cm'],
            "meanY": [1, 'cm'],
            "meanZ": [1, 'cm'],
            "meanXHP": [0.01, 'cm'],
            "meanYHP": [0.01, 'cm'],
            "meanZHP": [0.01, 'cm'],
            "reserved1": None,
            "meanAcc":[0.01, 'cm'],
            "obs": None,
            "valid": None,
            "active": None,
            "reserved2": None,
        }
    },
    'TIMEBDS':{
        'name': 'NAV-TIMEBDS',
        'type': POLL,
        'char': b'\x24',
        'length': 20,
        'payload':{
            "iTOW": U4,
            "SOW": U4,
            "fSOW": I4,
            "week": I2,
            "leapS": I1,
            "valid": (X1, {
                'sowValid': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'weekValid': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'leapSValid': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                }
            }),
            "tAcc": U4
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "SOW": [1, 's'],
            "fSOW": [1, 'ns'],
            "week": None,
            "leapS": [1, 's'],
            "valid": {
                'sowValid': None,
                'weekValid': None,
                'leapSValid': None
            },
            "tAcc": [1, 'ns']
        }
    },
    'TIMEGAL':{
        'name': 'NAV-TIMEGAL',
        'type': POLL,
        'char': b'\x25',
        'length': 20,
        'payload':{
            "iTOW": U4,
            "GalTOW": U4,
            "fGalTOW": I4,
            "galWno": I2,
            "leapS": I1,
            "valid": (X1, {
                'galTowValid': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'galWnoValid': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'leapSValid': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                }
            }),
            "tAcc": U4
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "galTOW": [1, 's'],
            "fgalTOW": [1, 'ns'],
            "galWno": None,
            "leapS": [1, 's'],
            "valid": {
                'galTowValid': None,
                'galWnoValid': None,
                'leapSValid': None
            },
            "tAcc": [1, 'ns']
        }
    },
    'TIMEGLO':{
        'name': 'NAV-TIMEGLO',
        'type': POLL,
        'char': b'\x23',
        'length': 20,
        'payload':{
            "iTOW": U4,
            "TOD": U4,
            "fTOD": I4,
            "Nt": U2,
            "N4": U1,
            "valid": (X1, {
                'todValid': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'dateValid': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
            }),
            "tAcc": U4
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "TOD": [1, 's'],
            "fTOD": [1, 'ns'],
            "Nt": [1, 'days'],
            "N4": None,
            "valid": {
                'todValid': None,
                'dateValid': None
            },
            "tAcc": [1, 'ns']
        }
    },
    'TIMEGPS':{
        'name': 'NAV-TIMEGPS',
        'type': POLL,
        'char': b'\x20',
        'length': 16,
        'payload':{
            "iTOW": U4,
            "fTOW": I4,
            "week": I2,
            "leapS": I1,
            "valid": (X1, {
                'towValid': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'weekValid': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'leapSValid': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                }
            }),
            "tAcc": U4
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "fTOW": [1, 'ns'],
            "week": None,
            "leapS": [1, 's'],
            "valid": {
                'towValid': None,
                'weekValid': None,
                'leapSValid': None
            },
            "tAcc": [1, 'ns']
        }
    },
    'TIMELS':{
        'name': 'NAV-TIMELS',
        'type': POLL,
        'char': b'\x26',
        'length': 24,
        'payload':{
            "iTOW": U4,
            "version": U1,
            "reserved1": U3,
            "srcOfCurrLs": U1,
            "currLs": I1,
            "srcOfLsChange": U1,
            "lsChange": I1,
            "timeToLsEvent": I4,
            "dateOfLsGpsWn": U2,
            "dateOfLsGpsDn": U2,
            "reserved2": U3,
            "valid": (X1, {
                'validCurrLs': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'validTimeToLsEvent': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                }
            })
        },
        'aux':{
            "iTOW": [1, 'ms'],
            "version": None,
            "reserved1": None,
            "srcOfCurrLs": None,
            "currLs": [1, 's'],
            "srcOfLsChange": U1,
            "lsChange": [1, 's'],
            "timeToLsEvent": [1, 's'],
            "dateOfLsGpsWn": None,
            "dateOfLsGpsDn": None,
            "reserved2": None,
            "valid": {
                'validCurrLs': None,
                'validTimeToLsEvent': None
            }
        }
    },
    'TIMEQZSS':{
        'name': 'NAV-TIMEQZSS',
        'type': POLL,
        'char': b'\x27',
        'length': 20,
        'payload':{
            "iTOW": U4,
            "qzssTow": U4,
            "fQzssTow": I4,
            "qzssWno": I2,
            "leapS": I1,
            "valid": (X1, {
                'qzssTowValid': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'qzssWnoValid': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'leapSValid': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                }
            }),
            "tAcc": U4,
        },
        'aux': {
            "iTOW": [1, 'ms'],
            "qzssTow": [1, 's'],
            "fQzssTow": [1, 'ns'],
            "qzssWno": None,
            "leapS": [1, 's'],
            "valid": {
                'qzssTowValid': None,
                'qzssWnoValid': None,
                'leapSValid': None
            },
            "tAcc": [1, 'ns'],
        }
    }, 
    'TIMEUTC':{
        'name': 'NAV-TIMEUTC',
        'type': POLL, 
        'char': b'\21',
        'length': 20,
        'payload':{
            "iTOW": U4,
            "tAcc": U4,
            "nano": I4,
            "year": U2,
            "month": U1,
            "day": U1,
            "hour": U1,
            "min": U1,
            "sec": U1,
            "validflags": (X1, {
                'validTow': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'validWKN': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'validUTC': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                },
                'utcStandard': {
                    'type': 'unsigned',
                    'start': 4,
                    'length': 4
                },
            })
        }, 
        'aux': {
            "iTOW": [1, 'ms'],
            "tAcc": [1, 'ns'],
            "nano": [1, 'ns'],
            "year": [1, 'y'],
            "month": [1, 'month'],
            "day": [1, 'day'],
            "hour": [1, 'h'],
            "min": [1, 'min'],
            "sec": [1, 's'],
            "validflags": {
                'validTow': None,
                'validWKN': None,
                'validUTC': None,
                'utcStandard': None,
            }
        }
    }, 
    'VELECEF': {
        'name': 'NAV-VELECEF',
        'type': POLL,
        'char': b'\x11',
        'length': 20, 
        'payload': {
            "iTOW": U4, 
            "ecefVX": I4, 
            "ecefVY": I4, 
            "ecefVZ": I4, 
            "sAcc": U4
        },
        'aux': {
            "iTOW": [1, 'ms'], 
            "ecefVX": [1, 'cm/s'], 
            "ecefVY": [1, 'cm/s'], 
            "ecefVZ": [1, 'cm/s'], 
            "sAcc": [1,'cm/s']
        }
    }, 
    'VELNED': {
        'name': 'NAV-VELNED',
        'type': POLL,
        'char': b'\x12',
        'length': 36, 
        'payload': {
            "iTOW": U4,
            "velN": I4,
            "velE": I4,
            "velD": I4,
            "speed": U4,
            "gSpeed": U4,
            "heading": I4,
            "sAcc": U4,
            "cAcc": U4
        }, 
        'aux': {
            "iTOW": [1, 'ms'],
            "velN": [1, 'cm/s'],
            "velE": [1, 'cm/s'],
            "velD": [1, 'cm/s'],
            "speed": [1, 'cm/s'],
            "gSpeed": [1, 'cm/s'],
            "heading": [1e-5, 'deg'],
            "sAcc": [1, 'cm/s'],
            "cAcc": [1e-5, 'deg']
        },
    }
}

esf_dict = {
    'char': b'\x10',
    'ALG': {
        'name': 'ESF-ALG',
        'char': b'\x14',
        'type': POLL,
        'length': 16,
        'payload': {
            "iTOW": U4,
            "version": U1,
            "flags": (X1, {
                'autoMntAlgOn': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'status': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 3
                }
            }),
            "error": (X1, {
                'tiltAlgError': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'yawAlgError': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'AngleError': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                }
            }),
            "reserved1": U1,
            "yaw": U4,
            "pitch": I2,
            "roll": I2
        },
        'aux': {
            "iTOW": [1, 'ms'],
            "version": None,
            "flags": {
                'autoMntAlgOn': None,
                'status': None
            },
            "error": {
                'tiltAlgError': None,
                'yawAlgError': None,
                'AngleError': None,
            },
            "reserved1": None,
            "yaw": [1e-2, 'deg'],
            "pitch": [1e-2, 'deg'],
            "roll": [1e-2, 'deg']
        }
    }, 
    'INS': {
        'name': 'ESF-INS',
        'char': b'\x15',
        'type': POLL,
        'length': 36,
        'payload': {
            "bitfield0": (X4, {
                'version': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 8
                },
                'xAngRateValid': {
                    'type': 'unsigned',
                    'start': 8,
                    'length': 1
                },
                'yAngRateValid': {
                    'type': 'unsigned',
                    'start': 9,
                    'length': 1
                },
                'zAngRateValid': {
                    'type': 'unsigned',
                    'start': 10,
                    'length': 1
                },
                'xAccelValid': {
                    'type': 'unsigned',
                    'start': 11,
                    'length': 1
                },
                'yAccelValid': {
                    'type': 'unsigned',
                    'start': 12,
                    'length': 1
                },
                'zAccelValid': {
                    'type': 'unsigned',
                    'start': 13,
                    'length': 1
                },
            }),
            "reserved1": U4,
            "iTOW": U4,
            "xAngRate": I4,
            "yAngRate": I4,
            "zAngRate": I4,
            "xAccel": I4,
            "yAccel": I4,
            "zAccel": I4,
        },
        'aux': {
            "bitfield0": {
                'version': None,
                'xAngRateValid': None,
                'yAngRateValid': None,
                'zAngRateValid': None,
                'xAccelValid': None,
                'yAccelValid': None,
                'zAccelValid': None
            },
            "reserved1": None,
            "iTOW": [1, 'ms'],
            "xAngRate": [1e-3, 'deg/2'],
            "yAngRate": [1e-3, 'deg/2'],
            "zAngRate": [1e-3, 'deg/2'],
            "xAccel": [1e-2, 'm/s^2'],
            "yAccel": [1e-2, 'm/s^2'],
            "zAccel": [1e-2, 'm/s^2'],
        }
    },
    'MEAS': {
        'name': 'ESF-MEAS',
        'char': b'\x02',
        'type': POLL,
        'length': 'Variable',
        'payload':{
            "timeTag": U4,
            "flags": (X1, {
                'timeMarkSent': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 2
                },
                'timeMarkEdge': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                },
                'calibTtagValid': {
                    'type': 'unsigned',
                    'start': 3,
                    'length': 1
                },
                'numMeas': {
                    'type': 'unsigned',
                    'start': 11,
                    'length': 5
                }
            }),
            "id": U2,
            "group": (
                'numMeas',
                { 
                    "data": (X4, {
                        'dataField': {
                            'type': 'signed',
                            'start': 0,
                            'length': 24
                        },
                        'dataType': {
                            'type': 'unsigned',
                            'start': 24,
                            'length': 6
                        },
                    }),
                }
            ),
            "calibTtag": U4,
        },
        'aux':{
            "timeTag": None,
            "flags": {
                'timeMarkSent': None,
                'timeMarkEdge': None,
                'calibTtagValid': None,
                'numMeas': None
            },
            "id": None,
            "group": {
                'data': imu_group
            },
            "calibTtag": None,
        }
    }, 
    'RAW': {
        'name': 'ESF-RAW',
        'char': b'\x03',
        'type': POLL,
        'length': 'Variable',
        'payload':{
            "reserved0": U4,
            "group": (
                None,
                { 
                    "data": (X4, {
                        'dataField': {
                            'type': 'signed',
                            'start': 0,
                            'length': 24
                        },
                        'dataType': {
                            'type': 'unsigned',
                            'start': 24,
                            'length': 8
                        },
                    }),
                    "sTtag": U4,
                }
            )
        },
        'aux':{
            "reserved0": None,            
            "group": {
                'data': imu_group,
                'sTtag': None
            },
        }
    },
    'STATUS':{
        'name': 'ESF-STATUS',
        'char': b'\x10',
        'type': POLL,
        'lenght': 'Variable',
        'payload': {
            "iTOW": U4,
            "version": U1,
            "reserved0": U7,
            "fusionMode": U1,
            "reserved1": U2,
            "numSens": U1,
            "group": (
                "numSens",
                {
                    "sensStatus1": (X1, {
                        'type': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 6
                        },
                        'used': {
                            'type': 'unsigned',
                            'start': 6,
                            'length': 1
                        },
                        'ready': {
                            'type': 'unsigned',
                            'start': 7,
                            'length': 1
                        }
                    }),
                    "sensStatus2": (X1, {
                        'CalibStatus': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 2
                        },
                        'TimeStatus': {
                            'type': 'unsigned',
                            'start': 2,
                            'length': 2
                        }
                    }),
                    "freq": U1,
                    "faults": (X1, {
                        'badMeas': {
                            'type': 'unsigned',
                            'start': 0,
                            'length': 1
                        },
                        'badTTag': {
                            'type': 'unsigned',
                            'start': 1,
                            'length': 1
                        },
                        'missingMeas': {
                            'type': 'unsigned',
                            'start': 2,
                            'length': 1
                        },
                        'noisyMeas': {
                            'type': 'unsigned',
                            'start': 3,
                            'length': 1
                        }
                    })
                },
            )
        },
        'aux': {
            "iTOW": [1, 'ms'],
            "version": None,
            "reserved0": None,
            "fusionMode": None,
            "reserved1": None,
            "numSens": None,
            "group": (
                "numCh",
                {
                    "sensStatus1": {
                        'type': None,
                        'used': None,
                        'ready': None
                    },
                    "sensStatus2": {
                        'CalibStatus': None,
                        'TimeStatus': None
                    },
                    "freq": [1, 'Hz'],
                    "faults": {
                        'badMeas': None,
                        'badTTag': None,
                        'missingMeas': None,
                        'noisyMeas': None
                    }
                }
            )
        }
    }
}

ack_dict = {
    'char': b'\x05',
    'ACK': {
        'name': 'ACK-ACK',
        'char': b'\x01',
        'type': OUTPUT,
        'length': 2,
        'payload':{
            "clsID": U1, 
            "msgID": U1
        },
        'aux':{
            "clsID": None, 
            "msgID": None
        }
    },
    'NAK': {
        'name': 'ACK-NAK',
        'char': b'\x00',
        'type': OUTPUT,
        'length': 2,
        'payload':{
            "clsID": U1, 
            "msgID": U1
        },
        'aux':{
            "clsID": None, 
            "msgID": None
        }
    }
}

cfg_dict = {
    'char': b'\x06',
    'RST': {
        'name': 'CFG_RST',
        'char': b'\x04',
        'type': INPUT, 
        'length': 4,
        'payload':{
            "navBbrMask": (X2, {
                'eph': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'alm': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'health': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                },
                'klob': {
                    'type': 'unsigned',
                    'start': 3,
                    'length': 1
                },
                'pos': {
                    'type': 'unsigned',
                    'start': 4,
                    'length': 1
                },
                'clkd': {
                    'type': 'unsigned',
                    'start': 5,
                    'length': 1
                },
                'osc': {
                    'type': 'unsigned',
                    'start': 6,
                    'length': 1
                },
                'utc': {
                    'type': 'unsigned',
                    'start': 7,
                    'length': 1
                },
                'rtc': {
                    'type': 'unsigned',
                    'start': 8,
                    'length': 1
                },
                'aop': {
                    'type': 'unsigned',
                    'start': 15,
                    'length': 1
                }
            }),
            "resetMode": U1,
            "reserved0": U1,
        },
        'aux':{
            "navBbrMask": {
                'eph': None,
                'alm': None,
                'health': None,
                'klob': None,
                'pos': None,
                'clkd': None,
                'osc': None,
                'utc': None,
                'rtc': None,
                'aop': None
            },
            "resetMode": None,
            "reserved0": None,
        }
    },
    'VALDEL':{
        'name': 'CFG-VALDEL',
        'char': b'\x8c',
        'type': INPUT,
        'length': 'Variable',
        'payload': {
            "version": U1,  
            "layers": (X1, {
                'bbr': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'flash': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                }
            }),
            "transaction": (X1, {
                'action': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 2
                }
            }), 
            "reserved0": U1,
            "group": ("None", {
                "keys": U4
            })
        },
        'aux': {
            "version": None,  
            "layers": {
                'bbr': None,
                'flash': None
            },
            "transaction": {
                'action': None
            }, 
            "reserved0": None,
            "group": {
                "keys": None
            }
        }
    },
    'VALGET': {
        'name': 'CFG-VALGET',
        'char': b'\x8b',
        'type': POLL,
        'length': 'Variable',
        'payload': {
            "version": U1,  
            "layers": U1, 
            "position": U2,
            "group": ("None", {
                "keys": U4
            })
        },
        'aux': {
            "version": None,  
            "layers": None,
            "position": None,
            "group": {
                "keys": None
            }
        }
    },
    'VALSET':{
        'name': 'CFG-VALSET',
        'char': b'\x8a',
        'type': INPUT,
        'length': 'Variable',
        'payload': {
            "version": U1,  
            "layers": (X1, {
                'ram': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 1
                },
                'bbr': {
                    'type': 'unsigned',
                    'start': 1,
                    'length': 1
                },
                'flash': {
                    'type': 'unsigned',
                    'start': 2,
                    'length': 1
                }
            }),
            "transaction": (X1, {
                'action': {
                    'type': 'unsigned',
                    'start': 0,
                    'length': 2
                }
            }), 
            "reserved0": U1,
            "group": ("None", {
                "keys": U4
            })
        },
        'aux': {
            "version": None,  
            "layers": {
                'ram': None,
                'bbr': None,
                'flash': None
            },
            "transaction": {
                'action': None
            }, 
            "reserved0": None,
            "group": {
                "keys": None
            }
        }
    }
}

ubx_dict = {
    'ACK': ack_dict,
    'CFG': cfg_dict,
    'ESF': esf_dict,
    'NAV': nav_dict
}


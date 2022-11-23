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
                {"state": U1, "reserved1": U1},# repeating group * numFences
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

UBX_CONFIG_DATABASE = {
    # CFG_ANA AssistNow Autonomous and Offline configuration
    "CFG_ANA_USE_ANA": (0x10230001, L),
    "CFG_ANA_ORBMAXERR": (0x30230002, U2),
    # CFG_BATCH Batched output configuration
    "CFG_BATCH_ENABLE": (0x10260013, L),
    "CFG_BATCH_PIOENABLE": (0x10260014, L),
    "CFG_BATCH_MAXENTRIES": (0x30260015, U2),
    "CFG_BATCH_WARNTHRS": (0x30260016, U2),
    "CFG_BATCH_PIOACTIVELOW": (0x10260018, L),
    "CFG_BATCH_PIOID": (0x20260019, U1),
    "CFG_BATCH_EXTRAPVT": (0x1026001A, L),
    "CFG_BATCH_EXTRAODO": (0x1026001B, L),
    # CFG_GEOFENCE Geofencing configuration
    "CFG_GEOFENCE_CONFLVL": (0x20240011, E1),
    "CFG_GEOFENCE_USE_PIO": (0x10240012, L),
    "CFG_GEOFENCE_PINPOL": (0x20240013, E1),
    "CFG_GEOFENCE_PIN": (0x20240014, U1),
    "CFG_GEOFENCE_USE_FENCE1": (0x10240020, L),
    "CFG_GEOFENCE_FENCE1_LAT": (0x40240021, I4),
    "CFG_GEOFENCE_FENCE1_LON": (0x40240022, I4),
    "CFG_GEOFENCE_FENCE1_RAD": (0x40240023, U4),
    "CFG_GEOFENCE_USE_FENCE2": (0x10240030, L),
    "CFG_GEOFENCE_FENCE2_LAT": (0x40240031, I4),
    "CFG_GEOFENCE_FENCE2_LON": (0x40240032, I4),
    "CFG_GEOFENCE_FENCE2_RAD": (0x40240033, U4),
    "CFG_GEOFENCE_USE_FENCE3": (0x10240040, L),
    "CFG_GEOFENCE_FENCE3_LAT": (0x40240041, I4),
    "CFG_GEOFENCE_FENCE3_LON": (0x40240042, I4),
    "CFG_GEOFENCE_FENCE3_RAD": (0x40240043, U4),
    "CFG_GEOFENCE_USE_FENCE4": (0x10240050, L),
    "CFG_GEOFENCE_FENCE4_LAT": (0x40240051, I4),
    "CFG_GEOFENCE_FENCE4_LON": (0x40240052, I4),
    "CFG_GEOFENCE_FENCE4_RAD": (0x40240053, U4),
    # CFG_HW Hardware configuration
    "CFG_HW_ANT_CFG_VOLTCTRL": (0x10A3002E, L),
    "CFG_HW_ANT_CFG_SHORTDET": (0x10A3002F, L),
    "CFG_HW_ANT_CFG_SHORTDET_POL": (0x10A30030, L),
    "CFG_HW_ANT_CFG_OPENDET": (0x10A30031, L),
    "CFG_HW_ANT_CFG_OPENDET_POL": (0x10A30032, L),
    "CFG_HW_ANT_CFG_PWRDOWN": (0x10A30033, L),
    "CFG_HW_ANT_CFG_PWRDOWN_POL": (0x10A30034, L),
    "CFG_HW_ANT_CFG_RECOVER": (0x10A30035, L),
    "CFG_HW_ANT_SUP_SWITCH_PIN": (0x20A30036, U1),
    "CFG_HW_ANT_SUP_SHORT_PIN": (0x20A30037, U1),
    "CFG_HW_ANT_SUP_OPEN_PIN": (0x20A30038, U1),
    "CFG_HW_ANT_SUP_ENGINE": (0x20A30054, E1),
    "CFG_HW_ANT_SUP_SHORT_THR": (0x20A30055, U1),
    "CFG_HW_ANT_SUP_OPEN_THR": (0x20A30056, U1),
    # CFG_I2C Configuration of the I2C interface
    "CFG_I2C_ADDRESS": (0x20510001, U1),
    "CFG_I2C_EXTENDEDTIMEOUT": (0x10510002, L),
    "CFG_I2C_ENABLED": (0x10510003, L),
    # CFG_I2CINPROT Input protocol configuration of the I2C interface
    "CFG_I2CINPROT_UBX": (0x10710001, L),
    "CFG_I2CINPROT_NMEA": (0x10710002, L),
    "CFG_I2CINPROT_RTCM3X": (0x10710004, L),
    # CFG_I2COUTPROT Output protocol configuration of the I2C interface
    "CFG_I2COUTPROT_UBX": (0x10720001, L),
    "CFG_I2COUTPROT_NMEA": (0x10720002, L),
    "CFG_I2COUTPROT_RTCM3X": (0x10720004, L),
    # CFG_INFMSG Information message configuration
    "CFG_INFMSG_UBX_I2C": (0x20920001, X1),
    "CFG_INFMSG_UBX_UART1": (0x20920002, X1),
    "CFG_INFMSG_UBX_UART2": (0x20920003, X1),
    "CFG_INFMSG_UBX_USB": (0x20920004, X1),
    "CFG_INFMSG_UBX_SPI": (0x20920005, X1),
    "CFG_INFMSG_NMEA_I2C": (0x20920006, X1),
    "CFG_INFMSG_NMEA_UART1": (0x20920007, X1),
    "CFG_INFMSG_NMEA_UART2": (0x20920008, X1),
    "CFG_INFMSG_NMEA_USB": (0x20920009, X1),
    "CFG_INFMSG_NMEA_SPI": (0x2092000A, X1),
    # CFG_ITFM Jamming and interference monitor configuration
    "CFG_ITFM_BBTHRESHOLD": (0x20410001, U1),
    "CFG_ITFM_CWTHRESHOLD": (0x20410002, U1),
    "CFG_ITFM_ENABLE": (0x1041000D, L),
    "CFG_ITFM_ANTSETTING": (0x20410010, E1),
    "CFG_ITFM_ENABLE_AUX": (0x10410013, L),
    # CFG_LOGFILTER Data logger configuration
    "CFG_LOGFILTER_RECORD_ENA": (0x10DE0002, L),
    "CFG_LOGFILTER_ONCE_PER_WAKE_UP_ENA": (0x10DE0003, L),
    "CFG_LOGFILTER_APPLY_ALL_FILTERS": (0x10DE0004, L),
    "CFG_LOGFILTER_MIN_INTERVAL": (0x30DE0005, U2),
    "CFG_LOGFILTER_TIME_THRS": (0x30DE0006, U2),
    "CFG_LOGFILTER_SPEED_THRS": (0x30DE0007, U2),
    "CFG_LOGFILTER_POSITION_THRS": (0x40DE0008, U4),
    # CFG_MOT Motion detector configuration
    "CFG_MOT_GNSSSPEED_THRS": (0x20250038, U1),
    "CFG_MOT_GNSSDIST_THRS": (0x3025003B, U2),
    # CFG_MSGOUT Message output configuration
    "CFG_MSGOUT_NMEA_ID_DTM_I2C": (0x209100A6, U1),
    "CFG_MSGOUT_NMEA_ID_DTM_SPI": (0x209100AA, U1),
    "CFG_MSGOUT_NMEA_ID_DTM_UART1": (0x209100A7, U1),
    "CFG_MSGOUT_NMEA_ID_DTM_UART2": (0x209100A8, U1),
    "CFG_MSGOUT_NMEA_ID_DTM_USB": (0x209100A9, U1),
    "CFG_MSGOUT_NMEA_ID_GBS_I2C": (0x209100DD, U1),
    "CFG_MSGOUT_NMEA_ID_GBS_SPI": (0x209100E1, U1),
    "CFG_MSGOUT_NMEA_ID_GBS_UART1": (0x209100DE, U1),
    "CFG_MSGOUT_NMEA_ID_GBS_UART2": (0x209100DF, U1),
    "CFG_MSGOUT_NMEA_ID_GBS_USB": (0x209100E0, U1),
    "CFG_MSGOUT_NMEA_ID_GGA_I2C": (0x209100BA, U1),
    "CFG_MSGOUT_NMEA_ID_GGA_SPI": (0x209100BE, U1),
    "CFG_MSGOUT_NMEA_ID_GGA_UART1": (0x209100BB, U1),
    "CFG_MSGOUT_NMEA_ID_GGA_UART2": (0x209100BC, U1),
    "CFG_MSGOUT_NMEA_ID_GGA_USB": (0x209100BD, U1),
    "CFG_MSGOUT_NMEA_ID_GLL_I2C": (0x209100C9, U1),
    "CFG_MSGOUT_NMEA_ID_GLL_SPI": (0x209100CD, U1),
    "CFG_MSGOUT_NMEA_ID_GLL_UART1": (0x209100CA, U1),
    "CFG_MSGOUT_NMEA_ID_GLL_UART2": (0x209100CB, U1),
    "CFG_MSGOUT_NMEA_ID_GLL_USB": (0x209100CC, U1),
    "CFG_MSGOUT_NMEA_ID_GNS_I2C": (0x209100B5, U1),
    "CFG_MSGOUT_NMEA_ID_GNS_SPI": (0x209100B9, U1),
    "CFG_MSGOUT_NMEA_ID_GNS_UART1": (0x209100B6, U1),
    "CFG_MSGOUT_NMEA_ID_GNS_UART2": (0x209100B7, U1),
    "CFG_MSGOUT_NMEA_ID_GNS_USB": (0x209100B8, U1),
    "CFG_MSGOUT_NMEA_ID_GRS_I2C": (0x209100CE, U1),
    "CFG_MSGOUT_NMEA_ID_GRS_SPI": (0x209100D2, U1),
    "CFG_MSGOUT_NMEA_ID_GRS_UART1": (0x209100CF, U1),
    "CFG_MSGOUT_NMEA_ID_GRS_UART2": (0x209100D0, U1),
    "CFG_MSGOUT_NMEA_ID_GRS_USB": (0x209100D1, U1),
    "CFG_MSGOUT_NMEA_ID_GSA_I2C": (0x209100BF, U1),
    "CFG_MSGOUT_NMEA_ID_GSA_SPI": (0x209100C3, U1),
    "CFG_MSGOUT_NMEA_ID_GSA_UART1": (0x209100C0, U1),
    "CFG_MSGOUT_NMEA_ID_GSA_UART2": (0x209100C1, U1),
    "CFG_MSGOUT_NMEA_ID_GSA_USB": (0x209100C2, U1),
    "CFG_MSGOUT_NMEA_ID_GST_I2C": (0x209100D3, U1),
    "CFG_MSGOUT_NMEA_ID_GST_SPI": (0x209100D7, U1),
    "CFG_MSGOUT_NMEA_ID_GST_UART1": (0x209100D4, U1),
    "CFG_MSGOUT_NMEA_ID_GST_UART2": (0x209100D5, U1),
    "CFG_MSGOUT_NMEA_ID_GST_USB": (0x209100D6, U1),
    "CFG_MSGOUT_NMEA_ID_GSV_I2C": (0x209100C4, U1),
    "CFG_MSGOUT_NMEA_ID_GSV_SPI": (0x209100C8, U1),
    "CFG_MSGOUT_NMEA_ID_GSV_UART1": (0x209100C5, U1),
    "CFG_MSGOUT_NMEA_ID_GSV_UART2": (0x209100C6, U1),
    "CFG_MSGOUT_NMEA_ID_GSV_USB": (0x209100C7, U1),
    "CFG_MSGOUT_NMEA_ID_RLM_I2C": (0x20910400, U1),
    "CFG_MSGOUT_NMEA_ID_RLM_SPI": (0x20910404, U1),
    "CFG_MSGOUT_NMEA_ID_RLM_UART1": (0x20910401, U1),
    "CFG_MSGOUT_NMEA_ID_RLM_UART2": (0x20910402, U1),
    "CFG_MSGOUT_NMEA_ID_RLM_USB": (0x20910403, U1),
    "CFG_MSGOUT_NMEA_ID_RMC_I2C": (0x209100AB, U1),
    "CFG_MSGOUT_NMEA_ID_RMC_SPI": (0x209100AF, U1),
    "CFG_MSGOUT_NMEA_ID_RMC_UART1": (0x209100AC, U1),
    "CFG_MSGOUT_NMEA_ID_RMC_UART2": (0x209100AD, U1),
    "CFG_MSGOUT_NMEA_ID_RMC_USB": (0x209100AE, U1),
    "CFG_MSGOUT_NMEA_ID_VLW_I2C": (0x209100E7, U1),
    "CFG_MSGOUT_NMEA_ID_VLW_SPI": (0x209100EB, U1),
    "CFG_MSGOUT_NMEA_ID_VLW_UART1": (0x209100E8, U1),
    "CFG_MSGOUT_NMEA_ID_VLW_UART2": (0x209100E9, U1),
    "CFG_MSGOUT_NMEA_ID_VLW_USB": (0x209100EA, U1),
    "CFG_MSGOUT_NMEA_ID_VTG_I2C": (0x209100B0, U1),
    "CFG_MSGOUT_NMEA_ID_VTG_SPI": (0x209100B4, U1),
    "CFG_MSGOUT_NMEA_ID_VTG_UART1": (0x209100B1, U1),
    "CFG_MSGOUT_NMEA_ID_VTG_UART2": (0x209100B2, U1),
    "CFG_MSGOUT_NMEA_ID_VTG_USB": (0x209100B3, U1),
    "CFG_MSGOUT_NMEA_ID_ZDA_I2C": (0x209100D8, U1),
    "CFG_MSGOUT_NMEA_ID_ZDA_SPI": (0x209100DC, U1),
    "CFG_MSGOUT_NMEA_ID_ZDA_UART1": (0x209100D9, U1),
    "CFG_MSGOUT_NMEA_ID_ZDA_UART2": (0x209100DA, U1),
    "CFG_MSGOUT_NMEA_ID_ZDA_USB": (0x209100DB, U1),
    "CFG_MSGOUT_PUBX_ID_POLYP_I2C": (0x209100EC, U1),
    "CFG_MSGOUT_PUBX_ID_POLYP_SPI": (0x209100F0, U1),
    "CFG_MSGOUT_PUBX_ID_POLYP_UART1": (0x209100ED, U1),
    "CFG_MSGOUT_PUBX_ID_POLYP_UART2": (0x209100EE, U1),
    "CFG_MSGOUT_PUBX_ID_POLYP_USB": (0x209100EF, U1),
    "CFG_MSGOUT_PUBX_ID_POLYS_I2C": (0x209100F1, U1),
    "CFG_MSGOUT_PUBX_ID_POLYS_SPI": (0x209100F5, U1),
    "CFG_MSGOUT_PUBX_ID_POLYS_UART1": (0x209100F2, U1),
    "CFG_MSGOUT_PUBX_ID_POLYS_UART2": (0x209100F3, U1),
    "CFG_MSGOUT_PUBX_ID_POLYS_USB": (0x209100F4, U1),
    "CFG_MSGOUT_PUBX_ID_POLYT_I2C": (0x209100F6, U1),
    "CFG_MSGOUT_PUBX_ID_POLYT_SPI": (0x209100FA, U1),
    "CFG_MSGOUT_PUBX_ID_POLYT_UART1": (0x209100F7, U1),
    "CFG_MSGOUT_PUBX_ID_POLYT_UART2": (0x209100F8, U1),
    "CFG_MSGOUT_PUBX_ID_POLYT_USB": (0x209100F9, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1005_I2C": (0x209102BD, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1005_SPI": (0x209102C1, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1005_UART1": (0x209102BE, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1005_UART2": (0x209102BF, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1005_USB": (0x209102C0, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1074_I2C": (0x2091035E, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1074_SPI": (0x20910362, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1074_UART1": (0x2091035F, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1074_UART2": (0x20910360, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1074_USB": (0x20910361, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1077_I2C": (0x209102CC, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1077_SPI": (0x209102D0, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1077_UART1": (0x209102CD, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1077_UART2": (0x209102CE, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1077_USB": (0x209102CF, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1084_I2C": (0x20910363, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1084_SPI": (0x20910367, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1084_UART1": (0x20910364, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1084_UART2": (0x20910365, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1084_USB": (0x20910366, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1087_I2C": (0x209102D1, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1087_SPI": (0x209102D5, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1087_UART1": (0x209102D2, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1087_UART2": (0x209102D3, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1087_USB": (0x209102D4, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1094_I2C": (0x20910368, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1094_SPI": (0x2091036C, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1094_UART1": (0x20910369, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1094_UART2": (0x2091036A, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1094_USB": (0x2091036B, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1097_I2C": (0x20910318, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1097_SPI": (0x2091031C, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1097_UART1": (0x20910319, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1097_UART2": (0x2091031A, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1097_USB": (0x2091031B, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1124_I2C": (0x2091036D, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1124_SPI": (0x20910371, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1124_UART1": (0x2091036E, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1124_UART2": (0x2091036F, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1124_USB": (0x20910370, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1127_I2C": (0x209102D6, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1127_SPI": (0x209102DA, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1127_UART1": (0x209102D7, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1127_UART2": (0x209102D8, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1127_USB": (0x209102D9, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1230_I2C": (0x20910303, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1230_SPI": (0x20910307, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1230_UART1": (0x20910304, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1230_UART2": (0x20910305, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE1230_USB": (0x20910306, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_0_I2C": (0x209102FE, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_0_SPI": (0x20910302, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_0_UART1": (0x209102FF, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_0_UART2": (0x20910300, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_0_USB": (0x20910301, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_1_I2C": (0x20910381, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_1_SPI": (0x20910385, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_1_UART1": (0x20910382, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_1_UART2": (0x20910383, U1),
    "CFG_MSGOUT_RTCM_3X_TYPE4072_1_USB": (0x20910384, U1),
    "CFG_MSGOUT_UBX_ESF_ALG_I2C": (0x2091010f, U1),
    "CFG_MSGOUT_UBX_ESF_ALG_SPI": (0x20910113, U1),
    "CFG_MSGOUT_UBX_ESF_ALG_UART1": (0x20910110, U1),
    "CFG_MSGOUT_UBX_ESF_ALG_UART2": (0x20910111, U1),
    "CFG_MSGOUT_UBX_ESF_ALG_USB": (0x20910112, U1),
    "CFG_MSGOUT_UBX_ESF_INS_I2C": (0x20910114, U1),
    "CFG_MSGOUT_UBX_ESF_INS_SPI": (0x20910118, U1),
    "CFG_MSGOUT_UBX_ESF_INS_UART1": (0x20910115, U1),
    "CFG_MSGOUT_UBX_ESF_INS_UART2": (0x20910116, U1),
    "CFG_MSGOUT_UBX_ESF_INS_USB": (0x20910117, U1),
    "CFG_MSGOUT_UBX_ESF_MEAS_I2C": (0x20910277, U1),
    "CFG_MSGOUT_UBX_ESF_MEAS_SPI": (0x2091027b, U1),
    "CFG_MSGOUT_UBX_ESF_MEAS_UART1": (0x20910278, U1),
    "CFG_MSGOUT_UBX_ESF_MEAS_UART2": (0x20910279, U1),
    "CFG_MSGOUT_UBX_ESF_MEAS_USB": (0x2091027a, U1),
    "CFG_MSGOUT_UBX_ESF_RAW_I2C": (0x2091029f, U1),
    "CFG_MSGOUT_UBX_ESF_RAW_SPI": (0x209102a3, U1),
    "CFG_MSGOUT_UBX_ESF_RAW_UART1": (0x209102a0, U1),
    "CFG_MSGOUT_UBX_ESF_RAW_UART2": (0x209102a1, U1),
    "CFG_MSGOUT_UBX_ESF_RAW_USB": (0x209102a2, U1),
    "CFG_MSGOUT_UBX_ESF_INS_I2C": (0x20910114, U1),
    "CFG_MSGOUT_UBX_ESF_INS_SPI": (0x20910118, U1),
    "CFG_MSGOUT_UBX_ESF_INS_UART1": (0x20910115, U1),
    "CFG_MSGOUT_UBX_ESF_INS_UART2": (0x20910116, U1),
    "CFG_MSGOUT_UBX_ESF_INS_USB": (0x20910117, U1),
    "CFG_MSGOUT_UBX_ESF_STATUS_I2C": (0x20910105, U1),
    "CFG_MSGOUT_UBX_ESF_STATUS_SPI": (0x20910109, U1),
    "CFG_MSGOUT_UBX_ESF_STATUS_UART1": (0x20910106, U1),
    "CFG_MSGOUT_UBX_ESF_STATUS_UART2": (0x20910107, U1),
    "CFG_MSGOUT_UBX_ESF_STATUS_USB": (0x20910108, U1),
    "CFG_MSGOUT_UBX_LOG_INFO_I2C": (0x20910259, U1),
    "CFG_MSGOUT_UBX_LOG_INFO_SPI": (0x2091025D, U1),
    "CFG_MSGOUT_UBX_LOG_INFO_UART1": (0x2091025A, U1),
    "CFG_MSGOUT_UBX_LOG_INFO_UART2": (0x2091025B, U1),
    "CFG_MSGOUT_UBX_LOG_INFO_USB": (0x2091025C, U1),
    "CFG_MSGOUT_UBX_MON_COMMS_I2C": (0x2091034F, U1),
    "CFG_MSGOUT_UBX_MON_COMMS_SPI": (0x20910353, U1),
    "CFG_MSGOUT_UBX_MON_COMMS_UART1": (0x20910350, U1),
    "CFG_MSGOUT_UBX_MON_COMMS_UART2": (0x20910351, U1),
    "CFG_MSGOUT_UBX_MON_COMMS_USB": (0x20910352, U1),
    "CFG_MSGOUT_UBX_MON_HW2_I2C": (0x209101B9, U1),
    "CFG_MSGOUT_UBX_MON_HW2_SPI": (0x209101BD, U1),
    "CFG_MSGOUT_UBX_MON_HW2_UART1": (0x209101BA, U1),
    "CFG_MSGOUT_UBX_MON_HW2_UART2": (0x209101BB, U1),
    "CFG_MSGOUT_UBX_MON_HW2_USB": (0x209101BC, U1),
    "CFG_MSGOUT_UBX_MON_HW3_I2C": (0x20910354, U1),
    "CFG_MSGOUT_UBX_MON_HW3_SPI": (0x20910358, U1),
    "CFG_MSGOUT_UBX_MON_HW3_UART1": (0x20910355, U1),
    "CFG_MSGOUT_UBX_MON_HW3_UART2": (0x20910356, U1),
    "CFG_MSGOUT_UBX_MON_HW3_USB": (0x20910357, U1),
    "CFG_MSGOUT_UBX_MON_HW_I2C": (0x209101B4, U1),
    "CFG_MSGOUT_UBX_MON_HW_SPI": (0x209101B8, U1),
    "CFG_MSGOUT_UBX_MON_HW_UART1": (0x209101B5, U1),
    "CFG_MSGOUT_UBX_MON_HW_UART2": (0x209101B6, U1),
    "CFG_MSGOUT_UBX_MON_HW_USB": (0x209101B7, U1),
    "CFG_MSGOUT_UBX_MON_IO_I2C": (0x209101A5, U1),
    "CFG_MSGOUT_UBX_MON_IO_SPI": (0x209101A9, U1),
    "CFG_MSGOUT_UBX_MON_IO_UART1": (0x209101A6, U1),
    "CFG_MSGOUT_UBX_MON_IO_UART2": (0x209101A7, U1),
    "CFG_MSGOUT_UBX_MON_IO_USB": (0x209101A8, U1),
    "CFG_MSGOUT_UBX_MON_MSGPP_I2C": (0x20910196, U1),
    "CFG_MSGOUT_UBX_MON_MSGPP_SPI": (0x2091019A, U1),
    "CFG_MSGOUT_UBX_MON_MSGPP_UART1": (0x20910197, U1),
    "CFG_MSGOUT_UBX_MON_MSGPP_UART2": (0x20910198, U1),
    "CFG_MSGOUT_UBX_MON_MSGPP_USB": (0x20910199, U1),
    "CFG_MSGOUT_UBX_MON_RF_I2C": (0x20910359, U1),
    "CFG_MSGOUT_UBX_MON_RF_SPI": (0x2091035D, U1),
    "CFG_MSGOUT_UBX_MON_RF_UART1": (0x2091035A, U1),
    "CFG_MSGOUT_UBX_MON_RF_UART2": (0x2091035B, U1),
    "CFG_MSGOUT_UBX_MON_RF_USB": (0x2091035C, U1),
    "CFG_MSGOUT_UBX_MON_RXBUF_I2C": (0x209101A0, U1),
    "CFG_MSGOUT_UBX_MON_RXBUF_SPI": (0x209101A4, U1),
    "CFG_MSGOUT_UBX_MON_RXBUF_UART1": (0x209101A1, U1),
    "CFG_MSGOUT_UBX_MON_RXBUF_UART2": (0x209101A2, U1),
    "CFG_MSGOUT_UBX_MON_RXBUF_USB": (0x209101A3, U1),
    "CFG_MSGOUT_UBX_MON_RXR_I2C": (0x20910187, U1),
    "CFG_MSGOUT_UBX_MON_RXR_SPI": (0x2091018B, U1),
    "CFG_MSGOUT_UBX_MON_RXR_UART1": (0x20910188, U1),
    "CFG_MSGOUT_UBX_MON_RXR_UART2": (0x20910189, U1),
    "CFG_MSGOUT_UBX_MON_RXR_USB": (0x2091018A, U1),
    "CFG_MSGOUT_UBX_MON_SPAN_I2C": (0x2091038B, U1),
    "CFG_MSGOUT_UBX_MON_SPAN_SPI": (0x2091038F, U1),
    "CFG_MSGOUT_UBX_MON_SPAN_UART1": (0x2091038C, U1),
    "CFG_MSGOUT_UBX_MON_SPAN_UART2": (0x2091038D, U1),
    "CFG_MSGOUT_UBX_MON_SPAN_USB": (0x2091038E, U1),
    "CFG_MSGOUT_UBX_MON_TXBUF_I2C": (0x2091019B, U1),
    "CFG_MSGOUT_UBX_MON_TXBUF_SPI": (0x2091019F, U1),
    "CFG_MSGOUT_UBX_MON_TXBUF_UART1": (0x2091019C, U1),
    "CFG_MSGOUT_UBX_MON_TXBUF_UART2": (0x2091019D, U1),
    "CFG_MSGOUT_UBX_MON_TXBUF_USB": (0x2091019E, U1),
    "CFG_MSGOUT_UBX_NAV_AOPSTATUS_I2C": (0x20910079, U1),
    "CFG_MSGOUT_UBX_NAV_AOPSTATUS_SPI": (0x2091007D, U1),
    "CFG_MSGOUT_UBX_NAV_AOPSTATUS_UART1": (0x2091007A, U1),
    "CFG_MSGOUT_UBX_NAV_AOPSTATUS_UART2": (0x2091007B, U1),
    "CFG_MSGOUT_UBX_NAV_AOPSTATUS_USB": (0x2091007C, U1),
    "CFG_MSGOUT_UBX_NAV_ATT_I2C": (0x2091001f, U1),
    "CFG_MSGOUT_UBX_NAV_ATT_SPI": (0x20910023, U1),
    "CFG_MSGOUT_UBX_NAV_ATT_UART1": (0x20910020, U1),
    "CFG_MSGOUT_UBX_NAV_ATT_UART2": (0x20910021, U1),
    "CFG_MSGOUT_UBX_NAV_ATT_USB": (0x20910022, U1),
    "CFG_MSGOUT_UBX_NAV_CLOCK_I2C": (0x20910065, U1),
    "CFG_MSGOUT_UBX_NAV_CLOCK_SPI": (0x20910069, U1),
    "CFG_MSGOUT_UBX_NAV_CLOCK_UART1": (0x20910066, U1),
    "CFG_MSGOUT_UBX_NAV_CLOCK_UART2": (0x20910067, U1),
    "CFG_MSGOUT_UBX_NAV_CLOCK_USB": (0x20910068, U1),
    "CFG_MSGOUT_UBX_NAV_COV_I2C": (0x20910083, U1),
    "CFG_MSGOUT_UBX_NAV_COV_SPI": (0x20910087, U1),
    "CFG_MSGOUT_UBX_NAV_COV_UART1": (0x20910084, U1),
    "CFG_MSGOUT_UBX_NAV_COV_UART2": (0x20910085, U1),
    "CFG_MSGOUT_UBX_NAV_COV_USB": (0x20910086, U1),
    "CFG_MSGOUT_UBX_NAV_DOP_I2C": (0x20910038, U1),
    "CFG_MSGOUT_UBX_NAV_DOP_SPI": (0x2091003C, U1),
    "CFG_MSGOUT_UBX_NAV_DOP_UART1": (0x20910039, U1),
    "CFG_MSGOUT_UBX_NAV_DOP_UART2": (0x2091003A, U1),
    "CFG_MSGOUT_UBX_NAV_DOP_USB": (0x2091003B, U1),
    "CFG_MSGOUT_UBX_NAV_EOE_I2C": (0x2091015F, U1),
    "CFG_MSGOUT_UBX_NAV_EOE_SPI": (0x20910163, U1),
    "CFG_MSGOUT_UBX_NAV_EOE_UART1": (0x20910160, U1),
    "CFG_MSGOUT_UBX_NAV_EOE_UART2": (0x20910161, U1),
    "CFG_MSGOUT_UBX_NAV_EOE_USB": (0x20910162, U1),
    "CFG_MSGOUT_UBX_NAV_GEOFENCE_I2C": (0x209100A1, U1),
    "CFG_MSGOUT_UBX_NAV_GEOFENCE_SPI": (0x209100A5, U1),
    "CFG_MSGOUT_UBX_NAV_GEOFENCE_UART1": (0x209100A2, U1),
    "CFG_MSGOUT_UBX_NAV_GEOFENCE_UART2": (0x209100A3, U1),
    "CFG_MSGOUT_UBX_NAV_GEOFENCE_USB": (0x209100A4, U1),
    "CFG_MSGOUT_UBX_NAV_ODO_I2C": (0x2091007E, U1),
    "CFG_MSGOUT_UBX_NAV_ODO_SPI": (0x20910082, U1),
    "CFG_MSGOUT_UBX_NAV_ODO_UART1": (0x2091007F, U1),
    "CFG_MSGOUT_UBX_NAV_ODO_UART2": (0x20910080, U1),
    "CFG_MSGOUT_UBX_NAV_ODO_USB": (0x20910081, U1),
    "CFG_MSGOUT_UBX_NAV_ORB_I2C": (0x20910010, U1),
    "CFG_MSGOUT_UBX_NAV_ORB_SPI": (0x20910014, U1),
    "CFG_MSGOUT_UBX_NAV_ORB_UART1": (0x20910011, U1),
    "CFG_MSGOUT_UBX_NAV_ORB_UART2": (0x20910012, U1),
    "CFG_MSGOUT_UBX_NAV_ORB_USB": (0x20910013, U1),
    "CFG_MSGOUT_UBX_NAV_POSECEF_I2C": (0x20910024, U1),
    "CFG_MSGOUT_UBX_NAV_POSECEF_SPI": (0x20910028, U1),
    "CFG_MSGOUT_UBX_NAV_POSECEF_UART1": (0x20910025, U1),
    "CFG_MSGOUT_UBX_NAV_POSECEF_UART2": (0x20910026, U1),
    "CFG_MSGOUT_UBX_NAV_POSECEF_USB": (0x20910027, U1),
    "CFG_MSGOUT_UBX_NAV_POSLLH_I2C": (0x20910029, U1),
    "CFG_MSGOUT_UBX_NAV_POSLLH_SPI": (0x2091002D, U1),
    "CFG_MSGOUT_UBX_NAV_POSLLH_UART1": (0x2091002A, U1),
    "CFG_MSGOUT_UBX_NAV_POSLLH_UART2": (0x2091002B, U1),
    "CFG_MSGOUT_UBX_NAV_POSLLH_USB": (0x2091002C, U1),
    "CFG_MSGOUT_UBX_NAV_PVT_I2C": (0x20910006, U1),
    "CFG_MSGOUT_UBX_NAV_PVT_SPI": (0x2091000A, U1),
    "CFG_MSGOUT_UBX_NAV_PVT_UART1": (0x20910007, U1),
    "CFG_MSGOUT_UBX_NAV_PVT_UART2": (0x20910008, U1),
    "CFG_MSGOUT_UBX_NAV_PVT_USB": (0x20910009, U1),
    "CFG_MSGOUT_UBX_NAV_SAT_I2C": (0x20910015, U1),
    "CFG_MSGOUT_UBX_NAV_SAT_SPI": (0x20910019, U1),
    "CFG_MSGOUT_UBX_NAV_SAT_UART1": (0x20910016, U1),
    "CFG_MSGOUT_UBX_NAV_SAT_UART2": (0x20910017, U1),
    "CFG_MSGOUT_UBX_NAV_SAT_USB": (0x20910018, U1),
    "CFG_MSGOUT_UBX_NAV_SBAS_I2C": (0x2091006A, U1),
    "CFG_MSGOUT_UBX_NAV_SBAS_SPI": (0x2091006E, U1),
    "CFG_MSGOUT_UBX_NAV_SBAS_UART1": (0x2091006B, U1),
    "CFG_MSGOUT_UBX_NAV_SBAS_UART2": (0x2091006C, U1),
    "CFG_MSGOUT_UBX_NAV_SBAS_USB": (0x2091006D, U1),
    "CFG_MSGOUT_UBX_NAV_SIG_I2C": (0x20910345, U1),
    "CFG_MSGOUT_UBX_NAV_SIG_SPI": (0x20910349, U1),
    "CFG_MSGOUT_UBX_NAV_SIG_UART1": (0x20910346, U1),
    "CFG_MSGOUT_UBX_NAV_SIG_UART2": (0x20910347, U1),
    "CFG_MSGOUT_UBX_NAV_SIG_USB": (0x20910348, U1),
    "CFG_MSGOUT_UBX_NAV_SLAS_I2C": (0x20910336, U1),
    "CFG_MSGOUT_UBX_NAV_SLAS_SPI": (0x2091033A, U1),
    "CFG_MSGOUT_UBX_NAV_SLAS_UART1": (0x20910337, U1),
    "CFG_MSGOUT_UBX_NAV_SLAS_UART2": (0x20910338, U1),
    "CFG_MSGOUT_UBX_NAV_SLAS_USB": (0x20910339, U1),
    "CFG_MSGOUT_UBX_NAV_STATUS_I2C": (0x2091001A, U1),
    "CFG_MSGOUT_UBX_NAV_STATUS_SPI": (0x2091001E, U1),
    "CFG_MSGOUT_UBX_NAV_STATUS_UART1": (0x2091001B, U1),
    "CFG_MSGOUT_UBX_NAV_STATUS_UART2": (0x2091001C, U1),
    "CFG_MSGOUT_UBX_NAV_STATUS_USB": (0x2091001D, U1),
    "CFG_MSGOUT_UBX_NAV_SVIN_I2C": (0x20910088, U1),
    "CFG_MSGOUT_UBX_NAV_SVIN_SPI": (0x2091008C, U1),
    "CFG_MSGOUT_UBX_NAV_SVIN_UART1": (0x20910089, U1),
    "CFG_MSGOUT_UBX_NAV_SVIN_UART2": (0x2091008A, U1),
    "CFG_MSGOUT_UBX_NAV_SVIN_USB": (0x2091008B, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEBDS_I2C": (0x20910051, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEBDS_SPI": (0x20910055, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEBDS_UART1": (0x20910052, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEBDS_UART2": (0x20910053, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEBDS_USB": (0x20910054, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGAL_I2C": (0x20910056, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGAL_SPI": (0x2091005A, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGAL_UART1": (0x20910057, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGAL_UART2": (0x20910058, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGAL_USB": (0x20910059, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGLO_I2C": (0x2091004C, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGLO_SPI": (0x20910050, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGLO_UART1": (0x2091004D, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGLO_UART2": (0x2091004E, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGLO_USB": (0x2091004F, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGPS_I2C": (0x20910047, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGPS_SPI": (0x2091004B, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGPS_UART1": (0x20910048, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGPS_UART2": (0x20910049, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEGPS_USB": (0x2091004A, U1),
    "CFG_MSGOUT_UBX_NAV_TIMELS_I2C": (0x20910060, U1),
    "CFG_MSGOUT_UBX_NAV_TIMELS_SPI": (0x20910064, U1),
    "CFG_MSGOUT_UBX_NAV_TIMELS_UART1": (0x20910061, U1),
    "CFG_MSGOUT_UBX_NAV_TIMELS_UART2": (0x20910062, U1),
    "CFG_MSGOUT_UBX_NAV_TIMELS_USB": (0x20910063, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEQZSS_I2C": (0x20910386, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEQZSS_SPI": (0x2091038A, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEQZSS_UART1": (0x20910387, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEQZSS_UART2": (0x20910388, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEQZSS_USB": (0x20910389, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEUTC_I2C": (0x2091005B, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEUTC_SPI": (0x2091005F, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEUTC_UART1": (0x2091005C, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEUTC_UART2": (0x2091005D, U1),
    "CFG_MSGOUT_UBX_NAV_TIMEUTC_USB": (0x2091005E, U1),
    "CFG_MSGOUT_UBX_NAV_VELECEF_I2C": (0x2091003D, U1),
    "CFG_MSGOUT_UBX_NAV_VELECEF_SPI": (0x20910041, U1),
    "CFG_MSGOUT_UBX_NAV_VELECEF_UART1": (0x2091003E, U1),
    "CFG_MSGOUT_UBX_NAV_VELECEF_UART2": (0x2091003F, U1),
    "CFG_MSGOUT_UBX_NAV_VELECEF_USB": (0x20910040, U1),
    "CFG_MSGOUT_UBX_NAV_VELNED_I2C": (0x20910042, U1),
    "CFG_MSGOUT_UBX_NAV_VELNED_SPI": (0x20910046, U1),
    "CFG_MSGOUT_UBX_NAV_VELNED_UART1": (0x20910043, U1),
    "CFG_MSGOUT_UBX_NAV_VELNED_UART2": (0x20910044, U1),
    "CFG_MSGOUT_UBX_NAV_VELNED_USB": (0x20910045, U1),
    "CFG_MSGOUT_UBX_RXM_MEASX_I2C": (0x20910204, U1),
    "CFG_MSGOUT_UBX_RXM_MEASX_SPI": (0x20910208, U1),
    "CFG_MSGOUT_UBX_RXM_MEASX_UART1": (0x20910205, U1),
    "CFG_MSGOUT_UBX_RXM_MEASX_UART2": (0x20910206, U1),
    "CFG_MSGOUT_UBX_RXM_MEASX_USB": (0x20910207, U1),
    "CFG_MSGOUT_UBX_RXM_RAWX_I2C": (0x209102A4, U1),
    "CFG_MSGOUT_UBX_RXM_RAWX_SPI": (0x209102A8, U1),
    "CFG_MSGOUT_UBX_RXM_RAWX_UART1": (0x209102A5, U1),
    "CFG_MSGOUT_UBX_RXM_RAWX_UART2": (0x209102A6, U1),
    "CFG_MSGOUT_UBX_RXM_RAWX_USB": (0x209102A7, U1),
    "CFG_MSGOUT_UBX_RXM_RLM_I2C": (0x2091025E, U1),
    "CFG_MSGOUT_UBX_RXM_RLM_SPI": (0x20910262, U1),
    "CFG_MSGOUT_UBX_RXM_RLM_UART1": (0x2091025F, U1),
    "CFG_MSGOUT_UBX_RXM_RLM_UART2": (0x20910260, U1),
    "CFG_MSGOUT_UBX_RXM_RLM_USB": (0x20910261, U1),
    "CFG_MSGOUT_UBX_RXM_RTCM_I2C": (0x20910268, U1),
    "CFG_MSGOUT_UBX_RXM_RTCM_SPI": (0x2091026C, U1),
    "CFG_MSGOUT_UBX_RXM_RTCM_UART1": (0x20910269, U1),
    "CFG_MSGOUT_UBX_RXM_RTCM_UART2": (0x2091026A, U1),
    "CFG_MSGOUT_UBX_RXM_RTCM_USB": (0x2091026B, U1),
    "CFG_MSGOUT_UBX_RXM_SFRBX_I2C": (0x20910231, U1),
    "CFG_MSGOUT_UBX_RXM_SFRBX_SPI": (0x20910235, U1),
    "CFG_MSGOUT_UBX_RXM_SFRBX_UART1": (0x20910232, U1),
    "CFG_MSGOUT_UBX_RXM_SFRBX_UART2": (0x20910233, U1),
    "CFG_MSGOUT_UBX_RXM_SFRBX_USB": (0x20910234, U1),
    "CFG_MSGOUT_UBX_TIM_TM2_I2C": (0x20910178, U1),
    "CFG_MSGOUT_UBX_TIM_TM2_SPI": (0x2091017C, U1),
    "CFG_MSGOUT_UBX_TIM_TM2_UART1": (0x20910179, U1),
    "CFG_MSGOUT_UBX_TIM_TM2_UART2": (0x2091017A, U1),
    "CFG_MSGOUT_UBX_TIM_TM2_USB": (0x2091017B, U1),
    "CFG_MSGOUT_UBX_TIM_TP_I2C": (0x2091017D, U1),
    "CFG_MSGOUT_UBX_TIM_TP_SPI": (0x20910181, U1),
    "CFG_MSGOUT_UBX_TIM_TP_UART1": (0x2091017E, U1),
    "CFG_MSGOUT_UBX_TIM_TP_UART2": (0x2091017F, U1),
    "CFG_MSGOUT_UBX_TIM_TP_USB": (0x20910180, U1),
    "CFG_MSGOUT_UBX_TIM_VRFY_I2C": (0x20910092, U1),
    "CFG_MSGOUT_UBX_TIM_VRFY_SPI": (0x20910096, U1),
    "CFG_MSGOUT_UBX_TIM_VRFY_UART1": (0x20910093, U1),
    "CFG_MSGOUT_UBX_TIM_VRFY_UART2": (0x20910094, U1),
    "CFG_MSGOUT_UBX_TIM_VRFY_USB": (0x20910095, U1),
    # following two items output by NEO-9M but not listed in spec?
    "CFG_MSGOUT_UBX_0x20910119": (0x20910119, U1),
    "CFG_MSGOUT_UBX_0x2091011A": (0x2091011A, U1),
    # CFG_NAVSPG Standard precision navigation configuration
    "CFG_NAVSPG_FIXMODE": (0x20110011, E1),
    "CFG_NAVSPG_INIFIX3D": (0x10110013, L),
    "CFG_NAVSPG_WKNROLLOVER": (0x30110017, U2),
    "CFG_NAVSPG_USE_PPP": (0x10110019, L),
    "CFG_NAVSPG_UTCSTANDARD": (0x2011001C, E1),
    "CFG_NAVSPG_DYNMODEL": (0x20110021, E1),
    "CFG_NAVSPG_ACKAIDING": (0x10110025, L),
    "CFG_NAVSPG_USE_USRDAT": (0x10110061, L),
    "CFG_NAVSPG_USRDAT_MAJA": (0x50110062, R8),
    "CFG_NAVSPG_USRDAT_FLAT": (0x50110063, R8),
    "CFG_NAVSPG_USRDAT_DX": (0x40110064, R4),
    "CFG_NAVSPG_USRDAT_DY": (0x40110065, R4),
    "CFG_NAVSPG_USRDAT_DZ": (0x40110066, R4),
    "CFG_NAVSPG_USRDAT_ROTX": (0x40110067, R4),
    "CFG_NAVSPG_USRDAT_ROTY": (0x40110068, R4),
    "CFG_NAVSPG_USRDAT_ROTZ": (0x40110069, R4),
    "CFG_NAVSPG_USRDAT_SCALE": (0x4011006A, R4),
    "CFG_NAVSPG_INFIL_MINSVS": (0x201100A1, U1),
    "CFG_NAVSPG_INFIL_MAXSVS": (0x201100A2, U1),
    "CFG_NAVSPG_INFIL_MINCNO": (0x201100A3, U1),
    "CFG_NAVSPG_INFIL_MINELEV": (0x201100A4, I1),
    "CFG_NAVSPG_INFIL_NCNOTHRS": (0x201100AA, U1),
    "CFG_NAVSPG_INFIL_CNOTHRS": (0x201100AB, U1),
    "CFG_NAVSPG_OUTFIL_PDOP": (0x301100B1, U2),
    "CFG_NAVSPG_OUTFIL_TDOP": (0x301100B2, U2),
    "CFG_NAVSPG_OUTFIL_PACC": (0x301100B3, U2),
    "CFG_NAVSPG_OUTFIL_TACC": (0x301100B4, U2),
    "CFG_NAVSPG_OUTFIL_FACC": (0x301100B5, U2),
    "CFG_NAVSPG_CONSTR_ALT": (0x401100C1, I4),
    "CFG_NAVSPG_CONSTR_ALTVAR": (0x401100C2, U4),
    "CFG_NAVSPG_CONSTR_DGNSSTO": (0x201100C4, U1),
    "CFG_NAVSPG_SIGATTCOMP": (0x201100D6, E1),
    # CFG_NMEA NMEA protocol configuration
    "CFG_NMEA_PROTVER": (0x20930001, E1),
    "CFG_NMEA_MAXSVS": (0x20930002, E1),
    "CFG_NMEA_COMPAT": (0x10930003, L),
    "CFG_NMEA_CONSIDER": (0x10930004, L),
    "CFG_NMEA_LIMIT82": (0x10930005, L),
    "CFG_NMEA_HIGHPREC": (0x10930006, L),
    "CFG_NMEA_SVNUMBERING": (0x20930007, E1),
    "CFG_NMEA_FILT_GPS": (0x10930011, L),
    "CFG_NMEA_FILT_SBAS": (0x10930012, L),
    "CFG_NMEA_FILT_GAL": (0x10930013, L),
    "CFG_NMEA_FILT_QZSS": (0x10930015, L),
    "CFG_NMEA_FILT_GLO": (0x10930016, L),
    "CFG_NMEA_FILT_BDS": (0x10930017, L),
    "CFG_NMEA_OUT_INVFIX": (0x10930021, L),
    "CFG_NMEA_OUT_MSKFIX": (0x10930022, L),
    "CFG_NMEA_OUT_INVTIME": (0x10930023, L),
    "CFG_NMEA_OUT_INVDATE": (0x10930024, L),
    "CFG_NMEA_OUT_ONLYGPS": (0x10930025, L),
    "CFG_NMEA_OUT_FROZENCOG": (0x10930026, L),
    "CFG_NMEA_MAINTALKERID": (0x20930031, E1),
    "CFG_NMEA_GSVTALKERID": (0x20930032, E1),
    "CFG_NMEA_BDSTALKERID": (0x30930033, U2),
    # CFG_ODO Odometer and low_speed course over ground filter configuration
    "CFG_ODO_USE_ODO": (0x10220001, L),
    "CFG_ODO_USE_COG": (0x10220002, L),
    "CFG_ODO_OUTLPVEL": (0x10220003, L),
    "CFG_ODO_OUTLPCOG": (0x10220004, L),
    "CFG_ODO_PROFILE": (0x20220005, E1),
    "CFG_ODO_COGMAXSPEED": (0x20220021, U1),
    "CFG_ODO_COGMAXPOSACC": (0x20220022, U1),
    "CFG_ODO_VELLPGAIN": (0x20220031, U1),
    "CFG_ODO_COGLPGAIN": (0x20220032, U1),
    # CFG_PM Configuration for receiver power management
    "CFG_PM_OPERATEMODE": (0x20D00001, E1),
    "CFG_PM_POSUPDATEPERIOD": (0x40D00002, U4),
    "CFG_PM_ACQPERIOD": (0x40D00003, U4),
    "CFG_PM_GRIDOFFSET": (0x40D00004, U4),
    "CFG_PM_ONTIME": (0x30D00005, U2),
    "CFG_PM_MINACQTIME": (0x20D00006, U1),
    "CFG_PM_MAXACQTIME": (0x20D00007, U1),
    "CFG_PM_DONOTENTEROFF": (0x10D00008, L),
    "CFG_PM_WAITTIMEFIX": (0x10D00009, L),
    "CFG_PM_UPDATEEPH": (0x10D0000A, L),
    "CFG_PM_EXTINTSEL": (0x20D0000B, E1),
    "CFG_PM_EXTINTWAKE": (0x10D0000C, L),
    "CFG_PM_EXTINTBACKUP": (0x10D0000D, L),
    "CFG_PM_EXTINTINACTIVE": (0x10D0000E, L),
    "CFG_PM_EXTINTINACTIVITY": (0x40D0000F, U4),
    "CFG_PM_LIMITPEAKCURR": (0x10D00010, L),
    # CFG_QZSS QZSS system configuration
    "CFG_QZSS_USE_SLAS_DGNSS": (0x10370005, L),
    "CFG_QZSS_USE_SLAS_TESTMODE": (0x10370006, L),
    "CFG_QZSS_USE_SLAS_RAIM_UNCORR": (0x10370007, L),
    # CFG_RATE Navigation and measurement rate configuration
    "CFG_RATE_MEAS": (0x30210001, U2),
    "CFG_RATE_NAV": (0x30210002, U2),
    "CFG_RATE_TIMEREF": (0x20210003, E1),
    # CFG_RINV Remote inventory
    "CFG_RINV_DUMP": (0x10C70001, L),
    "CFG_RINV_BINARY": (0x10C70002, L),
    "CFG_RINV_DATA_SIZE": (0x20C70003, U1),
    "CFG_RINV_CHUNK0": (0x50C70004, X8),
    "CFG_RINV_CHUNK1": (0x50C70005, X8),
    "CFG_RINV_CHUNK2": (0x50C70006, X8),
    "CFG_RINV_CHUNK3": (0x50C70007, X8),
    # CFG_SBAS SBAS configuration
    "CFG_SBAS_USE_TESTMODE": (0x10360002, L),
    "CFG_SBAS_USE_RANGING": (0x10360003, L),
    "CFG_SBAS_USE_DIFFCORR": (0x10360004, L),
    "CFG_SBAS_USE_INTEGRITY": (0x10360005, L),
    "CFG_SBAS_PRNSCANMASK": (0x50360006, X8),
    # CFG_SEC Security configuration
    "CFG_SEC_CFG_LOCK": (0x10F60009, L),
    "CFG_SEC_CFG_LOCK_UNLOCKGRP1": (0x30F6000A, U2),
    "CFG_SEC_CFG_LOCK_UNLOCKGRP2": (0x30F6000B, U2),
    # CFG_SIGNAL Satellite systems (GNSS) signal configuration
    "CFG_SIGNAL_GPS_ENA": (0x1031001F, L),
    "CFG_SIGNAL_GPS_L1CA_ENA": (0x10310001, L),
    "CFG_SIGNAL_SBAS_ENA": (0x10310020, L),
    "CFG_SIGNAL_SBAS_L1CA_ENA": (0x10310005, L),
    "CFG_SIGNAL_GAL_ENA": (0x10310021, L),
    "CFG_SIGNAL_GAL_E1_ENA": (0x10310007, L),
    "CFG_SIGNAL_BDS_ENA": (0x10310022, L),
    "CFG_SIGNAL_BDS_B1_ENA": (0x1031000D, L),
    "CFG_SIGNAL_QZSS_ENA": (0x10310024, L),
    "CFG_SIGNAL_QZSS_L1CA_ENA": (0x10310012, L),
    "CFG_SIGNAL_GLO_ENA": (0x10310025, L),
    "CFG_SIGNAL_GLO_L1_ENA": (0x10310018, L),
    # CFG_SPI Configuration of the SPI interface
    "CFG_SPI_MAXFF": (0x20640001, U1),
    "CFG_SPI_CPOLARITY": (0x10640002, L),
    "CFG_SPI_CPHASE": (0x10640003, L),
    "CFG_SPI_EXTENDEDTIMEOUT": (0x10640005, L),
    "CFG_SPI_ENABLED": (0x10640006, L),
    # CFG_SPIINPROT Input protocol configuration of the SPI interface
    "CFG_SPIINPROT_UBX": (0x10790001, L),
    "CFG_SPIINPROT_NMEA": (0x10790002, L),
    "CFG_SPIINPROT_RTCM3X": (0x10790004, L),
    # CFG_SPIOUTPROT Output protocol configuration of the SPI interface
    "CFG_SPIOUTPROT_UBX": (0x107A0001, L),
    "CFG_SPIOUTPROT_NMEA": (0x107A0002, L),
    "CFG_SPIOUTPROT_RTCM3X": (0x107A0004, L),
    # CFG_TMODE Time mode configuration
    "CFG_TMODE_MODE": (0x20030001, E1),
    "CFG_TMODE_POS_TYPE": (0x20030002, E1),
    "CFG_TMODE_ECEF_X": (0x20030003, I4),
    "CFG_TMODE_ECEF_Y": (0x20030004, I4),
    "CFG_TMODE_ECEF_Z": (0x20030005, I4),
    "CFG_TMODE_ECEF_X_HP": (0x20030006, I1),
    "CFG_TMODE_ECEF_Y_HP": (0x20030007, I1),
    "CFG_TMODE_ECEF_Z_HP": (0x20030008, I1),
    "CFG_TMODE_LAT": (0x20030009, I4),
    "CFG_TMODE_LON": (0x2003000A, I4),
    "CFG_TMODE_HEIGHT": (0x2003000B, I4),
    "CFG_TMODE_LAT_HP": (0x2003000C, I1),
    "CFG_TMODE_LON_HP": (0x2003000D, I1),
    "CFG_TMODE_HEIGHT_HP": (0x2003000E, I1),
    "CFG_TMODE_FIXED_POS_ACC": (0x2003000F, U4),
    "CFG_TMODE_SVIN_MIN_DUR": (0x20030010, U4),
    "CFG_TMODE_SVIN_ACC_LIMIT": (0x20030011, U4),
    # CFG_TP Timepulse configuration
    "CFG_TP_PULSE_DEF": (0x20050023, E1),
    "CFG_TP_PULSE_LENGTH_DEF": (0x20050030, E1),
    "CFG_TP_ANT_CABLEDELAY": (0x30050001, I2),
    "CFG_TP_PERIOD_TP1": (0x40050002, U4),
    "CFG_TP_PERIOD_LOCK_TP1": (0x40050003, U4),
    "CFG_TP_FREQ_TP1": (0x40050024, U4),
    "CFG_TP_FREQ_LOCK_TP1": (0x40050025, U4),
    "CFG_TP_LEN_TP1": (0x40050004, U4),
    "CFG_TP_LEN_LOCK_TP1": (0x40050005, U4),
    "CFG_TP_DUTY_TP1": (0x5005002A, R8),
    "CFG_TP_DUTY_LOCK_TP1": (0x5005002B, R8),
    "CFG_TP_USER_DELAY_TP1": (0x40050006, I4),
    "CFG_TP_TP1_ENA": (0x10050007, L),
    "CFG_TP_SYNC_GNSS_TP1": (0x10050008, L),
    "CFG_TP_USE_LOCKED_TP1": (0x10050009, L),
    "CFG_TP_ALIGN_TO_TOW_TP1": (0x1005000A, L),
    "CFG_TP_POL_TP1": (0x1005000B, L),
    "CFG_TP_TIMEGRID_TP1": (0x2005000C, E1),
    "CFG_TP_PERIOD_TP2": (0x4005000D, U4),
    "CFG_TP_PERIOD_LOCK_TP2": (0x4005000E, U4),
    "CFG_TP_FREQ_TP2": (0x40050026, U4),
    "CFG_TP_FREQ_LOCK_TP2": (0x40050027, U4),
    "CFG_TP_LEN_TP2": (0x4005000F, U4),
    "CFG_TP_LEN_LOCK_TP2": (0x40050010, U4),
    "CFG_TP_DUTY_TP2": (0x5005002C, R8),
    "CFG_TP_DUTY_LOCK_TP2": (0x5005002D, R8),
    "CFG_TP_USER_DELAY_TP2": (0x40050011, I4),
    "CFG_TP_TP2_ENA": (0x10050012, L),
    "CFG_TP_SYNC_GNSS_TP2": (0x10050013, L),
    "CFG_TP_USE_LOCKED_TP2": (0x10050014, L),
    "CFG_TP_ALIGN_TO_TOW_TP2": (0x10050015, L),
    "CFG_TP_POL_TP2": (0x10050016, L),
    "CFG_TP_TIMEGRID_TP2": (0x20050017, E1),
    # CFG_TXREADY TX ready configuration
    "CFG_TXREADY_ENABLED": (0x10A20001, L),
    "CFG_TXREADY_POLARITY": (0x10A20002, L),
    "CFG_TXREADY_PIN": (0x20A20003, U1),
    "CFG_TXREADY_THRESHOLD": (0x30A20004, U2),
    "CFG_TXREADY_INTERFACE": (0x20A20005, E1),
    # CFG_UART1 Configuration of the UART1 interface
    "CFG_UART1_BAUDRATE": (0x40520001, U4),
    "CFG_UART1_STOPBITS": (0x20520002, E1),
    "CFG_UART1_DATABITS": (0x20520003, E1),
    "CFG_UART1_PARITY": (0x20520004, E1),
    "CFG_UART1_ENABLED": (0x10520005, L),
    # CFG_UART1INPROT Input protocol configuration of the UART1 interface
    "CFG_UART1INPROT_UBX": (0x10730001, L),
    "CFG_UART1INPROT_NMEA": (0x10730002, L),
    "CFG_UART1INPROT_RTCM3X": (0x10730004, L),
    # CFG_UART1OUTPROT Output protocol configuration of the UART1 interface
    "CFG_UART1OUTPROT_UBX": (0x10740001, L),
    "CFG_UART1OUTPROT_NMEA": (0x10740002, L),
    "CFG_UART1OUTPROT_RTCM3X": (0x10740004, L),
    # CFG_UART2 Configuration of the UART2 interface
    "CFG_UART2_BAUDRATE": (0x40530001, U4),
    "CFG_UART2_STOPBITS": (0x20530002, E1),
    "CFG_UART2_DATABITS": (0x20530003, E1),
    "CFG_UART2_PARITY": (0x20530004, E1),
    "CFG_UART2_ENABLED": (0x10530005, L),
    "CFG_UART2_REMAP": (0x10530006, L),
    # CFG_UART2INPROT Input protocol configuration of the UART2 interface
    "CFG_UART2INPROT_UBX": (0x10750001, L),
    "CFG_UART2INPROT_NMEA": (0x10750002, L),
    "CFG_UART2INPROT_RTCM3X": (0x10750004, L),
    # CFG_UART2OUTPROT Output protocol configuration of the UART2 interface
    "CFG_UART2OUTPROT_UBX": (0x10760001, L),
    "CFG_UART2OUTPROT_NMEA": (0x10760002, L),
    "CFG_UART2OUTPROT_RTCM3X": (0x10760004, L),
    # CFG_USB Configuration of the USB interface
    "CFG_USB_ENABLED": (0x10650001, L),
    "CFG_USB_SELFPOW": (0x10650002, L),
    "CFG_USB_VENDOR_ID": (0x3065000A, U2),
    "CFG_USB_PRODUCT_ID": (0x3065000B, U2),
    "CFG_USB_POWER": (0x3065000C, U2),
    "CFG_USB_VENDOR_STR0": (0x5065000D, X8),
    "CFG_USB_VENDOR_STR1": (0x5065000E, X8),
    "CFG_USB_VENDOR_STR2": (0x5065000F, X8),
    "CFG_USB_VENDOR_STR3": (0x50650010, X8),
    "CFG_USB_PRODUCT_STR0": (0x50650011, X8),
    "CFG_USB_PRODUCT_STR1": (0x50650012, X8),
    "CFG_USB_PRODUCT_STR2": (0x50650013, X8),
    "CFG_USB_PRODUCT_STR3": (0x50650014, X8),
    "CFG_USB_SERIAL_NO_STR0": (0x50650015, X8),
    "CFG_USB_SERIAL_NO_STR1": (0x50650016, X8),
    "CFG_USB_SERIAL_NO_STR2": (0x50650017, X8),
    "CFG_USB_SERIAL_NO_STR3": (0x50650018, X8),
    # CFG_USBINPROT Input protocol configuration of the USB interface
    "CFG_USBINPROT_UBX": (0x10770001, L),
    "CFG_USBINPROT_NMEA": (0x10770002, L),
    "CFG_USBINPROT_RTCM3X": (0x10770004, L),
    # CFG_USBOUTPROT Output protocol configuration of the USB interface
    "CFG_USBOUTPROT_UBX": (0x10780001, L),
    "CFG_USBOUTPROT_NMEA": (0x10780002, L),
    "CFG_USBOUTPROT_RTCM3X": (0x10780004, L),
}

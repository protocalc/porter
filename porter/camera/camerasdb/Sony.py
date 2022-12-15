SONY_OPCODE = {
    'Values' : {
        'SDIOConnect' : 0x9201,
        'SDIOGetExtDeviceInfo' : 0x9202,
        'SonyGetDevicePropDesc' : 0x9203,
        'SonyGetDevicePropValue' : 0x9204,
        'SetControlDeviceA' : 0x9205,
        'GetControlDeviceDesc' : 0x9206,
        'SetControlDeviceB' : 0x9207,
        'GetAllDevicePropData' : 0x9209
    }
}

SONY_RESPCODE = {
    'Values' : {
        'Sony1' : 0xa101
    }
}

SONY_EVENTCODE = {
    'Values' : {
        'SonyObjectAdded' : 0xc201,
        'SonyObjectRemoved' : 0xc202,
        'SonyPropertyChanged' : 0xc203
    }
}

SONY_PROPCODE = {
    'Values' : {
        'DPCCompensation'   : 0xD200,
        'DRangeOptimize'    : 0xD201,
        'SonyImageSize'     : 0xD203,
        'ShutterSpeed'      : 0xD20D,
        'ColorTemp'         : 0xD20F,
        'CCFilter'          : 0xD210,
        'AspectRatio'       : 0xD211,
        'FocusFound'        : 0xD213,
        'ObjectInMemory'    : 0xD215,
        'ExposeIndex'       : 0xD216,
        'SonyBatteryLevel'  : 0xD218,
        'PictureEffect'     : 0xD21B,
        'ABFilter'          : 0xD21C,
        'ISO'               : 0xD21E,
        'AutoFocus'         : 0xD2C1,
        'Capture'           : 0xD2C2,
        'Movie'             : 0xD2C8,
        'StillImage'        : 0xD2C7,
        'ManualFocusMode'   : 0xD2D2,
        'FocusDistance'     : 0xD2D1,
        'FileFormat'        : 0xD253,
        'MovieFormat'       : 0xD241,
        'MovieSetting'      : 0xD242,
        'DateTime'          : 0xD223
        }
}

SONY_STILL_FORMAT = {
    'DataType': 'L',
    'Values': {
        'JPEG': 0x0002,
        'RAW' : 0x0003,
        'RAW+JPEG':0x0004,
        'RAW+HEIF':0x0005,
        'HEIF':0x0006,
    }
}

SONY_MOVIE_FORMAT = {
    'DataType': 'H',
    'Values': {
        'AVCHD':0x0000,
        'MP4':0x0001,
        'XAVC_S_4K':0x0002,
        'XAVC_S_HD':0x0003,
        'XAVC_HS_8K':0x0004,
        'XAVC_HS_4K':0x0005,
        'XAVC_S_L_4K':0x0006,
        'XAVC_S_L_HD':0x0007,
        'XAVC_S_I_4K':0x008,
        'XAVC_S_I_HD':0x0009,
        'XAVC_I':0x000A,
        'XAVC_L':0x000B
    }
}

SONY_MOVIE_SETTINGS = {
    'DataType': 'L',
    'Values': {
        '60p_50M' : 0x0001,
        '30p_50M' : 0x0002,
        '24p_50M' : 0x0003,
        '50p_50M' : 0x0004,
        '25p_50M' : 0x0005,
        '60i_24M' : 0x0006,
        '50i_24M_FX' : 0x0007,
        '60i_17M_FH' : 0x0008,
        '50i_17M_FH' : 0x0009,
        '60p_28M_PS' : 0x000A,
        '50p_28M_PS' : 0x000B,
        '24p_24M_FX' : 0x000C,
        '25p_24M_FX' : 0x000D,
        '24p_17M_FH' : 0x000E,
        '25p_17M_FH' : 0x000F,
        '120p_50M_1280x720' : 0x0010,
        '100p_50M_1280x720' : 0x0011,
        '1920x1080_30p_16M' : 0x0012,
        '1920x1080_25p_16M' : 0x0013,
        '1280x720_30p_6M' : 0x0014,
        '1280x720_25p_6M' : 0x0015,
        '1920x1080_60p_28M' : 0x0016,
        '1920x1080_50p_28M' : 0x0017,
        '60p_25M_XAVC_S_HD' : 0x0018,
        '50p_25M_XAVC_S_HD' : 0x0019,
        '30p_16M_XAVC_S_HD' : 0x001A,
        '25p_16M_XAVC_S_HD' : 0x001B,
        '120p_100M_1920x1080_XAVC_S_HD' : 0x001C,
        '100p_100M_1920x1080_XAVC_S_HD' : 0x001D,
        '120p_60M_1920x1080_XAVC_S_HD' : 0x001E,
        '100p_60M_1920x1080_XAVC_S_HD' : 0x001F,
        '30p_100M_XAVC_S_4K' : 0x0020,
        '25p_100M_XAVC_S_4K' : 0x0021,
        '24p_100M_XAVC_S_4K' : 0x0022,
        '30p_60M_XAVC_S_4K' : 0x0023,
        '25p_60M_XAVC_S_4K' : 0x0024,
        '24p_60M_XAVC_S_4K' : 0x0025,
        '600M_422_10bit' : 0x0026,
        '500M_422_10bit' : 0x0027,
        '400M_420_10bit' : 0x0028,
        '300M_422_10bit' : 0x0029,
        '280M_422_10bit' : 0x002A,
        '250M_422_10bit' : 0x002B,
        '240M_422_10bit' : 0x002C,
        '222M_422_10bit' : 0x002D,
        '200M_422_10bit' : 0x002E,
        '200M_420_10bit' : 0x002F,
        '200M_420_8bit' : 0x0030,
        '185M_422_10bit' : 0x0031,
        '150M_420_10bit' : 0x0032,
        '150M_420_8bit' : 0x0033,
        '140M_422_10bit' : 0x0034,
        '111M_422_10bit' : 0x0035,
        '100M_422_10bit' : 0x0036,
        '100M_420_10bit' : 0x0037,
        '100M_420_8bit' : 0x0038,
        '93M_422_10bit' : 0x0039,
        '89M_422_10bit' : 0x003A,
        '75M_420_10bit' : 0x003B,
        '60M_420_8bit' : 0x003C,
        '50M_422_10bit' : 0x003D,
        '50M_420_10bit' : 0x003E,
        '50M_420_8bit' : 0x003F,
        '45M_420_10bit' : 0x0040,
        '30M_420_10bit' : 0x0041,
        '25M_420_8bit' : 0x0042,
        '16M_420_8bit' : 0x0043,
        '520M_422_10bit' : 0x0044,
        '260M_422_10bit' : 0x0045,
    }
}

SONY_ISO_AUTO = 0xffffff

SONY_ISO_MODE = {
    'Values' : {
        'Normal': 0,
        'MultiFrameNR' : 1,
        'MultiFrameNR_High' : 2,
    }
}

SONY_BUTTON = {
    'DataType' : 'L',
    'Values' : {
        'Down' : 0x0002,
        'Up' : 0x0001
    }
}

SONY_VISIBILITY = {
    'DataType' : '<B',
    'Values' : {
        'Disabled' : 0x00,
        'Enabled' : 0x01,
        'DisplayOnly' : 0x02
    }
}

SONY_EXPMODE = {
    'DataType' : 'L',
    'Values' : {
        
        'Photo_M'                 : 0x00000001,
        'Photo_P'                 : 0x00010002,
        'Photo_Auto'              : 0x00048000,
        'Photo_AutoPlus'          : 0x00048001,

        'MovieP'            : 0x00078050,
        'MovieM'            : 0x00078053,
        'MovieA'            : 0x00078054,
        
        'HiFrameRate_P'     : 0x00088080,
        'HiFrameRate_M'     : 0x00088083,
        }
    }

VENDOR  =  {
    'DataType' : 'L',
    'Values': {
        'EastmanKodak' : 0x00000001,
        'SeikoEpson' : 0x00000002,
        'Agilent' : 0x00000003,
        'Polaroid' : 0x00000004,
        'AgfaGevaert' : 0x00000005,
        'Microsoft' : 0x00000006,
        'Equinox' : 0x00000007,
        'Viewquest' : 0x00000008,
        'STMicroelectronics' : 0x00000009,
        'Nikon' : 0x0000000A,
        'Canon' : 0x0000000B,
        'FotoNation' : 0x0000000C,
        'PENTAX' : 0x0000000D,
        'Fuji' : 0x0000000E,
        'Sony' : 0x00000011,  # Self-imposed.
        'NDD' : 0x00000012,  # ndd Medical Technologies
        'Samsung' : 0x0000001A,
        'Parrot' : 0x0000001B,
        'Panasonic' : 0x0000001C
        }
    }

PTP_OPCODE = {
    'DataType' : 'H',
    'Values': {
        'Undefined' : 0x1000,
        'GetDeviceInfo' : 0x1001,
        'OpenSession' : 0x1002,
        'CloseSession' : 0x1003,
        'GetStorageIDs' : 0x1004,
        'GetStorageInfo' : 0x1005,
        'GetNumObjects' : 0x1006,
        'GetObjectHandles' : 0x1007,
        'GetObjectInfo' : 0x1008,
        'GetObject' : 0x1009,
        'GetThumb' : 0x100A,
        'DeleteObject' : 0x100B,
        'SendObjectInfo' : 0x100C,
        'SendObject' : 0x100D,
        'InitiateCapture' : 0x100E,
        'FormatStore' : 0x100F,
        'ResetDevice' : 0x1010,
        'SelfTest' : 0x1011,
        'SetObjectProtection' : 0x1012,
        'PowerDown' : 0x1013,
        'GetDevicePropDesc' : 0x1014,
        'GetDevicePropValue' : 0x1015,
        'SetDevicePropValue' : 0x1016,
        'ResetDevicePropValue' : 0x1017,
        'TerminateOpenCapture' : 0x1018,
        'MoveObject' : 0x1019,
        'CopyObject' : 0x101A,
        'GetPartialObject' : 0x101B,
        'InitiateOpenCapture' : 0x101C,
        'StartEnumHandles' : 0x101D,
        'EnumHandles' : 0x101E,
        'StopEnumHandles' : 0x101F,
        'GetVendorExtensionMapss' : 0x1020,
        'GetVendorDeviceInfo' : 0x1021,
        'GetResizedImageObject' : 0x1022,
        'GetFilesystemManifest' : 0x1023,
        'GetStreamInfo' : 0x1024,
        'GetStream' : 0x1025
        }
    }

PTP_RESPCODE = {
    'DataType' : 'H',
    'Values': {
        'Undefined' : 0x2000,
        'OK' : 0x2001,
        'GeneralError' : 0x2002,
        'SessionNotOpen' : 0x2003,
        'InvalidTransactionID' : 0x2004,
        'OperationNotSupported' : 0x2005,
        'ParameterNotSupported' : 0x2006,
        'IncompleteTransfer' : 0x2007,
        'InvalidStorageId' : 0x2008,
        'InvalidObjectHandle' : 0x2009,
        'DevicePropNotSupported' : 0x200A,
        'InvalidObjectFormatCode' : 0x200B,
        'StoreFull' : 0x200C,
        'ObjectWriteProtected' : 0x200D,
        'StoreReadOnly' : 0x200E,
        'AccessDenied' : 0x200F,
        'NoThumbnailPresent' : 0x2010,
        'SelfTestFailed' : 0x2011,
        'PartialDeletion' : 0x2012,
        'StoreNotAvailable' : 0x2013,
        'SpecificationByFormatUnsupported' : 0x2014,
        'NoValidObjectInfo' : 0x2015,
        'InvalidCodeFormat' : 0x2016,
        'UnknownVendorCode' : 0x2017,
        'CaptureAlreadyTerminated' : 0x2018,
        'DeviceBusy' : 0x2019,
        'InvalidParentObject' : 0x201A,
        'InvalidDevicePropFormat' : 0x201B,
        'InvalidDevicePropValue' : 0x201C,
        'InvalidParameter' : 0x201D,
        'SessionAlreadyOpened' : 0x201E,
        'TransactionCanceled' : 0x201F,
        'SpecificationOfDestinationUnsupported' : 0x2020,
        'InvalidEnumHandle' : 0x2021,
        'NoStreamEnabled' : 0x2022,
        'InvalidDataset' : 0x2023,
    }
}

PTP_EVENTCODE = {
    'DataType' : 'H',
    'Values': {
        'Undefined' : 0x4000,
        'CancelTransaction' : 0x4001,
        'ObjectAdded' : 0x4002,
        'ObjectRemoved' : 0x4003,
        'StoreAdded' : 0x4004,
        'StoreRemoved' : 0x4005,
        'DevicePropChanged' : 0x4006,
        'ObjectInfoChanged' : 0x4007,
        'DeviceInfoChanged' : 0x4008,
        'RequestObjectTransfer' : 0x4009,
        'StoreFull' : 0x400A,
        'DeviceReset' : 0x400B,
        'StorageInfoChanged' : 0x400C,
        'CaptureComplete' : 0x400D,
        'UnreportedStatus' : 0x400E
    }
}

PTP_PROPCODE = {
    'DataType' : 'L',
    'Values': {
        'Undefined' : 0x5000,
        'BatteryLevel' : 0x5001,
        'FunctionalMode' : 0x5002,
        'ImageSize' : 0x5003,
        'CompressionSetting' : 0x5004,
        'WhiteBalance' : 0x5005,
        'RGBGain' : 0x5006,
        'FNumber' : 0x5007,
        'FocalLength' : 0x5008,
        'FocusDistance' : 0x5009,
        'FocusMode' : 0x500A,
        'ExposureMeteringMode' : 0x500B,
        'FlashMode' : 0x500C,
        'ExposureTime' : 0x500D,
        'ExposureProgramMode' : 0x500E,
        'ExposureIndex' : 0x500F,
        'ExposureBiasCompensation' : 0x5010,
        'DateTime' : 0x5011,
        'CaptureDelay' : 0x5012,
        'StillCaptureMode' : 0x5013,
        'Contrast' : 0x5014,
        'Sharpness' : 0x5015,
        'DigitalZoom' : 0x5016,
        'EffectMode' : 0x5017,
        'BurstNumber' : 0x5018,
        'BurstInterval' : 0x5019,
        'TimelapseNumber' : 0x501A,
        'TimelapseInterval' : 0x501B,
        'FocusMeteringMode' : 0x501C,
        'UploadURL' : 0x501D,
        'Artist' : 0x501E,
        'CopyrightInfo' : 0x501F,
    }
}

PTP_OBJFMTCODE = {
    'DataType': 'H',
    'Values': {
        'UndefinedAncilliary' : 0x3000,
        'Association' : 0x3001,
        'Script' : 0x3002,
        'Executable' : 0x3003,
        'Text' : 0x3004,
        'HTML' : 0x3005,
        'DPOF' : 0x3006,
        'AIFF' : 0x3007,
        'WAV' : 0x3008,
        'MP3' : 0x3009,
        'AVI' : 0x300A,
        'MPEG' : 0x300B,
        'ASF' : 0x300C,
        'QT' : 0x300D,
        # Images
        'UndefinedImage' : 0x3800,
        'EXIF_JPEG' : 0x3801,
        'TIFF_EP' : 0x3802,
        'FlashPix' : 0x3803,
        'BMP' : 0x3804,
        'CIFF' : 0x3805,
        'GIF' : 0x3807,
        'JFIF' : 0x3808,
        'PCD' : 0x3809,
        'PICT' : 0x380A,
        'PNG' : 0x380B,
        'TIFF' : 0x380D,
        'TIFF_IT' : 0x380E,
        'JP2' : 0x380F,
        'JPX' : 0x3810,
        'DNG' : 0x3811
    }
}

PTP_DATATYPE = {
    'DataType' : 'H',
    'Values' : {
        'Undefined' : {
            'Code': 0x0000,
            'PropLength': 0
            },
        'qq' : {
            'Code': 0x0009,
            'PropLength': 16
            },
        'q' : {
            'Code': 0x0007,
            'PropLength': 8
            },
        'l' : {
            'Code': 0x0005,
            'PropLength': 2
            },
        'h' : {
            'Code': 0x0003,
            'PropLength': 2
            },
        'b' : {
            'Code': 0x0001,
            'PropLength': 1
            },
        'QQ' : {
            'Code': 0x000a,
            'PropLength': 16
            },
        'Q' : {
            'Code': 0x0008,
            'PropLength': 8
            },
        'L' : {
            'Code': 0x0006,
            'PropLength': 2
            },
        'H' : {
            'Code': 0x0004,
            'PropLength': 2
            },
        'B' : {
            'Code': 0x0002,
            'PropLength': 1
            },
        's' : {
            'Code': 0xFFFF,
            'PropLength': 0
            }
        }
    }

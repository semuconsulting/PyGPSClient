"""
Examples of TTY command presets for a variety of GNSS and related devices

Copy those required to your *.json configuration file and invoke them
via the TTY Command dialog.

Created on 30 May 2025

:author: semuadmin
:copyright: 2025 SEMU Consulting
:license: BSD 3-Clause
"""

# ******************************************
# Septentrio Mosaic X5 Receiver
#
# Send an "Initialise Command Mode" string
# before sending further commands.
#
# Full details in https://www.septentrio.com/resources/mosaic-X5/mosaic-X5+Firmware+v4.14.10.1+Reference+Guide.pdf
# ******************************************
{
    "ttypresets_l": [
        "Initialise Command Mode; SSSSSSSSSS",
        "Display Help for all available commands; help, Overview",
        "Display Help for getReceiverCapabilities command; help, getReceiverCapabilities",
        "Display Help for getReceiverCapabilities command; help, grc",
        "List contents of current configuration file; lcf, Current",
        "Save current configuration to boot file; eccf, Current, Boot",
        "List receiver capabilities; grc",
        "Get command line interface version; gri",
        "List Current NMEA outputs; gno",
        "Enable NMEA messages; sno, Stream1, COM1, GGA+GLL+GSV+RMC, sec1",
        "Disable NMEA messages; sno, Stream1, none, none, off",
        "Enable Group stream; ssgp, Group1, MeasEpoch+PVTCartesian+DOP; sso, Stream2, COM1, Group1, sec1",
        "Disable Group stream; sso, Stream2, none, none, off",
        "Output next Measurement Epoch; esoc, COM1, MeasEpoch",
        "Enable PVTGeod stream; sso, Stream2, COM1, PVTGeod, sec1",
        "Enable Status stream; sso, Stream2, COM1, Status, sec1",
        "Enable RTCM3 messages on COM2 in base station mode;sr3o, COM2, RTCM1001+RTCM1002+RTCM1005+RTCM1006; sdio, COM2, , RTCMv3",
        "List Known Antenna Phase Centres; lai, Overview",
        "Turn ethernet interface on; seth, on",
    ],
}

# ******************************************
# Feyman IM19 IMU with Tilt Compensation
#
# Full details in http://www.feymani.com/en/uploadfile/2023/1008/20231008072903360.pdf
# ******************************************
{
    "ttypresets_l": [
        "Tilt Survey Setup; AT+LOAD_DEFAULT; AT+GNSS_PORT=PHYSICAL_UART2; AT+NASC_OUTPUT=UART1,ON; AT+LEVER_ARM2=0.0057,-0.0732,-0.0645; AT+CLUB_VECTOR=0,0,1.865; AT+INSTALL_ANGLE=0,180,0; AT+GNSS_CARD=OEM; AT+WORK_MODE=408; AT+CORRECT_HOLDER=ENABLE; AT+SET_PPS_EDGE=RISING; AT+AHRS=ENABLE; AT+MAG_AUTO_SAVE=ENABLE; AT+SAVE_ALL",
        "System reset CONFIRM; AT+SYSTEM_RESET",
        "Save the parameters CONFIRM AT+SAVE_ALL",
        "Update module firmware, see attachment for protocols; AT+UPDATE_APP",
        "Update Bootloader, see attachment for protocols; AT+UPDATE_BOOT",
        "Set the GNSS RTK receiver type; AT+GNSS_CARD=OEM",
        "Read parameters (SYSTEM/ALL); AT+READ_PARA=SYSTEM/ALL",
        "Loading default parameters; AT+LOAD_DEFAULT",
        "Installation angle estimation in tilt measurement applications; AT+AUTO_FIX=ENABLE/DISABLE",
        "Set the RTK pole vector to map the position to the end of the RTK pole; AT+CLUB_VECTOR=X,Y,Z",
        "Binary NAVI positioning output; AT+NAVI_OUTPUT=UART1,ON/OFF",
        "Ascii type NAVI positioning output; AT+NASC_OUTPUT=UART1,ON/OFF",
        "MEMS raw output; AT+MEMS_OUTPUT=UART1,ON/OFF",
        "GNSS raw output; AT+GNSS_OUTPUT=UART1,ON/OFF",
        "Set the lever arm; AT+LEVER_ARM=X,Y,Z",
        "Query whether time is synchronized between MEMS and GNSS; AT+CHECK_SYNC",
        "High-rate mode setting; AT+HIGH_RATE=ENABLE/DISABLE",
        "Module activation; AT+ACTIVATE_KEY=KEY",
        "Set the initial alignment speed threshold; AT+ALIGN_VEL=1.0",
        "Query the Firmware version; AT+VERSION",
        "Set GNSS serial port; AT+GNSS_PORT=PHYSICAL_UART2",
        "Set the module working mode; AT+WORK_MODE=X",
        "Set the module installation angle; AT+INSTALL_ANGLE=X,Y,Z",
        "Query the serial port number; AT+THIS_PORT",
        "Causes the filter to enter or exit stop mode; AT+FILTER_STOP=ENABLE/DISABLE",
        "UART n enters or exits the loopback mode; AT+LOOP_BACK=UARTn/NONE",
        "Filter Reset; AT+FILTER_RESET",
        "Check firmware CRC, N=firmware size; AT+CHECK_CRC=N",
        "Turn on or off RTK pole length compensation; AT+CORRECT_HOLDER=ENABLE/DISABLE",
        "Disable the output of all messages over the serial port x; AT+DISABLE_OUTPUT=UARTx",
        "Factory calibration command; AT+CALIBRATE_MODE2=STEP1/STEP2",
    ],
}

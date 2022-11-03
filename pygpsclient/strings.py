"""
ENGLISH language string literals for PyGPSClient application

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=line-too-long

TITLE = "PyGPSClient"

COPYRIGHTTXT = "\u00A9 SEMU Consulting 2020\nBSD-2 License. All Rights Reserved"

INTROTXT = "Welcome to PyGPSClient!"
INTROTXTNOPORTS = "Welcome to PyGPSClient!"

HELPTXT = "Help..About - display About dialog."

ABOUTTXT = (
    "PyGPSClient is a free, open-source NMEA, UBX & RTCM3 GNSS/GPS client "
    + "application written entirely in Python and tkinter. "
    + "Instructions and source code are available on GitHub at the link below."
)

# Message text
SETINITTXT = "Settings initialised"
VALERROR = "ERROR! Please correct highlighted entries"
SAVEERROR = "ERROR! File could not be saved to specified directory"
OPENFILEERROR = "ERROR! File could not be opened"
BADJSONERROR = "ERROR! Invalid metadata file"
NMEAVALERROR = "Value error in NMEA message: {}"
SEROPENERROR = "Error opening serial port {}"
FILEOPENERROR = "Error opening file {}"
NOWEBMAP = "Unable to display map."
NOWEBMAPKEY = NOWEBMAP + "\n\nMQAPIKEY not found or invalid."
NOWEBMAPHTTP = NOWEBMAP + "\n\nBad HTTP response: {}.\nCheck MQAPIKEY."
NOWEBMAPFIX = NOWEBMAP + "\n\nNo satellite fix."
NOWEBMAPCONN = NOWEBMAP + "\n\nCheck internet connection."
SAVETITLE = "Select Directory"
READTITLE = "Select File"
WAITNMEADATA = "Waiting for data..."
WAITUBXDATA = "Waiting for data..."
ENDOFFILE = "End of file reached"
STOPDATA = "Serial reader process stopped"
NOTCONN = "Not connected"
UBXPOLL = "Polling current UBX configuration..."

# Menu text
MENUFILE = "File"
MENUVIEW = "View"
MENUOPTION = "Options"
MENUSAVE = "Save Settings"
MENULOAD = "Load Settings"
MENUEXIT = "Exit"
MENUCAN = "Cancel"
MENURST = "Reset"
MENUHIDESE = "Hide Settings"
MENUSHOWSE = "Show Settings"
MENUHIDEUBX = "Hide UBX Config"
MENUSHOWUBX = "Show UBX Config"
MENUHIDESB = "Hide Status Bar"
MENUSHOWSB = "Show Status Bar"
MENUHIDECON = "Hide Console"
MENUSHOWCON = "Show Console"
MENUHIDEMAP = "Hide Map"
MENUSHOWMAP = "Show Map"
MENUHIDESATS = "Hide Satellites"
MENUSHOWSATS = "Show Satellites"
MENUUBXCONFIG = "UBX Configuration Dialog"
MENUNTRIPCONFIG = "NTRIP Configuration Dialog"
MENUHOWTO = "How To"
MENUABOUT = "About"
MENUHELP = "Help"

# Button text
BTNPLOT = "PLOT"
BTNSAVE = "Save"
BTNCAN = "Cancel"
BTNRST = "Reset"

# Label text
LBLPROTDISP = "Protocols Shown"
LBLDATADISP = "Console Display"
LBLUBXCONFIG = "UBX\nConfig"
LBLNTRIPCONFIG = "NTRIP\nClient"
LBLNTRIPGGAINT = "GGA Interval s"
LBLCTL = "Controls"
LBLSET = "Settings"
LBLCFGPRT = "CFG-PRT Protocol Configuration"
LBLCFGRATE = "CFG-RATE Navigation Solution Rate Configuration"
LBLCFGMSG = "CFG-MSG Message Rate Configuration"
LBLPRESET = "Preset UBX Configuration Commands"
LBLDATALOG = "DataLogging"
LBLSTREAM = "Stream\nfrom file"
LBLTRACKRECORD = "GPX Track"
LBLLEGEND = "Show Legend"
LBLSHOWUNUSED = "Show Unused Satellites"
LBLNTRIPSERVER = "Server"
LBLNTRIPPORT = "Port"
LBLNTRIPVERSION = "Version"
LBLNTRIPMOUNT = "Mountpoint"
LBLNTRIPUSER = "User"
LBLNTRIPPWD = "Password"
LBLNTRIPSTR = "Sourcetable"
LBLSOCKSERVE = "Socket Server /\nNTRIP Caster   "  # padded to align
LBLSERVERPORT = "Port"
LBLDEGFORMAT = "Degrees Format"
LBLSERVERMODE = "Mode"
LBLCFGDYN = "CFG-* Other Configuration"
LBLGGALIVE = "Receiver"
LBLGGAFIXED = "Fixed Reference"
LBLUDPORT = "USER-DEFINED PORT"

# Dialog text
DLGUBXCONFIG = "UBX Configuration"
DLGNTRIPCONFIG = "NTRIP Client Configuration"
DLGABOUT = "PyGPSClient"
DLGHOWTO = "How To Use PyGPSCLient"
DLGRESET = "Confirm Reset"
DLGSAVE = "Confirm Save"
DLGRESETCONFIRM = (
    "Are you sure you want to reset the\ncurrent configuration to the\nfactory default?"
)
DLGSAVECONFIRM = "Are you sure you want to save\nthe current configuration?"

# UBX Preset Command Descriptions
PSTRESET = "CFG-CFG - RESTORE FACTORY DEFAULTS"
PSTSAVE = "CFG-CFG - SAVE CURRENT CONFIGURATION"
PSTMINNMEAON = "CFG-MSG - Turn ON minimum NMEA msgs"
PSTALLNMEAON = "CFG-MSG - Turn ON all NMEA msgs"
PSTALLNMEAOFF = "CFG-MSG - Turn OFF all NMEA msgs"
PSTMINUBXON = "CFG-MSG - Turn ON minimum UBX NAV msgs"
PSTALLUBXON = "CFG-MSG - Turn ON all UBX NAV msgs"
PSTALLUBXOFF = "CFG-MSG - Turn OFF all UBX NAV msgs"
PSTALLINFON = "CFG-INF - Turn ON all INF msgs"
PSTALLINFOFF = "CFG-INF - Turn OFF all non-error INF msgs"
PSTALLLOGON = "CFG-MSG - Turn ON all LOG msgs"
PSTALLLOGOFF = "CFG-MSG - Turn OFF all LOG msgs"
PSTALLMONON = "CFG-MSG - Turn ON all MON msgs"
PSTALLMONOFF = "CFG-MSG - Turn OFF all MON msgs"
PSTALLRXMON = "CFG-MSG - Turn ON all RXM msgs"
PSTALLRXMOFF = "CFG-MSG - Turn OFF all RXM msgs"
PSTPOLLPORT = "CFG-PRT - Poll Port config"
PSTPOLLINFO = "CFG-INF - Poll Info message config"
PSTPOLLALLCFG = "CFG-xxx - Poll All Configuration Messages"
PSTPOLLALLNAV = "NAV(2)-xxx - Poll All Navigation Messages"

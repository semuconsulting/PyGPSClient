"""
ENGLISH language string literals for PyGPSClient application

Created on 12 Sep 2020

@author: semuadmin
"""
# pylint: disable=line-too-long

TITLE = "PyGPSClient"

COPYRIGHTTXT = "\u00A9 SEMU Consulting 2020\nBSD 3 License. All Rights Reserved"

INTROTXT = "Welcome to PyGPSClient!"
INTROTXTNOPORTS = (
    "Welcome to PyGPSClient! Please connect a serial GPS device and restart."
)

HELPTXT = "Help..About - display About dialog."

ABOUTTXT = (
    "PyGPSClient is a free, open-source NMEA & UBX GNSS/GPS client application written"
    + " entirely in Python and tkinter.\n\n"
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
NOWEBMAPERROR1 = "Map not available."
NOWEBMAPERROR2 = "mqapikey file not found or invalid."
NOWEBMAPERROR3 = "Unable to download web map."
NOWEBMAPERROR4 = "Check Internet connection."
NOWEBMAPERROR5 = "No satellite fix."
WEBMAPHTTPERROR = "HTTP error downloading web map. Are you connected to the Internet?"
WEBMAPERROR = "Error downloading web map"
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
MENUHOWTO = "How To"
MENUABOUT = "About"
MENUHELP = "Help"

# Button text
BTNPLOT = "PLOT"
BTNSAVE = "Save"
BTNCAN = "Cancel"
BTNRST = "Reset"

# Label text
LBLPROTDISP = "Protocols Displayed"
LBLDATADISP = "Console Display"
LBLUBXCONFIG = "UBX Configuration"
LBLCTL = "Controls"
LBLSET = "Settings"
LBLCFGPRT = "CFG-PRT Protocol Configuration"
LBLCFGMSG = "CFG-MSG Message Rate Configuration"
LBLPRESET = "Preset UBX Configuration Commands"
LBLDATALOG = "Enable DataLog"
LBLSTREAM = "Stream\nfrom file"
LBLTRACKRECORD = "Record GPX Track"
LBLLEGEND = "Show Legend"
LBLSHOWNULL = "Show Zero Signal"

# Dialog text
DLGUBXCONFIG = "UBX Configuration"
DLGABOUT = "PyGPSClient"
DLGHOWTO = "How To Use PyGPSCLient"
DLGRESET = "Confirm Reset"
DLGSAVE = "Confirm Save"
DLGRESETCONFIRM = (
    "Are you sure you want to reset the\ncurrent configuration to the\nfactory default?"
)
DLGSAVECONFIRM = "Are you sure you want to save\nthe current configuration?\nNOTE: This only works on devices with persistent storage\ne.g. battery-backed RAM, Flash or EEPROM"

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
PSTPOLLALL = "CFG-xxx - Poll Everything Available"

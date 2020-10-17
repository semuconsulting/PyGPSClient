'''
Zeichenfolgenliterale in deutsche Sprache für die PyGPSClient-Anwendung

Erstellt am 17 Oct. 2020

@author: semuadmin
'''
# pylint: disable=line-too-long

TITLE = "PyGPSClient"
WIKIURL = "https://en.wikipedia.org/wiki/NMEA_0183"
GITHUBURL = "https://github.com/semuconsulting/PyGPSClient"

COPYRIGHTTXT = "\u00A9 SEMU Consulting 2020 \nBSD 3-Lizenz. Alle Rechte vorbehalten"

INTROTXT = "Willkommen bei PyGPSClient!"
INTROTXTNOPORTS = "Willkommen bei PyGPSClient! Bitte schließen Sie ein serielles GPS-Gerät an und starten Sie es neu."

HELPTXT = "Hilfe ... Über - Dialogfeld' Info anzeigen '."

ABOUTTXT = "PyGPSClient ist eine kostenlose Open-Source-NMEA- und UBX-GNSS/GPS-Client-Anwendung, die geschrieben wurde" \
    + "vollständig in Python und tkinter.\n\n" \
    + "Anweisungen und Quellcode sind auf GitHub unter dem folgenden Link verfügbar."

# Nachrichtentext
SETINITTXT = "Einstellungen initialisiert"
VALERROR = "FEHLER! Bitte hervorgehobene Einträge korrigieren"
SAVEERROR = "FEHLER! Datei konnte nicht im angegebenen Verzeichnis gespeichert werden"
OPENFILEERROR = "FEHLER! Datei konnte nicht geöffnet werden"
BADJSONERROR = "FEHLER! Ungültige Metadatendatei"
NMEAVALERROR = "Wertfehler in NMEA-Nachricht: {}"
SEROPENERROR = "Fehler beim Öffnen der seriellen Schnittstelle {}"
NOWEBMAPERROR1 = "Karte nicht verfügbar."
NOWEBMAPERROR2 = "mqapikey-Datei nicht gefunden oder ungültig."
NOWEBMAPERROR3 = "Webkarte kann nicht heruntergeladen werden."
NOWEBMAPERROR4 = "Überprüfen Sie die Internetverbindung."
NOWEBMAPERROR5 = "Kein Satellitenfix."
WEBMAPHTTPERROR = 'HTTP-Fehler beim Herunterladen der Webkarte. Sind Sie mit dem Internet verbunden? '
WEBMAPERROR = 'Fehler beim Herunterladen der Webkarte'
SAVETITLE = "Verzeichnis speichern auswählen"
READTITLE = "Datei zum Importieren auswählen"
WAITNMEADATA = "Warten auf NMEA-Daten ..."
WAITUBXDATA = "Warten auf UBX-Daten ..."
STOPDATA = "Serieller Lesevorgang gestoppt"
NOTCONN = "Nicht verbunden"
UBXPOLL = "Aktuelle UBX-Konfiguration abrufen ..."

# Menütext
MENUFILE = "Datei"
MENUVIEW = "Anzeigen"
MENUOPTION = "Optionen"
MENUSAVE = "Einstellungen speichern"
MENULOAD = "Ladeeinstellungen"
MENUEXIT = "Beenden"
MENUCAN = "Abbrechen"
MENURST = "Zurücksetzen"
MENUHIDESE = "Einstellungen ausblenden"
MENUSHOWSE = "Einstellungen anzeigen"
MENUHIDEUBX = "UBX-Konfiguration ausblenden"
MENUSHOWUBX = "UBX-Konfiguration anzeigen"
MENUHIDESB = "Statusleiste ausblenden"
MENUSHOWSB = "Statusleiste anzeigen"
MENUHIDECON = "Konsole ausblenden"
MENUSHOWCON = "Konsole anzeigen"
MENUHIDEMAP = "Karte ausblenden"
MENUSHOWMAP = "Karte anzeigen"
MENUHIDESATS = "Satelliten ausblenden"
MENUSHOWSATS = "Satelliten anzeigen"
MENUUBXCONFIG = "UBX-Konfigurationsdialog"
MENUHOWTO = "How To"
MENUABOUT = "Über"
MENUHELP = "Hilfe"

# Schaltflächentext
BTNPLOT = "PLOT"
BTNSAVE = "Speichern"
BTNCAN = "Abbrechen"
BTNRST = "Zurücksetzen"

# Beschriftungstext
LBLPROTDISP = "Angezeigte Protokolle"
LBLDATADISP = "Konsolenanzeige"
LBLUBXCONFIG = "UBX-Konfiguration"
LBLCTL = "Kontrollen"
LBLSET = "Einstellungen"
LBLCFGPRT = "CFG-PRT-Port- und Protokollkonfiguration"
LBLCFGMSG = "CFG-MSG - UBX- und NMEA-Nachrichtenrate / Portauswahl"
LBLPRESET = "Voreingestellte UBX-Konfigurationsbefehle"
LBLDATALOG = "Datenprotokollierung aktivieren"
LBLSTREAM = "Stream\nfrom file"

# Dialogtext
DLGUBXCONFIG = "UBX-Konfiguration"
DLGABOUT = "PyGPSClient"
DLGHOWTO = "Verwendung von PyGPSCLient"
DLGRESET = "Reset bestätigen"
DLGSAVE = "Speichern bestätigen"
DLGRESETCONFIRM = "Möchten Sie die aktuelle Konfiguration im \nbatteriegepufferten RAM auf den\nStandardwert factory zurücksetzen?"
DLGSAVECONFIRM = "Möchten Sie die aktuelle Konfiguration\nwirklich im batteriegepufferten RAM speichern?"

# Beschreibungen der voreingestellten UBX-Befehle
PSTRESET = 'CFG-CFG - FACTORY DEFAULTS WIEDERHERSTELLEN'
PSTSAVE = 'CFG-CFG - Aktuelle Konfiguration im RAM speichern'
PSTMINNMEAON = 'CFG-MSG - Mindest-NMEA-Nachrichten einschalten'
PSTALLNMEAON = 'CFG-MSG - Alle NMEA-Nachrichten einschalten'
PSTALLNMEAOFF = 'CFG-MSG - Alle NMEA-Nachrichten ausschalten'
PSTMINUBXON = 'CFG-MSG - Mindest-UBX-NAV-Nachrichten einschalten'
PSTALLUBXON = 'CFG-MSG - Alle UBX NAV-Nachrichten einschalten'
PSTALLUBXOFF = 'CFG-MSG - Alle UBX NAV-Nachrichten ausschalten'
PSTALLINFON = 'CFG-INF - Alle INF-Nachrichten einschalten'
PSTALLINFOFF = 'CFG-INF - Alle fehlerfreien INF-Nachrichten ausschalten'
PSTALLLOGON = 'CFG-MSG - Alle LOG-Nachrichten einschalten'
PSTALLLOGOFF = 'CFG-MSG - Alle LOG-Nachrichten ausschalten'
PSTALLMONON = 'CFG-MSG - Alle MON-Nachrichten einschalten'
PSTALLMONOFF = 'CFG-MSG - Alle MON-Nachrichten ausschalten'
PSTALLRXMON = 'CFG-MSG - Alle RXM-Nachrichten einschalten'
PSTALLRXMOFF = 'CFG-MSG - Alle RXM-Nachrichten ausschalten'
PSTPOLLPORT = 'CFG-PRT - Poll Port-Konfiguration'
PSTPOLLINFO = 'CFG-INF - Konfiguration der Poll Info-Nachricht'

'''
Letterali stringa in lingua Italiana per l'applicazione PyGPSClient

Creato il 17 Oct. 2020

@author: semuadmin
'''
# pylint: disable=line-too-long

TITLE = "PyGPSClient"
WIKIURL = "https://en.wikipedia.org/wiki/NMEA_0183"
GITHUBURL = "https://github.com/semuconsulting/PyGPSClient"

COPYRIGHTTXT = "\u00A9 SEMU Consulting 2020\nLicenza BSD 3. Tutti i diritti riservati"

INTROTXT = "Benvenuto in PyGPSClient!"
INTROTXTNOPORTS = "Benvenuto in PyGPSClient! Connetti un dispositivo GPS seriale e riavvia."

HELPTXT = "Aiuto..Informazioni - visualizza la finestra di dialogo Informazioni."

ABOUTTXT = "PyGPSClient è un'applicazione client NMEA e UBX GPS gratuita e open source scritta" \
    + "interamente in Python e tkinter.\n\n" \
    + "Le istruzioni e il codice sorgente sono disponibili su Github al link sottostante."

# Messaggio di testo
SETINITTXT = "Impostazioni inizializzate"
VALERROR = "ERRORE! Correggi le voci evidenziate"
SAVEERROR = "ERRORE! Impossibile salvare il file nella directory specificata"
OPENFILEERROR = "ERRORE! Impossibile aprire il file"
BADJSONERROR = "ERRORE! File di metadati non valido"
NMEAVALERROR = "Errore di valore nel messaggio NMEA: {}"
SEROPENERROR = "Errore durante l'apertura della porta seriale {}"
NOWEBMAPERROR1 = "Mappa non disponibile."
NOWEBMAPERROR2 = "file mqapikey non trovato o non valido."
NOWEBMAPERROR3 = "Impossibile scaricare la mappa web."
NOWEBMAPERROR4 = "Controlla la connessione a Internet."
NOWEBMAPERROR5 = "Nessun fix satellitare."
WEBMAPHTTPERROR = "Errore HTTP durante il download della mappa web. Sei connesso a Internet?"
WEBMAPERROR = 'Errore durante il download della mappa web'
SAVETITLE = "Seleziona Salva directory"
SELTITLE = "Seleziona file per importazione"
WAITNMEADATA = "In attesa di dati NMEA ..."
WAITUBXDATA = "In attesa di dati UBX ..."
STOPDATA = "Processo del lettore seriale interrotto"
NOTCONN = "Non connesso"
UBXPOLL = "Polling attuale configurazione UBX ..."

# Testo del menu
MENUFILE = "File"
MENUVIEW = "Visualizza"
MENUOPTION = "Opzioni"
MENUSAVE = "Salva impostazioni"
MENULOAD = "Carica impostazioni"
MENUEXIT = "Esci"
MENUCAN = "Annulla"
MENURST = "Ripristina"
MENUHIDESE = "Nascondi impostazioni"
MENUSHOWSE = "Mostra impostazioni"
MENUHIDEUBX = "Nascondi UBX Config"
MENUSHOWUBX = "Mostra configurazione UBX"
MENUHIDESB = "Nascondi barra di stato"
MENUSHOWSB = "Mostra barra di stato"
MENUHIDECON = "Nascondi console"
MENUSHOWCON = "Mostra console"
MENUHIDEMAP = "Nascondi mappa"
MENUSHOWMAP = "Mostra mappa"
MENUHIDESATS = "Nascondi satelliti"
MENUSHOWSATS = "Mostra satelliti"
MENUUBXCONFIG = "Finestra di dialogo Configurazione UBX"
MENUHOWTO = "Come fare per"
MENUABOUT = "Informazioni"
MENUHELP = "Aiuto"

# Testo pulsante
BTNPLOT = "PLOT"
BTNSAVE = "Salva"
BTNCAN = "Annulla"
BTNRST = "Reimposta"

# Testo etichetta
LBLPROTDISP = "Protocolli visualizzati"
LBLDATADISP = "Console Display"
LBLUBXCONFIG = "Configurazione UBX"
LBLCTL = "Controlli"
LBLSET = "Impostazioni"
LBLCFGPRT = "Configurazione porta e protocollo CFG-PRT"
LBLCFGMSG = "CFG-MSG - Velocità messaggi UBX e NMEA / Selezione porta"
LBLPRESET = "Comandi di configurazione UBX preimpostati"

# Testo della finestra di dialogo
DLGUBXCONFIG = "Configurazione UBX"
DLGABOUT = "PyGPSClient"
DLGHOWTO = "Come utilizzare PyGPSCLient"
DLGRESET = "Conferma ripristino"
DLGSAVE = "Conferma salvataggio"
DLGRESETCONFIRM = "Sei sicuro di voler ripristinare la\nconfigurazione corrente al\npredefinito di fabbrica nella RAM supportata da batteria?"
DLGSAVECONFIRM = "Sei sicuro di voler salvare\nla configurazione corrente nella\nRAM supportata da batteria?"

# Descrizioni dei comandi preimpostati di UBX
PSTRESET = "CFG-CFG - RIPRISTINA I DEFAULTS DI FABBRICA"
PSTSAVE = 'CFG-CFG - Salva la configurazione corrente nella RAM'
PSTMINNMEAON = 'CFG-MSG - Attiva messaggi NMEA minimi'
PSTALLNMEAON = 'CFG-MSG - Attiva tutti i messaggi NMEA'
PSTALLNMEAOFF = 'CFG-MSG - Disattiva tutti i messaggi NMEA'
PSTMINUBXON = 'CFG-MSG - Attiva i messaggi UBX NAV minimi'
PSTALLUBXON = 'CFG-MSG - Attiva tutti i messaggi UBX NAV'
PSTALLUBXOFF = 'CFG-MSG - Disattiva tutti i messaggi UBX NAV'
PSTALLINFON = 'CFG-INF - Attiva tutti i messaggi INF'
PSTALLINFOFF = 'CFG-INF - Disattiva tutti i messaggi INF non di errore'
PSTALLLOGON = 'CFG-MSG - Attiva tutti i messaggi di LOG'
PSTALLLOGOFF = 'CFG-MSG - Disattiva tutti i messaggi di LOG'
PSTALLMONON = 'CFG-MSG - Attiva tutti i messaggi MON'
PSTALLMONOFF = 'CFG-MSG - Disattiva tutti i messaggi MON'
PSTALLRXMON = 'CFG-MSG - Attiva tutti i messaggi RXM'
PSTALLRXMOFF = 'CFG-MSG - Disattiva tutti i messaggi RXM'
PSTPOLLPORT = 'CFG-PRT - Poll Port config'
PSTPOLLINFO = 'CFG-INF - Configurazione messaggio informazioni sondaggio'

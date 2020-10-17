'''
Littéraux de chaîne de langue FRANCAIS pour l'application PyGPSClient

Créé le 17 Oct 2020

@author: semuadmin
'''
# pylint: disable=line-too-long

TITLE = "PyGPSClient"
WIKIURL = "https://en.wikipedia.org/wiki/NMEA_0183"
GITHUBURL = "https://github.com/semuconsulting/PyGPSClient"

COPYRIGHTTXT = "\u00A9 SEMU Consulting 2020 \nLicence BSD 3. Tous droits réservés"

INTROTXT = "Bienvenue dans PyGPSClient!"
INTROTXTNOPORTS = "Bienvenue dans PyGPSClient! Veuillez connecter un périphérique GPS série et redémarrer."

HELPTXT = "Aide..À propos - afficher la boîte de dialogue À propos."

ABOUTTXT = "PyGPSClient est une application client NMEA & UBX GPS gratuite et open-source écrite" \
    + "entièrement en Python et tkinter.\n\n" \
    + "Les instructions et le code source sont disponibles sur Github via le lien ci-dessous."

# Texte du message
SETINITTXT = "Paramètres initialisés"
VALERROR = "ERREUR! Veuillez corriger les entrées en surbrillance"
SAVEERROR = "ERREUR! Le fichier n'a pas pu être enregistré dans le répertoire spécifié"
OPENFILEERROR = "ERREUR! Le fichier n'a pas pu être ouvert"
BADJSONERROR = "ERREUR! Fichier de métadonnées invalide"
NMEAVALERROR = "Erreur de valeur dans le message NMEA: {}"
SEROPENERROR = "Erreur lors de l'ouverture du port série {}"
NOWEBMAPERROR1 = "Carte non disponible."
NOWEBMAPERROR2 = "Fichier mqapikey introuvable ou invalide."
NOWEBMAPERROR3 = "Impossible de télécharger la carte Web."
NOWEBMAPERROR4 = "Vérifiez la connexion Internet."
NOWEBMAPERROR5 = "Aucun correctif satellite."
WEBMAPHTTPERROR = 'Erreur HTTP lors du téléchargement de la carte Web. Êtes-vous connecté à Internet? '
WEBMAPERROR = 'Erreur lors du téléchargement de la carte Web'
SAVETITLE = "Sélectionnez Enregistrer le répertoire"
SELTITLE = "Sélectionner le fichier à importer"
WAITNMEADATA = "En attente de données NMEA ..."
WAITUBXDATA = "En attente de données UBX ..."
STOPDATA = "Processus du lecteur série arrêté"
NOTCONN = "Non connecté"
UBXPOLL = "Interrogation de la configuration UBX actuelle ..."

# Texte du menu
MENUFILE = "Fichier"
MENUVIEW = "Afficher"
MENUOPTION = "Options"
MENUSAVE = "Enregistrer les paramètres"
MENULOAD = "Charger les paramètres"
MENUEXIT = "Quitter"
MENUCAN = "Annuler"
MENURST = "Réinitialiser"
MENUHIDESE = "Masquer les paramètres"
MENUSHOWSE = "Afficher les paramètres"
MENUHIDEUBX = "Masquer la configuration UBX"
MENUSHOWUBX = "Afficher la configuration UBX"
MENUHIDESB = "Masquer la barre d'état"
MENUSHOWSB = "Afficher la barre d'état"
MENUHIDECON = "Masquer la console"
MENUSHOWCON = "Afficher la console"
MENUHIDEMAP = "Masquer la carte"
MENUSHOWMAP = "Afficher la carte"
MENUHIDESATS = "Masquer les satellites"
MENUSHOWSATS = "Afficher les satellites"
MENUUBXCONFIG = "Boîte de dialogue de configuration UBX"
MENUHOWTO = "Comment faire"
MENUABOUT = "À propos de"
MENUHELP = "Aide"

# Texte du bouton
BTNPLOT = "PLOT"
BTNSAVE = "Enregistrer"
BTNCAN = "Annuler"
BTNRST = "Réinitialiser"

# Texte de l'étiquette
LBLPROTDISP = "Protocoles affichés"
LBLDATADISP = "Affichage de la console"
LBLUBXCONFIG = "Configuration UBX"
LBLCTL = "Contrôles"
LBLSET = "Paramètres"
LBLCFGPRT = "Configuration du port et du protocole CFG-PRT"
LBLCFGMSG = "CFG-MSG - Sélection du débit / port des messages UBX & NMEA"
LBLPRESET = "Commandes de configuration UBX préréglées"

# Texte de la boîte de dialogue
DLGUBXCONFIG = "Configuration UBX"
DLGABOUT = "PyGPSClient"
DLGHOWTO = "Comment utiliser PyGPSCLient"
DLGRESET = "Confirmer la réinitialisation"
DLGSAVE = "Confirmer l'enregistrement"
DLGRESETCONFIRM = "Êtes-vous sûr de vouloir réinitialiser la\nconfiguration actuelle sur la\nfiguration d'usine par défaut dans la RAM sauvegardée par batterie?"
DLGSAVECONFIRM = "Êtes-vous sûr de vouloir enregistrer\nla configuration actuelle dans\nla RAM sauvegardée sur batterie?"

# Description des commandes de préréglage UBX
PSTRESET = 'CFG-CFG - RESTAURER LES DEFAUTS USINE'
PSTSAVE = 'CFG-CFG - Enregistrer la configuration actuelle dans la RAM'
PSTMINNMEAON = 'CFG-MSG - Activer les msgs NMEA minimum'
PSTALLNMEAON = 'CFG-MSG - Activer tous les msgs NMEA'
PSTALLNMEAOFF = 'CFG-MSG - Désactiver tous les msgs NMEA'
PSTMINUBXON = 'CFG-MSG - Activer les msgs UBX NAV minimum'
PSTALLUBXON = 'CFG-MSG - Active tous les msgs UBX NAV'
PSTALLUBXOFF = 'CFG-MSG - Désactiver tous les msgs UBX NAV'
PSTALLINFON = 'CFG-INF - Activer tous les msgs INF'
PSTALLINFOFF = 'CFG-INF - Désactive tous les msgs INF sans erreur'
PSTALLLOGON = 'CFG-MSG - Activer tous les msgs du journal'
PSTALLLOGOFF = 'CFG-MSG - Désactiver tous les msgs du journal'
PSTALLMONON = 'CFG-MSG - Activer tous les messages MON'
PSTALLMONOFF = 'CFG-MSG - Désactiver tous les messages MON'
PSTALLRXMON = 'CFG-MSG - Active tous les msgs RXM'
PSTALLRXMOFF = 'CFG-MSG - Désactiver tous les msgs RXM'
PSTPOLLPORT = "CFG-PRT - Configuration du port d'interrogation"
PSTPOLLINFO = "CFG-INF - Configuration du message d'information de sondage"

'''
Literales de cadena de idioma Espagnol para la aplicación PyGPSClient

Creado el 17 Oct. 2020

@author: semuadmin
'''
# pylint: disable=line-too-long

TITLE = "PyGPSClient"
WIKIURL = "https://en.wikipedia.org/wiki/NMEA_0183"
GITHUBURL = "https://github.com/semuconsulting/PyGPSClient"

COPYRIGHTTXT = "\u00A9 SEMU Consulting 2020 \nBSD 3 Licencia. Todos los derechos reservados"

INTROTXT = "¡Bienvenido a PyGPSClient!"
INTROTXTNOPORTS = "¡Bienvenido a PyGPSClient! Por favor, conecte un dispositivo GPS serial y reinicie."

HELPTXT = "Ayuda..Acerca de - mostrar el diálogo Acerca de"

ABOUTTXT = "PyGPSClient es una aplicación cliente de GPS NMEA y UBX de código abierto y gratuita escrita" \
    + "completamente en Python y tkinter.\n\n" \
    + "Las instrucciones y el código fuente están disponibles en Github en el siguiente enlace"

# Mensaje de texto
SETINITTXT = "Configuración inicializada"
VALERROR = "¡ERROR! Corrija las entradas resaltadas"
SAVEERROR = "¡ERROR! No se pudo guardar el archivo en el directorio especificado"
OPENFILEERROR = "¡ERROR! No se pudo abrir el archivo"
BADJSONERROR = "¡ERROR! Archivo de metadatos no válido"
NMEAVALERROR = "Error de valor en el mensaje NMEA: {}"
SEROPENERROR = "Error al abrir el puerto serie {}"
NOWEBMAPERROR1 = "Mapa no disponible"
NOWEBMAPERROR2 = "archivo mqapikey no encontrado o inválido"
NOWEBMAPERROR3 = "No se puede descargar el mapa web"
NOWEBMAPERROR4 = "Compruebe la conexión a Internet"
NOWEBMAPERROR5 = "Sin arreglo de satélite"
WEBMAPHTTPERROR = 'Error HTTP al descargar el mapa web. Estás conectado a Internet?'
WEBMAPERROR = 'Error al descargar el mapa web'
SAVETITLE = "Seleccione Guardar directorio"
SELTITLE = "Seleccionar archivo para importar"
WAITNMEADATA = "Esperando datos NMEA ..."
WAITUBXDATA = "Esperando datos UBX ..."
STOPDATA = "Proceso de lectura serial detenido"
NOTCONN = "No conectado"
UBXPOLL = "Consultando la configuración actual de UBX ..."

# Texto del menú
MENUFILE = "Archivo"
MENUVIEW = "Ver"
MENUOPTION = "Opciones"
MENUSAVE = "Guardar configuración"
MENULOAD = "Cargar configuración"
MENUEXIT = "Salir"
MENUCAN = "Cancelar"
MENURST = "Reiniciar"
MENUHIDESE = "Ocultar configuración"
MENUSHOWSE = "Mostrar configuración"
MENUHIDEUBX = "Ocultar configuración UBX"
MENUSHOWUBX = "Mostrar configuración UBX"
MENUHIDESB = "Ocultar barra de estado"
MENUSHOWSB = "Mostrar barra de estado"
MENUHIDECON = "Ocultar consola"
MENUSHOWCON = "Mostrar consola"
MENUHIDEMAP = "Ocultar mapa"
MENUSHOWMAP = "Mostrar mapa"
MENUHIDESATS = "Ocultar satélites"
MENUSHOWSATS = "Mostrar satélites"
MENUUBXCONFIG = "Cuadro de diálogo de configuración de UBX"
MENUHOWTO = "Cómo"
MENUABOUT = "Acerca de"
MENUHELP = "Ayuda"

# Botón de texto
BTNPLOT = "PLOT"
BTNSAVE = "Guardar"
BTNCAN = "Cancelar"
BTNRST = "Reiniciar"

# Texto de etiqueta
LBLPROTDISP = "Protocolos mostrados"
LBLDATADISP = "Pantalla de consola"
LBLUBXCONFIG = "Configuración UBX"
LBLCTL = "Controles"
LBLSET = "Configuración"
LBLCFGPRT = "Configuración de protocolo y puerto CFG-PRT"
LBLCFGMSG = "CFG-MSG - Selección de puerto / velocidad de mensajes UBX y NMEA"
LBLPRESET = "Comandos de configuración preestablecidos de UBX"

# Texto de diálogo
DLGUBXCONFIG = "Configuración UBX"
DLGABOUT = "PyGPSClient"
DLGHOWTO = "Cómo utilizar PyGPSCLient"
DLGRESET = "Confirmar reinicio"
DLGSAVE = "Confirmar guardar"
DLGRESETCONFIRM = "Está seguro de que desea restablecer la\nconfiguración actual a la\npredeterminada de fábrica en la RAM con batería?"
DLGSAVECONFIRM = "Está seguro de que desea guardar\nla configuración actual en\nRAM respaldada por batería?"

# Descripciones de comandos predefinidos de UBX
PSTRESET = 'CFG-CFG - RESTAURAR LOS VALORES DE FÁBRICA'
PSTSAVE = 'CFG-CFG - Guardar la configuración actual en la RAM'
PSTMINNMEAON = 'CFG-MSG - Activar mensajes NMEA mínimos'
PSTALLNMEAON = 'CFG-MSG - Activar todos los mensajes NMEA'
PSTALLNMEAOFF = 'CFG-MSG - Desactivar todos los mensajes NMEA'
PSTMINUBXON = 'CFG-MSG - Activar mensajes mínimos UBX NAV'
PSTALLUBXON = 'CFG-MSG - Activar todos los mensajes de UBX NAV'
PSTALLUBXOFF = 'CFG-MSG - Desactivar todos los mensajes UBX NAV'
PSTALLINFON = 'CFG-INF - Activar todos los mensajes INF'
PSTALLINFOFF = 'CFG-INF - Apague todos los mensajes INF que no sean de error'
PSTALLLOGON = 'CFG-MSG - Activar todos los mensajes de registro'
PSTALLLOGOFF = 'CFG-MSG - Desactivar todos los mensajes de registro'
PSTALLMONON = 'CFG-MSG - Activar todos los mensajes MON'
PSTALLMONOFF = 'CFG-MSG - Apagar todos los mensajes MON'
PSTALLRXMON = 'CFG-MSG - Activar todos los mensajes RXM'
PSTALLRXMOFF = 'CFG-MSG - Apagar todos los mensajes RXM'
PSTPOLLPORT = 'CFG-PRT - Configuración del puerto de encuesta'
PSTPOLLINFO = 'CFG-INF - Configuración del mensaje de información de la encuesta'

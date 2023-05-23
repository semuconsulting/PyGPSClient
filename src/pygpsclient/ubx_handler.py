"""
UBX Protocol handler

Uses pyubx2 library for parsing

Created on 30 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from pyubx2 import UBXMessage, itow2utc

from pygpsclient.globals import DLGTSPARTN, DLGTUBX, GLONASS_NMEA
from pygpsclient.helpers import corrage2int, fix2desc, svid2gnssid
from pygpsclient.widgets import WDGSPECTRUM, WDGSYSMON


class UBXHandler:
    """
    UBXHandler class
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        self._cdb = 0
        self._raw_data = None
        self._parsed_data = None
        self.gsv_data = (
            []
        )  # Holds array of current satellites in view from NMEA GSV or UBX NAV-SVINFO sentences

    def process_data(self, raw_data: bytes, parsed_data: object):
        """
        Process relevant UBX message types

        :param bytes raw_data: raw data
        :param UBXMessage parsed_data: parsed data
        """

        if raw_data is None:
            return

        if parsed_data.identity[0:3] in ("ACK", "CFG"):
            self._process_ACK(parsed_data)
        elif parsed_data.identity in ("MON-VER", "MON-HW"):
            self._process_MONVER(parsed_data)
        elif parsed_data.identity in ("NAV-POSLLH", "NAV-HPPOSLLH"):
            self._process_NAV_POSLLH(parsed_data)
        elif parsed_data.identity in ("NAV-PVT", "NAV2-PVT"):
            self._process_NAV_PVT(parsed_data)
        elif parsed_data.identity == "NAV-VELNED":
            self._process_NAV_VELNED(parsed_data)
        elif parsed_data.identity in ("NAV-SAT", "NAV2-SAT"):
            self._process_NAV_SAT(parsed_data)
        elif parsed_data.identity in ("NAV-STATUS", "NAV2-STATUS)"):
            self._process_NAV_STATUS(parsed_data)
        elif parsed_data.identity == "NAV-SVINFO":
            self._process_NAV_SVINFO(parsed_data)
        elif parsed_data.identity == "NAV-SOL":
            self._process_NAV_SOL(parsed_data)
        elif parsed_data.identity in ("NAV-DOP", "NAV2-DOP"):
            self._process_NAV_DOP(parsed_data)
        elif parsed_data.identity == "HNR-PVT":
            self._process_HNR_PVT(parsed_data)
        elif parsed_data.identity == "RXM-RTCM":
            self._process_RXM_RTCM(parsed_data)
        elif parsed_data.identity == "MON-SPAN":
            self._process_MON_SPAN(parsed_data)
        elif parsed_data.identity == "MON-SYS":
            self._process_MON_SYS(parsed_data)
        elif parsed_data.identity == "MON-COMMS":
            self._process_MON_COMMS(parsed_data)
        elif parsed_data.identity == "RXM-SPARTN-KEY":
            self._process_RXM_SPARTN_KEY(parsed_data)

    def _process_ACK(self, msg: UBXMessage):
        """
        Process ACK-ACK & ACK-NAK sentences and CFG poll responses.

        :param UBXMessage msg: UBX config message
        """

        if self.__app.dialog(DLGTUBX) is not None:
            self.__app.dialog(DLGTUBX).update_pending(msg)

        # if SPARTN config dialog is open, send CFG & ACKs there
        if self.__app.dialog(DLGTSPARTN) is not None:
            self.__app.dialog(DLGTSPARTN).update_pending(msg)

        # if Spectrumview or Sysmon widgets are active, send ACKSs there
        if msg.identity in ("ACK-ACK", "ACK-NAK"):
            wdgs = self.__app.widgets
            for wdg in (WDGSYSMON, WDGSPECTRUM):
                if wdgs[wdg]["visible"]:
                    if msg.clsID == 6 and msg.msgID == 1:  # CFG-MSG
                        getattr(self.__app, wdgs[wdg]["frm"]).update_pending(msg)

    def _process_MONVER(self, msg: UBXMessage):
        """
        Process MON-VER & MON-HW sentences.

        :param UBXMessage msg: UBX config message
        """

        if self.__app.dialog(DLGTUBX) is not None:
            self.__app.dialog(DLGTUBX).update_pending(msg)

    def _process_MON_SYS(self, data: UBXMessage):
        """
        Process MON-SYS sentences - System Monitor Information.

        :param UBXMessage data: MON-SYS parsed message
        """

        sysdata = {}
        sysdata["bootType"] = data.bootType
        sysdata["cpuLoad"] = data.cpuLoad
        sysdata["cpuLoadMax"] = data.cpuLoadMax
        sysdata["memUsage"] = data.memUsage
        sysdata["memUsageMax"] = data.memUsageMax
        sysdata["ioUsage"] = data.ioUsage
        sysdata["ioUsageMax"] = data.ioUsageMax
        sysdata["runTime"] = data.runTime
        sysdata["noticeCount"] = data.noticeCount
        sysdata["warnCount"] = data.warnCount
        sysdata["errorCount"] = data.errorCount
        sysdata["tempValue"] = data.tempValue
        self.__app.gnss_status.sysmon_data = sysdata

    def _process_MON_COMMS(self, data: UBXMessage):
        """
        Process MON-COMMS sentences - Comms Port Information.

        :param UBXMessage data: MON-COMMS parsed message
        """

        commsdata = {}
        for i in range(1, data.nPorts + 1):
            idx = f"_{i:02}"
            pid = getattr(data, "portId" + idx)
            tx = getattr(data, "txUsage" + idx)
            txmax = getattr(data, "txPeakUsage" + idx)
            txbytes = getattr(data, "txBytes" + idx)
            txpending = getattr(data, "txPending" + idx)
            rx = getattr(data, "rxUsage" + idx)
            rxmax = getattr(data, "rxPeakUsage" + idx)
            rxbytes = getattr(data, "rxBytes" + idx)
            rxpending = getattr(data, "rxPending" + idx)
            commsdata[pid] = (
                tx,
                txmax,
                txbytes,
                txpending,
                rx,
                rxmax,
                rxbytes,
                rxpending,
            )
        self.__app.gnss_status.comms_data = commsdata

    def _process_NAV_POSLLH(self, data: UBXMessage):
        """
        Process NAV-(HP)POSLLH sentence - Latitude, Longitude, Height.

        :param UBXMessage data: NAV-(HP)POSLLH parsed message
        """

        self.__app.gnss_status.utc = itow2utc(data.iTOW)  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.alt = data.hMSL / 1000  # meters
        self.__app.gnss_status.hacc = data.hAcc / 1000  # meters
        self.__app.gnss_status.vacc = data.vAcc / 1000  # meters

    def _process_NAV_PVT(self, data: UBXMessage):
        """
        Process NAV-PVT sentence -  Navigation position velocity time solution.

        :param UBXMessage data: NAV-PVT parsed message
        """

        self.__app.gnss_status.utc = itow2utc(data.iTOW)  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.alt = data.hMSL / 1000  # meters
        self.__app.gnss_status.hacc = data.hAcc / 1000  # meters
        self.__app.gnss_status.vacc = data.vAcc / 1000  # meters
        self.__app.gnss_status.pdop = data.pDOP
        self.__app.gnss_status.sip = data.numSV
        self.__app.gnss_status.speed = data.gSpeed / 1000  # m/s
        self.__app.gnss_status.track = data.headMot
        self.__app.gnss_status.fix = fix2desc("NAV-PVT", data.fixType)
        if data.carrSoln > 0:
            self.__app.gnss_status.fix = fix2desc("NAV-PVT", data.carrSoln + 5)

        self.__app.gnss_status.diff_corr = data.difSoln
        if data.lastCorrectionAge != 0:
            self.__app.gnss_status.diff_age = corrage2int(data.lastCorrectionAge)

    def _process_NAV_VELNED(self, data: UBXMessage):
        """
        Process NAV-VELNED sentence - Velocity Solution in North East Down format.

        :param UBXMessage data: NAV-VELNED parsed message
        """

        self.__app.gnss_status.track = data.heading
        self.__app.gnss_status.speed = data.gSpeed / 100  # m/s

    def _process_NAV_SAT(self, data: UBXMessage):
        """
        Process NAV-SAT sentences - Space Vehicle Information.

        NB: For consistency with NMEA GSV and UBX NAV-SVINFO message types,
        this uses the NMEA SVID numbering range for GLONASS satellites
        (65 - 96) rather than the Slot ID (1-24) by default.
        To change this, set the GLONASS_NMEA flag in globals.py to False.

        :param UBXMessage data: NAV-SAT parsed message
        """

        settings = self.__app.frm_settings.config
        show_unused = settings["unusedsat"]
        self.gsv_data = []
        num_siv = int(data.numSvs)

        for i in range(num_siv):
            idx = f"_{i+1:02d}"
            gnssId = getattr(data, "gnssId" + idx)
            svid = getattr(data, "svId" + idx)
            # use NMEA GLONASS numbering (65-96) rather than slotID (1-24)
            if gnssId == 6 and svid < 25 and svid != 255 and GLONASS_NMEA:
                svid += 64
            elev = getattr(data, "elev" + idx)
            azim = getattr(data, "azim" + idx)
            cno = getattr(data, "cno" + idx)
            if cno == 0 and not show_unused:  # omit unused sats
                continue
            self.gsv_data.append((gnssId, svid, elev, azim, cno))

        self.__app.gnss_status.siv = len(self.gsv_data)
        self.__app.gnss_status.gsv_data = self.gsv_data

    def _process_NAV_STATUS(self, data: UBXMessage):
        """
        Process NAV-STATUS sentences - Status Information.

        :param UBXMessage data: NAV-STATUS parsed message
        """

        self.__app.gnss_status.diff_corr = data.diffSoln
        # self.__app.gnss_status.diff_age = "<60"
        self.__app.gnss_status.fix = fix2desc("NAV-STATUS", data.gpsFix)
        if data.carrSoln > 0:
            self.__app.gnss_status.fix = fix2desc("NAV-STATUS", data.carrSoln + 5)

    def _process_NAV_SVINFO(self, data: UBXMessage):
        """
        Process NAV-SVINFO sentences - Space Vehicle Information.

        NB: Since UBX Gen8 this message is deprecated in favour of NAV-SAT

        :param UBXMessage data: NAV-SVINFO parsed message
        """

        settings = self.__app.frm_settings.config
        show_unused = settings["unusedsat"]
        self.gsv_data = []
        num_siv = int(data.numCh)

        for i in range(num_siv):
            idx = f"_{i+1:02d}"
            svid = getattr(data, "svid" + idx)
            gnssId = svid2gnssid(svid)  # derive gnssId from svid
            elev = getattr(data, "elev" + idx)
            azim = getattr(data, "azim" + idx)
            cno = getattr(data, "cno" + idx)
            if cno == 0 and not show_unused:  # omit unused sats
                continue
            self.gsv_data.append((gnssId, svid, elev, azim, cno))

        self.__app.gnss_status.gsv_data = self.gsv_data

    def _process_NAV_SOL(self, data: UBXMessage):
        """
        Process NAV-SOL sentence - Navigation Solution.

        :param UBXMessage data: NAV-SOL parsed message
        """

        self.__app.gnss_status.pdop = data.pDOP
        self.__app.gnss_status.sip = data.numSV
        self.__app.gnss_status.fix = fix2desc("NAV-SOL", data.gpsFix)

    def _process_NAV_DOP(self, data: UBXMessage):
        """
        Process NAV-DOP sentence - Dilution of Precision.

        :param UBXMessage data: NAV-DOP parsed message
        """

        self.__app.gnss_status.pdop = data.pDOP
        self.__app.gnss_status.hdop = data.hDOP
        self.__app.gnss_status.vdop = data.vDOP

    def _process_HNR_PVT(self, data: UBXMessage):
        """
        Process HNR-PVT sentence -  High Rate Navigation position velocity time solution.

        :param UBXMessage data: HNR-PVT parsed message
        """

        self.__app.gnss_status.utc = itow2utc(data.iTOW)  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.alt = data.hMSL / 1000  # meters
        self.__app.gnss_status.hacc = data.hAcc / 1000  # meters
        self.__app.gnss_status.vacc = data.vAcc / 1000  # meters
        self.__app.gnss_status.speed = data.gSpeed / 1000  # m/s
        self.__app.gnss_status.track = data.headMot
        self.__app.gnss_status.fix = fix2desc("HNR-PVT", data.gpsFix)
        self.__app.gnss_status.diff_corr = data.DiffSoln
        if data.DiffSoln > 0:
            self.__app.gnss_status.fix = fix2desc("HNR-PVT", 6)

    def _process_RXM_RTCM(self, data: UBXMessage):
        """
        Process RXM-RTCM sentences - Status Information.

        :param UBXMessage data: RXM-RTCM parsed message
        """

        self.__app.gnss_status.diff_corr = data.msgUsed >= 1
        self.__app.gnss_status.diff_station = data.refStation

    def _process_MON_SPAN(self, data: UBXMessage):
        """
        Process MON-SPAN sentences - Spectrum Information.

        :param UBXMessage data: MON-SPAN parsed message
        """

        numrf = data.numRfBlocks
        rfbs = []
        for i in range(1, numrf + 1):
            idx = f"_{i:02}"
            spec = getattr(data, "spectrum" + idx)
            spn = getattr(data, "span" + idx)
            res = getattr(data, "res" + idx)
            ctr = getattr(data, "center" + idx)
            pga = getattr(data, "pga" + idx)
            rfbs.append((spec, spn, res, ctr, pga))

        self.__app.gnss_status.spectrum_data = rfbs

    def _process_RXM_SPARTN_KEY(self, data: UBXMessage):
        """
        Process RXM-SPARTN_KEY sentences - poll response.

        :param UBXMessage data: RXM-SPARTN_KEY poll response message
        """

        if self.__app.dialog(DLGTSPARTN) is not None:
            self.__app.dialog(DLGTSPARTN).update_pending(data)

"""
ubx_handler.py

UBX Protocol handler - handles all incoming UBX messages

Parses individual UBX messages (using pyubx2 library)
and adds selected attribute values to the app.gnss_status
data dictionary. This dictionary is then used to periodically
update the various user-selectable widget panels.

Created on 30 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging

from pyubx2 import UBXMessage, itow2utc

from pygpsclient.globals import GLONASS_NMEA, UTF8
from pygpsclient.helpers import corrage2int, fix2desc, ned2vector, svid2gnssid
from pygpsclient.strings import DLGTSPARTN, DLGTUBX, NA
from pygpsclient.widget_state import VISIBLE, WDGSPECTRUM, WDGSYSMON


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
        self.logger = logging.getLogger(__name__)

        self._cdb = 0
        self._raw_data = None
        self._parsed_data = None
        # Holds array of current satellites in view from NMEA GSV or UBX NAV-SVINFO sentences
        self.gsv_data = {}

    def process_data(self, raw_data: bytes, parsed_data: object):
        """
        Process relevant UBX message types

        :param bytes raw_data: raw data
        :param UBXMessage parsed_data: parsed data
        """

        if raw_data is None:
            return
        # self.logger.debug(f"data received {parsed_data.identity}")
        if parsed_data.identity[0:3] in ("ACK", "CFG"):
            self._process_ACK(parsed_data)
        elif parsed_data.identity == "ESF-ALG":
            self._process_ESF_ALG(parsed_data)
        elif parsed_data.identity == "HNR-ATT":
            self._process_HNR_ATT(parsed_data)
        elif parsed_data.identity == "HNR-PVT":
            self._process_HNR_PVT(parsed_data)
        elif parsed_data.identity == "NAV-ATT":
            self._process_NAV_ATT(parsed_data)
        elif parsed_data.identity in ("NAV-DOP", "NAV2-DOP"):
            self._process_NAV_DOP(parsed_data)
        elif parsed_data.identity in ("NAV-POSLLH", "NAV-HPPOSLLH"):
            self._process_NAV_POSLLH(parsed_data)
        elif parsed_data.identity in ("NAV-PVT", "NAV2-PVT"):
            self._process_NAV_PVT(parsed_data)
        elif parsed_data.identity in ("NAV-PVAT", "NAV2-PVAT"):
            self._process_NAV_PVAT(parsed_data)
        elif parsed_data.identity == "NAV-RELPOSNED":
            self._process_NAV_RELPOSNED(parsed_data)
        elif parsed_data.identity in ("NAV-SAT", "NAV2-SAT"):
            self._process_NAV_SAT(parsed_data)
        elif parsed_data.identity in ("NAV-STATUS", "NAV2-STATUS"):
            self._process_NAV_STATUS(parsed_data)
        elif parsed_data.identity == "NAV-SVIN":
            self._process_NAV_SVIN(parsed_data)
        elif parsed_data.identity == "NAV-SVINFO":
            self._process_NAV_SVINFO(parsed_data)
        elif parsed_data.identity == "NAV-SOL":
            self._process_NAV_SOL(parsed_data)
        elif parsed_data.identity == "NAV-VELNED":
            self._process_NAV_VELNED(parsed_data)
        elif parsed_data.identity == "MON-COMMS":
            self._process_MON_COMMS(parsed_data)
        elif parsed_data.identity == "MON-SPAN":
            self._process_MON_SPAN(parsed_data)
        elif parsed_data.identity == "MON-SYS":
            self._process_MON_SYS(parsed_data)
        elif parsed_data.identity == "MON-VER":
            self._process_MONVER(parsed_data)
        elif parsed_data.identity == "RXM-RTCM":
            self._process_RXM_RTCM(parsed_data)
        elif parsed_data.identity == "RXM-PMP":
            self._process_RXM_PMP(parsed_data)
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
            wdgs = self.__app.widget_state.state
            for wdg in (WDGSYSMON, WDGSPECTRUM):
                if wdgs[wdg][VISIBLE]:
                    if msg.clsID == 6 and msg.msgID == 1:  # CFG-MSG
                        getattr(self.__app, wdgs[wdg]["frm"]).update_pending(msg)

    def _process_MONVER(self, msg: UBXMessage):
        """
        Process MON-VER sentences.

        :param UBXMessage msg: UBX MON-VER config message
        """

        exts = []
        fw_version = NA
        rom_version = NA
        gnss_supported = ""
        model = ""
        sw_version = getattr(msg, "swVersion", b"N/A")
        sw_version = sw_version.replace(b"\x00", b"").decode(UTF8)
        sw_version = sw_version.replace("ROM CORE", "ROM")
        sw_version = sw_version.replace("EXT CORE", "Flash")
        hw_version = getattr(msg, "hwVersion", b"N/A")
        hw_version = hw_version.replace(b"\x00", b"").decode(UTF8)

        for i in range(9):
            ext = getattr(msg, f"extension_{i+1:02d}", b"")
            ext = ext.replace(b"\x00", b"").decode(UTF8)
            exts.append(ext)
            if "FWVER=" in exts[i]:
                fw_version = exts[i].replace("FWVER=", "")
            if "PROTVER=" in exts[i]:
                rom_version = exts[i].replace("PROTVER=", "")
            if "PROTVER " in exts[i]:
                rom_version = exts[i].replace("PROTVER ", "")
            if "MOD=" in exts[i]:
                model = exts[i].replace("MOD=", "")
                hw_version = f"{model} {hw_version}"
            for gnss in (
                "GPS",
                "GLO",
                "GAL",
                "BDS",
                "SBAS",
                "IMES",
                "QZSS",
                "NAVIC",
            ):
                if gnss in exts[i]:
                    gnss_supported = gnss_supported + gnss + " "

        verdata = {}
        verdata["swversion"] = sw_version
        verdata["hwversion"] = hw_version
        verdata["fwversion"] = fw_version
        verdata["romversion"] = rom_version
        verdata["gnss"] = gnss_supported
        self.__app.gnss_status.version_data = verdata

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
        self.__app.gnss_status.hae = data.height / 1000  # meters

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
        self.__app.gnss_status.hae = data.height / 1000  # meters
        self.__app.gnss_status.fix = fix2desc("NAV-PVT", data.fixType)
        if data.carrSoln > 0:
            self.__app.gnss_status.fix = fix2desc("NAV-PVT", data.carrSoln + 5)

        if hasattr(data, "difSoln"):  # for pyubx2 <= 1.2.42
            self.__app.gnss_status.diff_corr = data.difSoln
        elif hasattr(data, "diffSoln"):
            self.__app.gnss_status.diff_corr = data.diffSoln
        if data.lastCorrectionAge != 0:
            self.__app.gnss_status.diff_age = corrage2int(data.lastCorrectionAge)

    def _process_NAV_PVAT(self, data: UBXMessage):
        """
        Process NAV-PVAT sentence -  Navigation position velocity attitude time solution.

        :param UBXMessage data: NAV-PVT parsed message
        """

        self.__app.gnss_status.utc = itow2utc(data.iTOW)  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.alt = data.hMSL / 1000  # meters
        self.__app.gnss_status.speed = data.gSpeed / 1000  # m/s
        self.__app.gnss_status.sip = data.numSV
        self.__app.gnss_status.hae = data.height / 1000  # meters
        ims = self.__app.gnss_status.imu_data
        ims["source"] = data.identity
        ims["roll"] = data.vehRoll
        ims["pitch"] = data.vehPitch
        ims["yaw"] = data.vehHeading
        ims["status"] = (
            (data.vehRollValid << 3) + (data.vehPitchValid << 2) + data.vehHeadingValid
        )

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

        show_unused = self.__app.configuration.get("unusedsat_b")
        self.gsv_data = {}
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
            self.gsv_data[f"{gnssId}-{svid}"] = (gnssId, svid, elev, azim, cno)

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

    def _process_NAV_SVIN(self, data: UBXMessage):
        """
        Process NAV-SVIN sentences - Survey In Status.

        :param UBXMessage data: NAV-SVIN parsed message
        """

        if self.__app.frm_settings.frm_socketserver is not None:
            self.__app.frm_settings.frm_socketserver.svin_countdown(
                data.dur, data.valid, data.active
            )

    def _process_NAV_SVINFO(self, data: UBXMessage):
        """
        Process NAV-SVINFO sentences - Space Vehicle Information.

        NB: Since UBX Gen8 this message is deprecated in favour of NAV-SAT

        :param UBXMessage data: NAV-SVINFO parsed message
        """

        show_unused = self.__app.configuration.get("unusedsat_b")
        self.gsv_data = {}
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
            self.gsv_data[f"{gnssId}-{svid}"] = (gnssId, svid, elev, azim, cno)

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

    def _process_NAV_RELPOSNED(self, data: UBXMessage):
        """
        Process NAV-RELPOSNED sentence - Relative position of rover.

        Two version of this message:
        - version 0 has no heading or length attributes, so these
          must be derived from the NED values
        - version 1 has heading and length attributes

        NB: pyubx2 parses relPosHP values as mm, so total relPosN
        in cm = relPosN + (relPosHPN * 1e-1), etc.

        :param UBXMessage data: NAV-RELPOSNED parsed message
        """

        if data.version == 0x00:
            n = data.relPosN
            e = data.relPosE
            d = data.relPosD
            relPosLength, relPosHeading = ned2vector(n, e, d)
            n = data.accN * 1e-2
            e = data.accE * 1e-2
            d = data.accD * 1e-2
            accLength, _ = ned2vector(n, e, d)
            accHeading = accLength * relPosHeading / relPosLength  # ballpark
        else:
            relPosLength, relPosHeading, accLength, accHeading = (
                data.relPosLength,
                data.relPosHeading,
                data.accLength * 1e-2,
                data.accHeading,
            )

        self.__app.gnss_status.rel_pos_heading = relPosHeading
        self.__app.gnss_status.rel_pos_length = relPosLength
        self.__app.gnss_status.acc_heading = accHeading
        self.__app.gnss_status.acc_length = accLength
        self.__app.gnss_status.rel_pos_flags = [
            data.gnssFixOK,
            data.diffSoln,
            data.relPosValid,
            data.carrSoln,
            data.isMoving,
            data.refPosMiss,
            data.refObsMiss,
            data.relPosHeadingValid,
            data.relPosNormalized,
        ]

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

    def _process_RXM_PMP(self, data: UBXMessage):
        """
        Process RXM-PMP sentence - SPARTN L-Band data.

        :param UBXMessage data: RXM-PMP message
        """

        if self.__app.dialog(DLGTSPARTN) is not None:
            self.__app.dialog(DLGTSPARTN).update_pending(data)

    def _process_ESF_ALG(self, data: UBXMessage):
        """
        Process ESF-ALG sentence - External Sensor Fusion IMU Alignment.

        :param UBXMessage data: ESF-ALG message
        """

        ims = self.__app.gnss_status.imu_data
        ims["source"] = data.identity
        ims["roll"] = data.roll
        ims["pitch"] = data.pitch
        ims["yaw"] = data.yaw
        ims["status"] = data.status

    def _process_NAV_ATT(self, data: UBXMessage):
        """
        Process NAV_ATT sentence - Navigation Attitude.

        :param UBXMessage data: NAV_ATT message
        """

        ims = self.__app.gnss_status.imu_data
        ims["source"] = data.identity
        ims["roll"] = data.roll
        ims["pitch"] = data.pitch
        ims["yaw"] = data.heading
        ims["status"] = ""

    def _process_HNR_ATT(self, data: UBXMessage):
        """
        Process HNR_ATT sentence - High Rate Navigation Attitude..

        :param UBXMessage data: HNR_ATT message
        """

        ims = self.__app.gnss_status.imu_data
        ims["source"] = data.identity
        ims["roll"] = data.roll
        ims["pitch"] = data.pitch
        ims["yaw"] = data.heading
        ims["status"] = ""

"""
UBX Protocol handler

Uses pyubx2 library for parsing

Created on 30 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from pyubx2 import UBXMessage, UBX_MSGIDS
from pyubx2.ubxhelpers import msgclass2bytes
from pygpsclient.globals import GLONASS_NMEA
from pygpsclient.helpers import itow2utc, svid2gnssid, fix2desc, corrage2int


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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

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

        try:
            if raw_data is None:
                return

            if parsed_data.identity == "ACK-ACK":
                self._process_ACK_ACK(parsed_data)
            elif parsed_data.identity == "ACK-NAK":
                self._process_ACK_NAK(parsed_data)
            elif parsed_data.identity == "CFG-MSG":
                self._process_CFG_MSG(parsed_data)
            elif parsed_data.identity == "CFG-PRT":
                self._process_CFG_PRT(parsed_data)
            elif parsed_data.identity == "CFG-RATE":
                self._process_CFG_RATE(parsed_data)
            elif parsed_data.identity == "CFG-INF":
                self._process_CFG_INF(parsed_data)
            elif parsed_data.identity == "CFG-VALGET":
                self._process_CFG_VALGET(parsed_data)
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
            elif parsed_data.identity == "MON-VER":
                self._process_MON_VER(parsed_data)
            elif parsed_data.identity == "MON-HW":
                self._process_MON_HW(parsed_data)
            elif parsed_data.identity == "RXM-RTCM":
                self._process_RXM_RTCM(parsed_data)

        except ValueError:
            # self.__app.set_status(ube.UBXMessageError(err), "red")
            pass

    def _process_ACK_ACK(self, data: UBXMessage):
        """
        Process CFG-MSG sentence - UBX message configuration.

        :param UBXMessage data: ACK_ACK parsed message
        """

        (ubxClass, ubxID) = msgclass2bytes(data.clsID, data.msgID)

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(
                "ACK-ACK", msgtype=UBX_MSGIDS[ubxClass + ubxID]
            )

    def _process_ACK_NAK(self, data: UBXMessage):
        """
        Process CFG-MSG sentence - UBX message configuration.

        :param UBXMessage data: ACK_NAK parsed message
        """

        (ubxClass, ubxID) = msgclass2bytes(data.clsID, data.msgID)

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(
                "ACK-NAK", msgtype=UBX_MSGIDS[ubxClass + ubxID]
            )

    def _process_CFG_MSG(self, data: UBXMessage):
        """
        Process CFG-MSG sentence - UBX message configuration.

        :param UBXMessage data: CFG-MSG parsed message
        """

        (ubxClass, ubxID) = msgclass2bytes(data.msgClass, data.msgID)

        ddcrate = data.rateDDC
        uart1rate = data.rateUART1
        uart2rate = data.rateUART2
        usbrate = data.rateUSB
        spirate = data.rateSPI

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(
                "CFG-MSG",
                msgtype=UBX_MSGIDS[ubxClass + ubxID],
                ddcrate=ddcrate,
                uart1rate=uart1rate,
                uart2rate=uart2rate,
                usbrate=usbrate,
                spirate=spirate,
            )

    def _process_CFG_INF(self, data: UBXMessage):  # pylint: disable=unused-argument
        """
        Process CFG-INF sentence - UBX info message configuration.

        :param UBXMessage data: CFG-INF parsed message
        """

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending("CFG-INF")

    def _process_CFG_PRT(self, data: UBXMessage):
        """
        Process CFG-PRT sentence - UBX port configuration.

        :param UBXMessage data: CFG-PRT parsed message
        """

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(
                "CFG-PRT",
                portid=data.portID,
                bpsrate=data.baudRate,
                inprot=(data.inUBX, data.inNMEA, data.inRTCM, data.inRTCM3),
                outprot=(data.outUBX, data.outNMEA, data.outRTCM3),
            )

    def _process_CFG_RATE(self, data: UBXMessage):
        """
        Process CFG-RATE sentence - UBX solution rate configuration.

        :param UBXMessage data: CFG-RATE parsed message
        """

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(
                "CFG-RATE",
                measrate=data.measRate,
                navrate=data.navRate,
                timeref=data.timeRef,
            )

    def _process_CFG_VALGET(self, data: UBXMessage):  # pylint: disable=unused-argument
        """
        Process CFG-VALGET sentence.

        :param UBXMessage data: CFG-VALGET parsed message
        """

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(
                "CFG-VALGET",
                data=data,
            )

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
            if cno == 0 and not self.__app.frm_settings.show_unused:  # omit unused sats
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

    def _process_NAV_SVINFO(self, data: UBXMessage):
        """
        Process NAV-SVINFO sentences - Space Vehicle Information.

        NB: Since UBX Gen8 this message is deprecated in favour of NAV-SAT

        :param UBXMessage data: NAV-SVINFO parsed message
        """

        self.gsv_data = []
        num_siv = int(data.numCh)

        for i in range(num_siv):
            idx = f"_{i+1:02d}"
            svid = getattr(data, "svid" + idx)
            gnssId = svid2gnssid(svid)  # derive gnssId from svid
            elev = getattr(data, "elev" + idx)
            azim = getattr(data, "azim" + idx)
            cno = getattr(data, "cno" + idx)
            if cno == 0 and not self.__app.frm_settings.show_unused:  # omit unused sats
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
        self.__app.gnss_status.diff_corr = data.diffSoln  # TODO check reliability

    def _process_MON_VER(self, data: UBXMessage):
        """
        Process MON-VER sentence - Receiver Software / Hardware version information.

        :param UBXMessage data: MON-VER parsed message
        """

        exts = []
        fw_version = "n/a"
        protocol = "n/a"
        gnss_supported = ""

        sw_version = (
            getattr(data, "swVersion", "n/a").replace(b"\x00", b"").decode("utf-8")
        )
        sw_version = sw_version.replace("ROM CORE", "ROM")
        sw_version = sw_version.replace("EXT CORE", "Flash")
        hw_version = (
            getattr(data, "hwVersion", "n/a").replace(b"\x00", b"").decode("utf-8")
        )

        for i in range(9):
            idx = f"_{i+1:02d}"
            exts.append(
                getattr(data, "extension" + idx, b"")
                .replace(b"\x00", b"")
                .decode("utf-8")
            )
            if "FWVER=" in exts[i]:
                fw_version = exts[i].replace("FWVER=", "")
            if "PROTVER=" in exts[i]:
                protocol = exts[i].replace("PROTVER=", "")
            if "PROTVER " in exts[i]:
                protocol = exts[i].replace("PROTVER ", "")
            for gnss in ("GPS", "GLO", "GAL", "BDS", "SBAS", "IMES", "QZSS"):
                if gnss in exts[i]:
                    gnss_supported = gnss_supported + gnss + " "

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(
                "MON-VER",
                swversion=sw_version,
                hwversion=hw_version,
                fwversion=fw_version,
                protocol=protocol,
                gnsssupported=gnss_supported,
            )

    def _process_MON_HW(self, data: UBXMessage):
        """
        Process MON-HW sentence - Receiver Hardware status.

        :param UBXMessage data: MON-HW parsed message
        """

        ant_status = getattr(data, "aStatus", 1)
        ant_power = getattr(data, "aPower", 2)

        # update the UBX config panel
        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(
                "MON-HW", antstatus=ant_status, antpower=ant_power
            )

    def _process_RXM_RTCM(self, data: UBXMessage):
        """
        Process RXM-RTCM sentences - Status Information.

        :param UBXMessage data: RXM-RTCM parsed message
        """

        self.__app.gnss_status.diff_corr = data.msgUsed >= 1
        self.__app.gnss_status.diff_station = data.refStation

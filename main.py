from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import time
from threading import Thread, Lock

from Register import Value, Register, U32, U64, STR32, S32, S16, U16


class Modbus:
    def __init__(self, ip, port, unit):
        self.thread = Thread(target=self._polling_thread)
        self.register_lock = Lock()
        self.registers: [Register] = []
        self.unit = unit
        self.client = ModbusTcpClient(ip, port=port, timeout=10)
        self.polling_groups = []

    def __del__(self):
        self.client.close()

    def connect(self):
        self.client.connect()

    def poll_register(self, register: Register):
        self.registers.append(register)

    def start(self):
        self._group_register()
        self._poll()
        # self.thread.daemon = True
        # self.thread.start()

    def _poll(self):
        for group in self.polling_groups:
            start_id = group[0].id
            length = self._length_of_group(group)
            first_register = group[0]
            print(f"Poll {start_id} {length} start with {first_register}")

            response = self.client.read_holding_registers(start_id, length, unit=self.unit)

            if response:
                for index in range(len(group)):
                    register = group[index]
                    start_index = sum(register.length for register in group[0:index])
                    chunk = response.registers[start_index:start_index + register.length]
                    register.set_registers(chunk)
                    value = register.get_value()

                    if register.is_null():
                        value = "NAN"

                    print(f"{register} => {value}")
            # for register_id, register in self.registers:
            #
            # for register_id, register in self.registers:
            #     print(register.name, register.values)

    def _length_of_group(self, group):
        return sum(reg.length for reg in group)

    def _polling_thread(self):
        while True:
            with self.register_lock:
                self._poll()
                time.sleep(5)

    def _group_register(self):
        def by_id(register: Register):
            return register.id

        if len(self.registers) == 0:
            return

        self.registers.sort(key=by_id)

        current_group = []
        polling_groups = []

        next_id = self.registers[0].id
        for register in self.registers:
            if next_id != register.id:
                polling_groups.append(current_group)
                current_group = []

            current_group.append(register)
            next_id = register.id + register.length

        self.polling_groups = polling_groups

        print(f"{len(self.polling_groups)} groups")


# find regex -> (\d{5})	\d	(\w*\d*)	([\w\.]*)	(.*)
# replace wr.poll_register($2($1, "$3", "$4"))

wr = Modbus('192.168.178.46', 502, 3)
wr.connect()

# wr.poll_register(U32(30051, "Nameplate.MainModel", "Geräteklasse"))
# wr.poll_register(U32(30053, "Nameplate.Model", "Gerätetyp"))
# wr.poll_register(U32(30055, "Nameplate.Vendor", "Hersteller"))
# wr.poll_register(U32(30057, "Nameplate.SerNum", "Seriennummer"))
# wr.poll_register(U32(30059, "Nameplate.PkgRev", "Softwarepaket"))
wr.poll_register(U32(30199, "Operation.RmgTms", "Wartezeit bis Einspeisung"))
wr.poll_register(U32(30201, "Operation.Health", "Zustand"))
wr.poll_register(U32(30203, "Operation.HealthStt.Ok", "Nennleistung im Zustand Ok"))
wr.poll_register(U32(30205, "Operation.HealthStt.Wrn", "Nennleistung im Zustand Warnung"))
wr.poll_register(U32(30207, "Operation.HealthStt.Alm", "Nennleistung im Zustand Fehler"))

wr.poll_register(U32(30211, "Operation.Evt.Prio", "Empfohlene Aktion"))
wr.poll_register(U32(30213, "Operation.Evt.Msg", "Meldung"))
wr.poll_register(U32(30215, "Operation.Evt.Dsc", "Fehlerbehebungsmaßnahme"))
wr.poll_register(U32(30217, "Operation.GriSwStt", "Netzrelais/-schütz"))
wr.poll_register(U32(30219, "Operation.DrtStt", "Leistungsreduzierung"))

# wr.poll_register(U32(30225, "Isolation.LeakRis", "Isolationswiderstand"))

# wr.poll_register(U32(30231, "Inverter.WLim", "Maximale Gerätewirkleistung"))
# wr.poll_register(U32(30233, "Inverter.WMax", "Eingestellte Wirkleistungsgrenze"))

wr.poll_register(U32(30247, "Operation.Evt.EvtNo", "Aktuelle Ereignisnummer für Hersteller"))
wr.poll_register(U64(30513, "Metering.TotWhOut", "Gesamtertrag"))

wr.poll_register(U64(30521, "Metering.TotOpTms", "Betriebszeit"))
wr.poll_register(U64(30525, "Metering.TotFeedTms", "Einspeisezeit"))
wr.poll_register(U32(30529, "Metering.TotWhOut", "Gesamtertrag Wh"))
wr.poll_register(U32(30531, "Metering.TotWhOut", "Gesamtertrag kWh"))
wr.poll_register(U32(30533, "Metering.TotWhOut", "Gesamtertrag MWh"))

wr.poll_register(U32(30541, "Metering.TotOpTms", "Betriebszeit"))
wr.poll_register(U32(30543, "Metering.TotFeedTms", "Einspeisezeit"))

wr.poll_register(U32(30559, "Operation.EvtCntUsr", "Anzahl Ereignisse für Benutzer"))
wr.poll_register(U32(30561, "Operation.EvtCntIstl", "Anzahl Ereignisse für Installateur"))
wr.poll_register(U32(30563, "Operation.EvtCntSvc", "Anzahl Ereignisse für Service"))

# wr.poll_register(U32(30581, "Metering.GridMs.TotWhIn", "Zählerstand Bezugszähler"))
# wr.poll_register(U32(30583, "Metering.GridMs.TotWhOut", "Zählerstand Einspeisezähler"))

wr.poll_register(U32(30599, "Operation.GriSwCnt", "Anzahl Netzzuschaltungen"))

wr.poll_register(S32(30769, "DcMs.Amp", "DC Strom Eingang"))
wr.poll_register(S32(30771, "DcMs.Vol", "DC Spannung Eingang"))
wr.poll_register(S32(30773, "DcMs.Watt", "DC Leistung Eingang"))
wr.poll_register(S32(30775, "GridMs.TotW", "Leistung"))
wr.poll_register(S32(30777, "GridMs.W.phsA", "Leistung L1"))
wr.poll_register(S32(30779, "GridMs.W.phsB", "Leistung L2"))
wr.poll_register(S32(30781, "GridMs.W.phsC", "Leistung L3"))
wr.poll_register(U32(30783, "GridMs.PhV.phsA", "Netzspannung Phase L1"))
wr.poll_register(U32(30785, "GridMs.PhV.phsB", "Netzspannung Phase L2"))
wr.poll_register(U32(30787, "GridMs.PhV.phsC", "Netzspannung Phase L3"))
wr.poll_register(U32(30789, "GridMs.PhV.phsA2B", "Netzspannung Phase L1 gegen L2"))
wr.poll_register(U32(30791, "GridMs.PhV.phsB2C", "Netzspannung Phase L2 gegen L3"))
wr.poll_register(U32(30793, "GridMs.PhV.phsC2A", "Netzspannung Phase L3 gegen L1"))
wr.poll_register(U32(30795, "GridMs.TotA", "Netzstrom"))

wr.poll_register(U32(30803, "GridMs.Hz", "Netzfrequenz"))
# wr.poll_register(S32(30805, "GridMs.TotVAr", "Blindleistung"))
# wr.poll_register(S32(30807, "GridMs.VAr.phsA", "Blindleistung L1"))
# wr.poll_register(S32(30809, "GridMs.VAr.phsB", "Blindleistung L2"))
# wr.poll_register(S32(30811, "GridMs.VAr.phsC", "Blindleistung L3"))
# wr.poll_register(S32(30813, "GridMs.TotVA", "Scheinleistung"))
# wr.poll_register(S32(30815, "GridMs.VA.phsA", "Scheinleistung L1"))
# wr.poll_register(S32(30817, "GridMs.VA.phsB", "Scheinleistung L2"))
# wr.poll_register(S32(30819, "GridMs.VA.phsC", "Scheinleistung L3"))

# wr.poll_register(U32(30825, "Inverter.VArModCfg.VArMod", "Betriebsart der statischen Spannungshaltung, Konfiguration der statischen Spannungshaltung"))

# wr.poll_register(S32(30829, "Inverter.VArModCfg.VArCnstCfg.VArNom", "Blindleistungssollwert in %"))
# wr.poll_register(S32(30831, "Inverter.VArModCfg.PFCnstCfg.PF", "Sollwert des cos Phi, Konfiguration des cos Phi, direkte Vorgabe"))
# wr.poll_register(U32(30833, "Inverter.VArModCfg.PFCnstCfg.PFExt", "Erregungsart des cos Phi, Konfiguration des cos Phi, direkte Vorgabe"))
# wr.poll_register(U32(30835, "Inverter.WModCfg.WMod", "Betriebsart des Einspeisemanagements"))
# wr.poll_register(U32(30837, "Inverter.WModCfg.WCnstCfg.W", "Wirkleistungsbegrenzung in W"))
# wr.poll_register(U32(30839, "Inverter.WModCfg.WCnstCfg.WNom", "Wirkleistungsbegrenzung in %"))

wr.poll_register(S32(30865, "Metering.GridMs.TotWIn", "Leistung Bezug"))
wr.poll_register(S32(30867, "Metering.GridMs.TotWOut", "Leistung Einspeisung"))

# wr.poll_register(U32(30875, "MltFncSw.Stt", "Status des Multifunktionsrelais"))
#
# wr.poll_register(U32(30881, "Operation.PvGriConn", "Netzanbindung der Anlage"))

# wr.poll_register(U32(30925, "Spdwr.ComSocA.ConnSpd", "Verbindungsgeschwindigkeit von SMACOM A"))
# wr.poll_register(U32(30927, "Spdwr.ComSocA.DpxMode", "Duplexmodus von SMACOM A"))
# wr.poll_register(U32(30929, "Spdwr.ComSocA.Stt", "Speedwire-Verbindungsstatus von SMACOM A"))
# wr.poll_register(U32(30931, "Spdwr.ComSocB.ConnSpd", "Verbindungsgeschwindigkeit von SMACOM B"))
# wr.poll_register(U32(30933, "Spdwr.ComSocB.DpxMode", "Duplexmodus von SMACOM B"))
# wr.poll_register(U32(30935, "Spdwr.ComSocB.Stt", "Speedwire-Verbindungsstatus von SMACOM B"))

# wr.poll_register(U32(30949, "GridMs.TotPFPrc", "Verschiebungsfaktor"))

# wr.poll_register(S32(30953, "Coolsys.Cab.TmpVal", "Innentemperatur"))

wr.poll_register(S32(30957, "DcMs.Amp", "DC Strom Eingang"))
wr.poll_register(S32(30959, "DcMs.Vol", "DC Spannung Eingang"))
wr.poll_register(S32(30961, "DcMs.Watt", "DC Leistung Eingang"))

wr.poll_register(S32(30975, "Inverter.DclVol", "Zwischenkreisspannung"))
wr.poll_register(S32(30977, "GridMs.A.phsA", "Netzstrom Phase L1"))
wr.poll_register(S32(30979, "GridMs.A.phsB", "Netzstrom Phase L2"))
wr.poll_register(S32(30981, "GridMs.A.phsC", "Netzstrom Phase L3"))

# wr.poll_register(STR32(31017, "Spdwr.ActlIp", "-"))
# wr.poll_register(STR32(31025, "Spdwr.ActlSnetMsk", "-"))
# wr.poll_register(STR32(31033, "Spdwr.ActlGwIp", "-"))
# wr.poll_register(STR32(31041, "Spdwr.ActlDnsSrvIp", "-"))
#
# wr.poll_register(U32(31061, "Bat.ChaCtlComAval", "Steuerung der Batterieladung über Kommunikation verfügbar"))
#
# wr.poll_register(U32(31085, "Operation.HealthStt.Ok", "Nennleistung im Zustand Ok"))
#
# wr.poll_register(S32(31159, "Operation.Dmd.VArCtl", "Aktuelle Vorgabe Blindleistung Q"))
#
# wr.poll_register(S32(31221, "GridMs.TotPFEEI", "EEI-Verschiebungsfaktor"))
#
# wr.poll_register(S32(31247, "Isolation.FltA", "Fehlerstrom"))

# wr.poll_register(U32(31253, "Metering.GridMs.PhV.phsA", "Netzspannung Phase L1"))
# wr.poll_register(U32(31255, "Metering.GridMs.PhV.phsB", "Netzspannung Phase L2"))
# wr.poll_register(U32(31257, "Metering.GridMs.PhV.phsC", "Netzspannung Phase L3"))
# wr.poll_register(U32(31259, "Metering.GridMs.W.phsA", "Leistung Netzeinspeisung L1"))
# wr.poll_register(U32(31261, "Metering.GridMs.W.phsB", "Leistung Netzeinspeisung L2"))
# wr.poll_register(U32(31263, "Metering.GridMs.W.phsC", "Leistung Netzeinspeisung L3"))
# wr.poll_register(U32(31265, "Metering.GridMs.WIn.phsA", "Leistung Netzbezug Phase L1"))
# wr.poll_register(U32(31267, "Metering.GridMs.WIn.phsB", "Leistung Netzbezug Phase L2"))
# wr.poll_register(U32(31269, "Metering.GridMs.WIn.phsC", "Leistung Netzbezug Phase L3"))
# wr.poll_register(S32(31271, "Metering.GridMs.VAr.phsA", "Blindleistung Netzeinspeisung Phase L1"))
# wr.poll_register(S32(31273, "Metering.GridMs.VAr.phsB", "Blindleistung Netzeinspeisung Phase L2"))
# wr.poll_register(S32(31275, "Metering.GridMs.VAr.phsC", "Blindleistung Netzeinspeisung Phase L3"))
# wr.poll_register(S32(31277, "Metering.GridMs.TotVAr", "Blindleistung Netzeinspeisung"))

# wr.poll_register(U32(31405, "Operation.Dmd.WCtl", "Aktuelle Vorgabe Wirkleistungsbegrenzung P"))
# wr.poll_register(U32(31407, "Operation.Dmd.PFCtl", "Aktuelle Vorgabe cos Phi"))
# wr.poll_register(U32(31409, "Operation.Dmd.PFExtCtl", "Aktuelle Vorgabe Erregungsart cos Phi"))
# wr.poll_register(S32(31411, "Operation.Dmd.VArCtl", "Aktuelle Vorgabe Blindleistung Q"))

# wr.poll_register(S32(31793, "DcMs.Amp", "DC Strom Eingang"))
# wr.poll_register(S32(31795, "DcMs.Amp", "DC Strom Eingang"))

# wr.poll_register(S32(34113, "Coolsys.Cab.TmpVal", "Innentemperatur"))

# wr.poll_register(S32(34609, "Env.TmpVal", "Außentemperatur"))
# wr.poll_register(S32(34611, "Env.TmpValMax", "Höchste gemessene Außentemperatur"))

# wr.poll_register(U32(34615, "Env.HorWSpd", "Windgeschwindigkeit"))

# wr.poll_register(S32(34621, "Mdul.TmpVal", "Modultemperatur"))
# wr.poll_register(U32(34623, "Env.ExInsol", "Einstrahlung auf externen Sensor"))
# wr.poll_register(S32(34625, "Env.TmpVal", "Außentemperatur"))
# wr.poll_register(S32(34627, "Env.TmpVal", "Außentemperatur"))
# wr.poll_register(S32(34629, "Mdul.TmpVal", "Modultemperatur"))
# wr.poll_register(S32(34631, "Mdul.TmpVal", "Modultemperatur"))
# wr.poll_register(U32(34633, "Env.HorWSpd", "Windgeschwindigkeit"))
# wr.poll_register(U32(34635, "Env.HorWSpd", "Windgeschwindigkeit"))

# wr.poll_register(U32(34669, "Bat.ChaCtlComAval", "Steuerung der Batterieladung über Kommunikation verfügbar"))

wr.poll_register(U64(35377, "Operation.EvtCntUsr", "Anzahl Ereignisse für Benutzer"))
wr.poll_register(U64(35381, "Operation.EvtCntIstl", "Anzahl Ereignisse für Installateur"))
wr.poll_register(U64(35385, "Operation.EvtCntSvc", "Anzahl Ereignisse für Service"))

# wr.poll_register(U32(40003, "DtTm.TmZn", "Zeitzone"))
# wr.poll_register(U32(40005, "DtTm.DlSvIsOn", "Automatische Sommer-/Winterzeitumstellung eingeschaltet"))

wr.poll_register(U32(40009, "Operation.OpMod", "Betriebszustand"))

# wr.poll_register(U32(40013, "CntrySettings.Lang", "Sprache der Oberfläche"))
# wr.poll_register(S16(40015, "Inverter.VArModCfg.VArCtlComCfg.VArNom", "Normierte Blindleistungsvorgabe durch Anlagensteuerung"))
# wr.poll_register(S16(40016, "Inverter.WModCfg.WCtlComCfg.WNom", "Normierte Wirkleistungsbegrenzung durch Anlagensteuerung"))
#
# wr.poll_register(U32(40018, "Inverter.FstStop", "Schnellabschaltung"))
#
# wr.poll_register(S16(40022, "Inverter.VArModCfg.VArCtlComCfg.VArNomPrc", "Normierte Blindleistungsbegrenzung durch Anlagensteuerung"))
# wr.poll_register(S16(40023, "Inverter.WModCfg.WCtlComCfg.WNomPrc", "Normierte Wirkleistungsbegrenzung durch Anlagensteuerung"))
# wr.poll_register(U16(40024, "Inverter.VArModCfg.PFCtlComCfg.PF", "Verschiebungsfaktor durch Anlagensteuerung"))
# wr.poll_register(U32(40025, "Inverter.VArModCfg.PFCtlComCfg.PFExt", "Erregungsart durch Anlagensteuerung"))
#
# wr.poll_register(U32(40029, "Operation.OpStt", "Betriebsstatus"))
#
# wr.poll_register(U32(40063, "Nameplate.CmpMain.SwRev", "Firmware-Version des Hauptprozessors"))
#
# wr.poll_register(U32(40067, "Nameplate.SerNum", "Seriennummer"))
#
# wr.poll_register(U32(40077, "Sys.DevRstr", "Geräteneustart auslösen"))
#
# wr.poll_register(U32(40095, "GridGuard.Cntry.VolCtl.Max", "Spannungsüberwachung obere Maximalschwelle"))
#
# wr.poll_register(U32(40109, "GridGuard.Cntry", "Eingestellte Ländernorm"))
#
# wr.poll_register(U32(40133, "GridGuard.Cntry.VRtg", "Netz-Nennspannung"))
# wr.poll_register(U32(40135, "GridGuard.Cntry.HzRtg", "Nennfrequenz"))
#
# wr.poll_register(S32(40149, "Inverter.WModCfg.WCtlComCfg.WSpt", "Wirkleistungsvorgabe"))
# wr.poll_register(U32(40151, "Inverter.WModCfg.WCtlComCfg.WCtlComAct", "Wirk- und Blindleistungsregelung über Kommunikation"))
#
# wr.poll_register(U32(40157, "Spdwr.AutoCfgIsOn", "Automatische Speedwire-Konfiguration eingeschaltet"))
# wr.poll_register(STR32(40159, "Spdwr.Ip", "-"))
# wr.poll_register(STR32(40167, "Spdwr.SnetMsk", "-"))
# wr.poll_register(STR32(40175, "Spdwr.GwIp", "-"))
#
# wr.poll_register(U32(40185, "Inverter.VALim", "Maximale Gerätescheinleistung"))
#
# wr.poll_register(U32(40195, "Inverter.VAMax", "Eingestellte Scheinleistungsgrenze"))
#
# wr.poll_register(U32(40200, "Inverter.VArModCfg.VArMod", "Betriebsart der statischen Spannungshaltung, Konfiguration der statischen Spannungshaltung"))
#
# wr.poll_register(S32(40204, "Inverter.VArModCfg.VArCnstCfg.VArNom", "Blindleistungssollwert in %"))
# wr.poll_register(S32(40206, "Inverter.VArModCfg.PFCnstCfg.PF", "Sollwert des cos Phi, Konfiguration des cos Phi, direkte Vorgabe"))
# wr.poll_register(U32(40208, "Inverter.VArModCfg.PFCnstCfg.PFExt", "Erregungsart des cos Phi, Konfiguration des cos Phi, direkte Vorgabe"))
# wr.poll_register(U32(40210, "Inverter.WModCfg.WMod", "Betriebsart des Einspeisemanagements"))
# wr.poll_register(U32(40212, "Inverter.WModCfg.WCnstCfg.W", "Wirkleistungsbegrenzung in W"))
# wr.poll_register(U32(40214, "Inverter.WModCfg.WCnstCfg.WNom", "Wirkleistungsbegrenzung in %"))
# wr.poll_register(U32(40216, "Inverter.WCtlHzModCfg.WCtlHzMod", "Betriebsart der Wirkleistungsreduktion bei Überfrequenz P(f)"))
# wr.poll_register(U32(40218, "Inverter.WCtlHzModCfg.WCtlHzCfg.HzStr", "Abstand der Startfrequenz zur Netzfrequenz, Konfiguration des linearen Gradienten der Momentanleistung"))
# wr.poll_register(U32(40220, "Inverter.WCtlHzModCfg.WCtlHzCfg.HzStop", "Abstand der Rücksetzfrequenz zur Netzfrequenz, Konfiguration des linearen Gradienten der Momentanleistung"))
# wr.poll_register(U32(40222, "Inverter.VArModCfg.PFCtlWCfg.PFStr", "cos Phi des Startpunktes, Konfiguration der cos Phi(P)-Kennlinie"))
# wr.poll_register(U32(40224, "Inverter.VArModCfg.PFCtlWCfg.PFExtStr", "Erregungsart des Startpunktes, Konfiguration der cos Phi(P)-Kennlinie"))
# wr.poll_register(U32(40226, "Inverter.VArModCfg.PFCtlWCfg.PFStop", "cos Phi des Endpunktes, Konfiguration der cos Phi(P)-Kennlinie"))
# wr.poll_register(U32(40228, "Inverter.VArModCfg.PFCtlWCfg.PFExtStop", "Erregungsart des Endpunktes, Konfiguration der cos Phi(P)-Kennlinie"))
# wr.poll_register(U32(40230, "Inverter.VArModCfg.PFCtlWCfg.WNomStr", "Wirkleistung des Startpunktes, Konfiguration der cos Phi(P)-Kennlinie"))
# wr.poll_register(U32(40232, "Inverter.VArModCfg.PFCtlWCfg.WNomStop", "Wirkleistung des Endpunktes, Konfiguration der cos Phi(P)-Kennlinie"))
# wr.poll_register(U32(40234, "Inverter.WGra", "Wirkleistungsgradient"))
#
# wr.poll_register(U32(40238, "Inverter.WCtlHzModCfg.WCtlHzCfg.WGra", "Wirkleistungsgradient, Konfiguration des linearen Gradienten der Momentanleistung"))
# wr.poll_register(U32(40240, "Inverter.WCtlHzModCfg.WCtlHzCfg.HystEna", "Aktivierung der Schleppzeigerfunktion, Konfiguration des linearen Gradienten der Momentanleistung"))
# wr.poll_register(U32(40242, "Inverter.WCtlHzModCfg.WCtlHzCfg.HzStopWGra", "Wirkleistungsgradient nach Rücksetzfrequenz, Konfiguration des linearen Gradienten der Momentanleistung"))
# wr.poll_register(U32(40244, "Inverter.DGSModCfg.DGSFlCfg.ArGraMod", "Blindstromstatik, Konfiguration der vollständigen dynamischen Netzstützung"))
# wr.poll_register(U32(40246, "Inverter.DGSModCfg.DGSFlCfg.ArGraSag", "Gradient K der Blindstromstatik für Unterpannung bei dynamischer Netzstützung"))
# wr.poll_register(U32(40248, "Inverter.DGSModCfg.DGSFlCfg.ArGraSwell", "Gradient K der Blindstromstatik für Überpannung bei dynamischer Netzstützung"))
# wr.poll_register(U32(40250, "Inverter.DGSModCfg.DGSMod", "Betriebsart der dynamischen Netzstützung, Konfiguration der dynamischen Netzstützung"))
# wr.poll_register(S32(40252, "Inverter.DGSModCfg.DGSFlCfg.DbVolNomMin", "Untergrenze Spannungstotband, Konfiguration der vollständigen dynamischen Netzstützung"))
# wr.poll_register(U32(40254, "Inverter.DGSModCfg.DGSFlCfg.DbVolNomMax", "Obergrenze Spannungstotband, Konfiguration der vollständigen dynamischen Netzstützung"))
# wr.poll_register(U32(40256, "Inverter.DGSModCfg.PwrCirInopVolNom", "PWM-Sperrspannung, Konfiguration der dynamischen Netzstützung"))
# wr.poll_register(U32(40258, "Inverter.DGSModCfg.PwrCirInopTms", "PWM-Sperrverzögerung, Konfiguration der dynamischen Netzstützung"))
#
# wr.poll_register(U32(40262, "Inverter.UtilCrvCfg.Crv0.NumPt", "Kennlinie, Anzahl der zu verwendenden Punkte der Kennlinie"))
# wr.poll_register(U32(40264, "Inverter.UtilCrvCfg.Crv0.NumPt", "Kennlinie, Anzahl der zu verwendenden Punkte der Kennlinie"))
# wr.poll_register(U32(40266, "Inverter.UtilCrvCfg.Crv0.NumPt", "Kennlinie, Anzahl der zu verwendenden Punkte der Kennlinie"))
#
# wr.poll_register(S32(40282, "Inverter.UtilCrvCfg.CrvPt1.XVal", "X-Werte der Kennlinie 1"))
# wr.poll_register(S32(40284, "Inverter.UtilCrvCfg.CrvPt1.XVal", "X-Werte der Kennlinie 1"))
# wr.poll_register(S32(40286, "Inverter.UtilCrvCfg.CrvPt1.XVal", "X-Werte der Kennlinie 1"))
# wr.poll_register(S32(40288, "Inverter.UtilCrvCfg.CrvPt1.XVal", "X-Werte der Kennlinie 1"))
# wr.poll_register(S32(40290, "Inverter.UtilCrvCfg.CrvPt1.XVal", "X-Werte der Kennlinie 1"))
# wr.poll_register(S32(40292, "Inverter.UtilCrvCfg.CrvPt1.XVal", "X-Werte der Kennlinie 1"))
# wr.poll_register(S32(40294, "Inverter.UtilCrvCfg.CrvPt1.XVal", "X-Werte der Kennlinie 1"))
# wr.poll_register(S32(40296, "Inverter.UtilCrvCfg.CrvPt1.XVal", "X-Werte der Kennlinie 1"))
#
# wr.poll_register(S32(40306, "Inverter.UtilCrvCfg.CrvPt1.YVal", "Y-Werte der Kennlinie 1"))
# wr.poll_register(S32(40308, "Inverter.UtilCrvCfg.CrvPt1.YVal", "Y-Werte der Kennlinie 1"))
# wr.poll_register(S32(40310, "Inverter.UtilCrvCfg.CrvPt1.YVal", "Y-Werte der Kennlinie 1"))
# wr.poll_register(S32(40312, "Inverter.UtilCrvCfg.CrvPt1.YVal", "Y-Werte der Kennlinie 1"))
# wr.poll_register(S32(40314, "Inverter.UtilCrvCfg.CrvPt1.YVal", "Y-Werte der Kennlinie 1"))
# wr.poll_register(S32(40316, "Inverter.UtilCrvCfg.CrvPt1.YVal", "Y-Werte der Kennlinie 1"))
# wr.poll_register(S32(40318, "Inverter.UtilCrvCfg.CrvPt1.YVal", "Y-Werte der Kennlinie 1"))
# wr.poll_register(S32(40320, "Inverter.UtilCrvCfg.CrvPt1.YVal", "Y-Werte der Kennlinie 1"))
#
# wr.poll_register(S32(40330, "Inverter.UtilCrvCfg.CrvPt2.XVal", "X-Werte der Kennlinie 2"))
# wr.poll_register(S32(40332, "Inverter.UtilCrvCfg.CrvPt2.XVal", "X-Werte der Kennlinie 2"))
# wr.poll_register(S32(40334, "Inverter.UtilCrvCfg.CrvPt2.XVal", "X-Werte der Kennlinie 2"))
# wr.poll_register(S32(40336, "Inverter.UtilCrvCfg.CrvPt2.XVal", "X-Werte der Kennlinie 2"))
# wr.poll_register(S32(40338, "Inverter.UtilCrvCfg.CrvPt2.XVal", "X-Werte der Kennlinie 2"))
# wr.poll_register(S32(40340, "Inverter.UtilCrvCfg.CrvPt2.XVal", "X-Werte der Kennlinie 2"))
# wr.poll_register(S32(40342, "Inverter.UtilCrvCfg.CrvPt2.XVal", "X-Werte der Kennlinie 2"))
# wr.poll_register(S32(40344, "Inverter.UtilCrvCfg.CrvPt2.XVal", "X-Werte der Kennlinie 2"))
#
# wr.poll_register(S32(40354, "Inverter.UtilCrvCfg.CrvPt2.YVal", "Y-Werte der Kennlinie 2"))
# wr.poll_register(S32(40356, "Inverter.UtilCrvCfg.CrvPt2.YVal", "Y-Werte der Kennlinie 2"))
# wr.poll_register(S32(40358, "Inverter.UtilCrvCfg.CrvPt2.YVal", "Y-Werte der Kennlinie 2"))
# wr.poll_register(S32(40360, "Inverter.UtilCrvCfg.CrvPt2.YVal", "Y-Werte der Kennlinie 2"))
# wr.poll_register(S32(40362, "Inverter.UtilCrvCfg.CrvPt2.YVal", "Y-Werte der Kennlinie 2"))
# wr.poll_register(S32(40364, "Inverter.UtilCrvCfg.CrvPt2.YVal", "Y-Werte der Kennlinie 2"))
# wr.poll_register(S32(40366, "Inverter.UtilCrvCfg.CrvPt2.YVal", "Y-Werte der Kennlinie 2"))
# wr.poll_register(S32(40368, "Inverter.UtilCrvCfg.CrvPt2.YVal", "Y-Werte der Kennlinie 2"))
#
# wr.poll_register(S32(40378, "Inverter.UtilCrvCfg.CrvPt3.XVal", "X-Werte der Kennlinie 3"))
# wr.poll_register(S32(40380, "Inverter.UtilCrvCfg.CrvPt3.XVal", "X-Werte der Kennlinie 3"))
# wr.poll_register(S32(40382, "Inverter.UtilCrvCfg.CrvPt3.XVal", "X-Werte der Kennlinie 3"))
# wr.poll_register(S32(40384, "Inverter.UtilCrvCfg.CrvPt3.XVal", "X-Werte der Kennlinie 3"))
# wr.poll_register(S32(40386, "Inverter.UtilCrvCfg.CrvPt3.XVal", "X-Werte der Kennlinie 3"))
# wr.poll_register(S32(40388, "Inverter.UtilCrvCfg.CrvPt3.XVal", "X-Werte der Kennlinie 3"))
# wr.poll_register(S32(40390, "Inverter.UtilCrvCfg.CrvPt3.XVal", "X-Werte der Kennlinie 3"))
# wr.poll_register(S32(40392, "Inverter.UtilCrvCfg.CrvPt3.XVal", "X-Werte der Kennlinie 3"))
#
# wr.poll_register(S32(40402, "Inverter.UtilCrvCfg.CrvPt3.YVal", "Y-Werte der Kennlinie 3"))
# wr.poll_register(S32(40404, "Inverter.UtilCrvCfg.CrvPt3.YVal", "Y-Werte der Kennlinie 3"))
# wr.poll_register(S32(40406, "Inverter.UtilCrvCfg.CrvPt3.YVal", "Y-Werte der Kennlinie 3"))
# wr.poll_register(S32(40408, "Inverter.UtilCrvCfg.CrvPt3.YVal", "Y-Werte der Kennlinie 3"))
# wr.poll_register(S32(40410, "Inverter.UtilCrvCfg.CrvPt3.YVal", "Y-Werte der Kennlinie 3"))
# wr.poll_register(S32(40412, "Inverter.UtilCrvCfg.CrvPt3.YVal", "Y-Werte der Kennlinie 3"))
# wr.poll_register(S32(40414, "Inverter.UtilCrvCfg.CrvPt3.YVal", "Y-Werte der Kennlinie 3"))
# wr.poll_register(S32(40416, "Inverter.UtilCrvCfg.CrvPt3.YVal", "Y-Werte der Kennlinie 3"))
#
# wr.poll_register(U32(40428, "GridGuard.Cntry.FrqCtl.hhLim", "Frequenzüberwachung mittlere Maximalschwelle"))
# wr.poll_register(U32(40430, "GridGuard.Cntry.FrqCtl.hhLimTmms", "Frequenzüberwachung mittlere Maximalschwelle Auslösezeit"))
# wr.poll_register(U32(40432, "GridGuard.Cntry.FrqCtl.hLim", "Frequenzüberwachung untere Maximalschwelle"))
# wr.poll_register(U32(40434, "GridGuard.Cntry.FrqCtl.hLimTmms", "Frequenzüberwachung untere Maximalschwelle Auslösezeit"))
# wr.poll_register(U32(40436, "GridGuard.Cntry.FrqCtl.lLim", "Frequenzüberwachung obere Minimalschwelle"))
# wr.poll_register(U32(40438, "GridGuard.Cntry.FrqCtl.lLimTmms", "Frequenzüberwachung obere Minimalschwelle Auslösezeit"))
# wr.poll_register(U32(40440, "GridGuard.Cntry.FrqCtl.llLim", "Frequenzüberwachung mittlere Minimalschwelle"))
# wr.poll_register(U32(40442, "GridGuard.Cntry.FrqCtl.llLimTmms", "Frequenzüberwachung mittlere Minimalschwelle Auslösezeit"))
#
# wr.poll_register(U32(40446, "GridGuard.Cntry.VolCtl.MaxTmms", "Spannungsüberwachung obere Maximalschwelle Auslösezeit"))
# wr.poll_register(U32(40448, "GridGuard.Cntry.VolCtl.hhLim", "Spannungsüberwachung mittlere Maximalschwelle"))
# wr.poll_register(U32(40450, "GridGuard.Cntry.VolCtl.hhLimTmms", "Spannungsüberwachung mittlere Maximalschwelle Auslösezeit"))
# wr.poll_register(U32(40452, "GridGuard.Cntry.VolCtl.hLim", "Spannungsüberwachung untere Maximalschwelle"))
#
# wr.poll_register(U32(40456, "GridGuard.Cntry.VolCtl.hLimTmms", "Spannungsüberwachung untere Maximalschwelle Auslösezeit"))
# wr.poll_register(U32(40458, "GridGuard.Cntry.VolCtl.lLim", "Spannungsüberwachung obere Minimalschwelle"))
#
# wr.poll_register(U32(40462, "GridGuard.Cntry.VolCtl.lLimTmms", "Spannungsüberwachung obere Minimalschwelle Auslösezeit"))
# wr.poll_register(U32(40464, "GridGuard.Cntry.VolCtl.llLim", "Spannungsüberwachung mittlere Minimalschwelle"))
# wr.poll_register(U32(40466, "GridGuard.Cntry.VolCtl.llLimTmms", "Spannungsüberwachung mittlere Minimalschwelle Auslösezeit"))
#
# wr.poll_register(U32(40472, "Inverter.PlntCtl.VRef", "Referenzspannung"))
# wr.poll_register(S32(40474, "Inverter.PlntCtl.VRefOfs", "Referenzkorrekturspannung"))
#
# wr.poll_register(U32(40480, "Nameplate.ARtg", "Nennstrom über alle Phasen"))
# wr.poll_register(U32(40482, "Inverter.VArGra", "Blindleistungsgradient"))
# wr.poll_register(U32(40484, "Inverter.WGraEna", "Aktivierung des Wirkleistungsgradienten"))
#
# wr.poll_register(U32(40490, "Inverter.VArModCfg.VArCtlVolCfg.VArGraNom", "Blindleistungsgradient, Konfiguration der Blindleistungs-/Spannungskennlinie Q(U)"))
#
# wr.poll_register(STR32(40497, "Nameplate.MacId", "-"))
# wr.poll_register(STR32(40513, "Spdwr.DnsSrvIp", "-"))
# wr.poll_register(U32(40575, "MltFncSw.OpMode", "Betriebsart des Multifunktionsrelais"))
# wr.poll_register(U32(40577, "MltFncSw.OpMode", "Betriebsart des Multifunktionsrelais"))
# wr.poll_register(STR32(40631, "Nameplate.Location", "-"))
# wr.poll_register(U32(40647, "Upd.AutoUpdIsOn", "Automatische Updates eingeschaltet"))
# wr.poll_register(U32(40789, "Nameplate.ComRev", "Kommunikationsversion"))
# wr.poll_register(U32(40791, "Inverter.PlntCtl.IntvTmsMax", "Timeout für Kommunikationsfehlermeldung"))
# wr.poll_register(U32(40855, "Inverter.UtilCrvCfg.Crv0.RmpDec", "Kennlinie, Absenkungsrampe für Erreichung des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40857, "Inverter.UtilCrvCfg.Crv0.RmpDec", "Kennlinie, Absenkungsrampe für Erreichung des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40859, "Inverter.UtilCrvCfg.Crv0.RmpDec", "Kennlinie, Absenkungsrampe für Erreichung des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40875, "Inverter.UtilCrvCfg.Crv0.RmpInc", "Kennlinie, Steigerungsrampe für Erreichung des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40877, "Inverter.UtilCrvCfg.Crv0.RmpInc", "Kennlinie, Steigerungsrampe für Erreichung des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40879, "Inverter.UtilCrvCfg.Crv0.RmpInc", "Kennlinie, Steigerungsrampe für Erreichung des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40895, "Inverter.UtilCrvCfg.Crv0.CrvTms", "Kennlinie, Einstellzeit des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40897, "Inverter.UtilCrvCfg.Crv0.CrvTms", "Kennlinie, Einstellzeit des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40899, "Inverter.UtilCrvCfg.Crv0.CrvTms", "Kennlinie, Einstellzeit des Kennlinienarbeitspunktes"))
# wr.poll_register(U32(40915, "Inverter.WMax", "Eingestellte Wirkleistungsgrenze"))
# wr.poll_register(U32(40917, "Inverter.UtilCrvCfg.CrvModCfg.CrvNum", "Kennliniennummer, Konfiguration des Kennlinienmodus"))
# wr.poll_register(U32(40919, "Inverter.UtilCrvCfg.CrvModCfg.CrvNum", "Kennliniennummer, Konfiguration des Kennlinienmodus"))
# wr.poll_register(U32(40921, "Inverter.UtilCrvCfg.CrvModCfg.CrvNum", "Kennliniennummer, Konfiguration des Kennlinienmodus"))
# wr.poll_register(U32(40937, "Inverter.UtilCrvCfg.CrvModCfg.CrvEna", "Aktivierung der Kennlinie, Konfiguration des Kennlinienmodus"))
# wr.poll_register(U32(40939, "Inverter.UtilCrvCfg.CrvModCfg.CrvEna", "Aktivierung der Kennlinie, Konfiguration des Kennlinienmodus"))
# wr.poll_register(U32(40941, "Inverter.UtilCrvCfg.CrvModCfg.CrvEna", "Aktivierung der Kennlinie, Konfiguration des Kennlinienmodus"))
# wr.poll_register(U32(40957, "Inverter.UtilCrvCfg.Crv0.XRef", "Kennlinie X-Achsen Referenz"))
# wr.poll_register(U32(40959, "Inverter.UtilCrvCfg.Crv0.XRef", "Kennlinie X-Achsen Referenz"))
# wr.poll_register(U32(40961, "Inverter.UtilCrvCfg.Crv0.XRef", "Kennlinie X-Achsen Referenz"))
# wr.poll_register(U32(40977, "Inverter.UtilCrvCfg.Crv0.YRef", "Kennlinie Y-Achsen Referenz"))
# wr.poll_register(U32(40979, "Inverter.UtilCrvCfg.Crv0.YRef", "Kennlinie Y-Achsen Referenz"))
# wr.poll_register(U32(40981, "Inverter.UtilCrvCfg.Crv0.YRef", "Kennlinie Y-Achsen Referenz"))
# wr.poll_register(U32(40997, "Inverter.DGSModCfg.HystVolNom", "Hysteresespannung, Konfiguration der dynamischen Netzstützung"))
# wr.poll_register(S32(40999, "Inverter.VArModCfg.PFCtlComCfg.PFEEI", "Sollwert cos(Phi) gemäß EEI-Konvention"))
# wr.poll_register(U32(41121, "GridGuard.CntrySet", "Setze Ländernorm"))
# wr.poll_register(U32(41123, "GridGuard.Cntry.VolCtl.ReconMin", "Min. Spannung zur Wiederzuschaltung"))
# wr.poll_register(U32(41125, "GridGuard.Cntry.VolCtl.ReconMax", "Max. Spannung zur Wiederzuschaltung"))
# wr.poll_register(U32(41127, "GridGuard.Cntry.FrqCtl.ReconMin", "Untere Frequenz für Wiederzuschaltung"))
# wr.poll_register(U32(41129, "GridGuard.Cntry.FrqCtl.ReconMax", "Obere Frequenz für Wiederzuschaltung"))
# wr.poll_register(U32(41131, "DcCfg.StrVol", "minimale Spannung Eingang "))
# wr.poll_register(U32(41133, "DcCfg.StrVol", "minimale Spannung Eingang "))
# wr.poll_register(U32(41155, "DcCfg.StrTms", "Startverzögerung Eingang "))
# wr.poll_register(U32(41157, "DcCfg.StrTms", "Startverzögerung Eingang "))
# wr.poll_register(U32(41169, "GridGuard.Cntry.LeakRisMin", "Minimaler Isolationswiderstand"))
# wr.poll_register(U32(41171, "Metering.TotkWhOutSet", "Setze Gesamtertrag"))
# wr.poll_register(U32(41173, "Metering.TotOpTmhSet", "Setze Gesamte Betriebszeit am Netzanschlusspunkt"))
# wr.poll_register(U32(41187, "Inverter.CtlComCfg.CtlMsSrc", "Quelle der Referenzmessung zur Blind-/Wirkleistungsregelung"))
# wr.poll_register(U32(41193, "Inverter.CtlComCfg.WCtlCom.CtlComMssMod", "Betriebsart für ausbleibende Wirkleistungsbegrenzung"))
# wr.poll_register(U32(41195, "Inverter.CtlComCfg.WCtlCom.TmsOut", "Timeout für ausbleibende Wirkleistungsbegrenzung"))
# wr.poll_register(U32(41197, "Inverter.CtlComCfg.WCtlCom.FlbWNom", "Fallback Wirkleistungsbegrenzung P in % von WMax für ausbleibende Wirkleistungsbegrenzung"))
# wr.poll_register(U32(41199, "PCC.WMaxNom", "Eingestellte Wirkleistungsgrenze am Netzanschlusspunkt"))
# wr.poll_register(U32(41203, "Plnt.DcWRtg", "Anlagen-Nennleistung"))
# wr.poll_register(S32(41215, "Inverter.WModCfg.WCtlComCfg.FlbWSpt", "Fallback Leistung für Betriebsart WCtlCom"))
# wr.poll_register(U32(41217, "PCC.WMax", "Eingestellte Wirkleistungsgrenze am Netzanschlusspunkt"))
# wr.poll_register(U32(41219, "Inverter.CtlComCfg.VArCtlCom.CtlComMssMod", "Betriebsart für ausbleibende Blindleistungsregelung"))
# wr.poll_register(U32(41221, "Inverter.CtlComCfg.VArCtlCom.TmsOut", "Timeout für ausbleibende Blindleistungsregelung"))
# wr.poll_register(S32(41223, "Inverter.CtlComCfg.VArCtlCom.FlbVArNom", "Fallback Blindleistung Q in % von WMax für ausbleibende Blindleistungsregelung"))
# wr.poll_register(U32(41225, "Inverter.CtlComCfg.PFCtlCom.CtlComMssMod", "Betriebsart für ausbleibende cos Phi-Vorgabe"))
# wr.poll_register(U32(41227, "Inverter.CtlComCfg.PFCtlCom.TmsOut", "Timeout für ausbleibende cos Phi-Vorgabe"))
# wr.poll_register(S32(41229, "Inverter.CtlComCfg.PFCtlCom.FlbPF", "Fallback cos Phi für ausbleibende cos Phi-Vorgabe"))
# wr.poll_register(U32(41253, "Inverter.FstStop", "Schnellabschaltung"))
# wr.poll_register(S16(41255, "Inverter.WModCfg.WCtlComCfg.WNomPrc", "Normierte Wirkleistungsbegrenzung durch Anlagensteuerung"))
# wr.poll_register(S16(41256, "Inverter.VArModCfg.VArCtlComCfg.VArNomPrc", "Normierte Blindleistungsbegrenzung durch Anlagensteuerung"))
# wr.poll_register(S32(41257, "Inverter.VArModCfg.PFCtlComCfg.PFEEI", "Sollwert cos(Phi) gemäß EEI-Konvention"))


wr.start()

# while True:
#     time.sleep(10)

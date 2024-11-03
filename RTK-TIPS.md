# Achieving cm Level Accuracy Via Real-time Kinematics (RTK)

[Tips and Recommendations](#tips) |
[Illustrated Example](#example) |
[Glossary of Terms and Abbreviations](#glossary) |
[References and Further Reading](#references) |

A common topic on the PyGPSClient [Discussion Forums](https://github.com/semuconsulting/PyGPSClient/discussions) is how to achieve centimeter-level accuracy using an RTK-compatible receiver like the [u-blox ZED-F9P](https://www.u-blox.com/en/product/zed-f9p-module).

The following is by no means a rigorous treatment, but is intended to offer some practical tips and recommendations. **YOUR MILEAGE MAY VARY!** The focus here is real-time kinematics (**RTK**), but much the same considerations will apply to post-processing kinematics (**PPK**) and other differential GPS (**DGPS**) techniques.

If you're relatively new to GNSS and RTK techniques and terminology, you may want to review this [wiki](https://www.semuconsulting.com/gnsswiki/) first.

---
## <a name="tips">Tips and Recommendations</a>

**NB:** RTK techniques cannot 'correct' a poor GNSS signal - *you need to have a solid 3D fix in the first place to stand any chance of achieving centimeter-level positional accuracy*.

### 1. The importance of Reference Frame

- Navigation or surveying solutions produced by RTK or PPK techniques are only meaningful in relation to a given reference frame or datum. A full discussion of datums is beyond the scope of this article, but in essence a reference frame can be global e.g. [WGS84](https://en.wikipedia.org/wiki/World_Geodetic_System), or local to a particular geographical area e.g. [NAD83 (North America)](https://en.wikipedia.org/wiki/North_American_Datum#North_American_Datum_of_1983) or [ETRS89 (Europe)](https://en.wikipedia.org/wiki/European_Terrestrial_Reference_System_1989). While the differences may be subtle, no two reference frames will yield exactly the same results. All other things being equal, a local reference frame will be more accurate than a global one *within its region of coverage*. Results based on a mix of disparate reference frames are likely to be spurious.
- GNSS has traditionally been based on the [World Geodetic System 1984 or WGS84](https://en.wikipedia.org/wiki/World_Geodetic_System). WGS84 is an ensemble of geocentric reference frames which were originally accurate to within 1 m. Subsequent revisions have brought this down to around 10 cm.
- When dealing with terrestrial positional accuracy at the centimeter or millimeter level, it is necessary to take into account factors like tectonic plate movement and gravitational/magnetic displacements. This is the function of the [International Terrestrial Reference System or ITRS](https://en.wikipedia.org/wiki/International_Terrestrial_Reference_System_and_Frame) and its associated International Terrestrial Reference Frame ITRF. New ITRF solutions are produced every few years, using the latest mathematical and surveying techniques to attempt to realize the ITRS as precisely as possible. The difference between the latest WGS84 and ITRF2000 frames is of the order of a few centimeters.
- Terrestrial datums can be static ("plate-fixed" i.e. fixed relative to a specific tectonic plate) or dynamic ("earth-fixed" i.e. fixed relative to the earth's centre). The “earth-fixed” ITRF is typically not regarded as a “datum” – rather it is the international standard reference framework to which national geocentric datums are aligned.
- In order to achieve meaningful centimeter or millimeter level accuracy, all components in the end-to-end application (including the RTK data source and any maps or geo-referenced imagery) must be using the same ITRF or related "plate-fixed" reference frame.

### 2. Use a dual-band RTK-compatible GNSS receiver

- The receiver must be capable of receiving and processing real-time kinematic 'corrections', typically from an NTRIP or SPARTN source via the RTCM3 or SPARTN2 protocols.
- The receiver should be capable of receiving GNSS transmissions on both the L1 and L2 (or L5) frequencies (*refer to the [wiki](https://www.semuconsulting.com/gnsswiki/#Signal) to understand why this is beneficial to positional accuracy*).
- The receiver and/or its antenna should be reasonably robust (ideally IP67 or better), as the best results are likely to be obtained outdoors.

### 3. Use a suitable L-Band antenna and cable

- A GNSS antenna must be capable of receiving a clear signal on the key GNSS L-Band frequencies - specifically the L1, L2 and (ideally) L5 and/or L6 frequencies. Depending on your local environment and intended application, a multi-band active patch antenna like the u-blox [ANN-MB-00](https://www.sparkfun.com/products/15192) may suffice, or you may benefit from a "UFO" style multi-band [surveying antenna](https://www.sparkfun.com/products/21801). 
- If weight is at a premium - e.g. for aerial applications - a [helical antenna](https://www.sparkfun.com/products/23847) may be more suitable, albeit with some loss of performance.
- Active GNSS antennae typically incorporate low noise amplifiers (LNA) to boost gain, along with bandpass or 'saw' filters to remove extraneous noise and frequencies which are not required for GNSS reception. **Note, however**, that such filters may render the antenna unsuitable for other RTK applications e.g. reception of L-Band SPARTN data from geostationary Inmarsat satellites using a [u-blox NEO-D9S](https://www.sparkfun.com/products/19390) receiver, for which a [broad-spectrum active patch antenna](https://www.amazon.com/RTL-SDR-Blog-1525-1637-Inmarsat-Iridium/dp/B07WGWZS1D), or even a [passive directional antenna](https://www.beamcommunications.com/satellite/35-inmarsat-beam-fixed-directional-antenna-passive#specifications), may be more suitable. Check the antenna specification to ensure it covers the required frequency spectra.
- Ensure that the antenna cable is a high-quality coaxial cable with minimum attenuation in the L-Band spectrum - [RG58](https://www.sparkfun.com/products/21281) as a bare minimum, preferably [RF240](https://www.connextech.co.uk/8m-rf240-low-loss-cable-assembly-1441-p.asp) or [RF400](https://www.connextech.co.uk/10m-rf400-very-low-loss-cable-assembly-1433-p.asp) for longer runs (> 3m).
- If possible, use a GNSS receiver/breakout board and antenna which support robust TNC, BNC or SMA connectors rather than the much smaller U.FL type, which is not designed for repeated insertion and has limited cable length.

### 4. Use a suitable ground plane

- Popular active patch antennae like the u-blox [ANN-MB-00](https://www.sparkfun.com/products/15192) are designed to be used with an external ground plane - typically a (steel) car roof or a [small steel plate](https://www.sparkfun.com/products/17519) suitable for mounting on a tripod. At a push, a heavy ferrous saucepan lid may suffice.
- The science behind ground planes is beyond the scope of this article but, in essence, a good ground plane under the antenna improves signal strength and reduces noise and interference. Refer to [Importance of Ground Planes](https://novotech.com/pages/ground-plane) for a more in-depth discussion.
- Specialised [surveying antennae](https://www.sparkfun.com/products/21801) of the "UFO" type normally have a built-in ground plane.
- Helical antennae do not generally require a ground plane.

### 5. Ensure you have the best possible view of the sky

- Needless to say, you need to have good unrestricted visibility of the sky (ideally 360°) with the broadest possible satellite coverage to obtain the most accurate results. This is indicated by the various Dilution of Precision (DOP) values (`pDOP`, `vDOP`, `hDOP`). Ideally the indicated pDOP should be <= 1.0.
- You should be able to receive signals from *at least* 10 satellites with a signal strength (CN₀) of 45dB or better.

| **Poor Satellite Coverage**  | **Good Satellite Coverage** |
|:----------------------------:|:---------------------------:|
| ![poor sats](https://github.com/semuconsulting/PyGPSClient/blob/master/images/poor_sats.png?raw=true) |![good sats](https://github.com/semuconsulting/PyGPSClient/blob/master/images/good_sats.png?raw=true) |
| | |

### 6. Ensure you are using a reliable, local RTK data source

- In the present context this generally means NTRIP (via the public internet) or SPARTN (via NTRIP, MQTT (IP) or L-Band channels). NTRIP casters traditionally output data in RTCM format, but there are now proprietary services offering SPARTN format instead.
- Ideally, an NTRIP source ('mountpoint') should be no further than 30km from your antenna location, such that its correction data is [representative of local atmospheric conditions](https://www.semuconsulting.com/gnsswiki/#ION).
- **NB:** While free public domain NTRIP resources exist and can often give perfectly satisfactory results, there is no guarantee as to the quality of the correction data available. Some public domain CORS are essentially amateurs working out of their back yards.  The best results *for your location* may be obtained from proprietary or subscription services which use specialised, carefully calibrated equipment in optimal locations with ITRF or local plate-fixed datums - but it's always worth trying public domain resources first.

### 7. Check your receiver is successfully receiving and processing RTK data

- If you're using a UBX receiver like the F9P, you may find it easier to configure it to output UBX messages rather than the default NMEA, as the former are more concise and offer more comprehensive and consistent RTK status information.
- Successful receipt and processing of RTK correction data is generally indicated as follows:
  - The fix status will change to 'RTK', 'RTK-FLOAT' or 'RTK-FIXED'. **NB:** The exact status wording will depend on which NMEA or UBX messages the receiver is configured to output - for example, the NMEA GLL and VTG sentences can only output 'RTK', whereas the NMEA GGA or RMC sentences or UBX NAV-PVT message can distinguish between 'RTK-FIXED' and 'RTK-FLOAT'.
  - The correction age (aka 'diffAge') will reflect the elapsed time since the most recently received correction. Note that the F9P (*in its default configuration*) will continue to apply RTK corrections for up to 60 seconds after the last correction message is received.
  - The reference station ID (aka 'diffStation') *may* change to the reference station's ARP identifier (this is purely an identifier - it has no direct bearing on positional accuracy and some reference stations broadcast a null or nominal identifier which will appear in PyGPSClient as "N/A").
  - After a short period (typically a minute or so), the reported horizontal and vertical accuracy values ('hAcc' and 'vAcc') will start to fall to < 1m levels - **BUT NOTE [CAVEATS](#caveats) BELOW**.

- If you're using an F9P or similar, useful additional diagnostics can be obtained by enabling UBX RXM-COR (or, for RTCM only, RXM-RTCM) Receiver Management message types (this can be done using PYGPSClient's UBX CFG-MSG or CFG-VALSET [configuration facilities](https://github.com/semuconsulting/PyGPSClient?tab=readme-ov-file#ubxconfig)). For example, the RXM-COR message includes two data attributes `errStatus` and `msgUsed`; `errStatus=1, msgUsed=2` signifies that valid RTK correction data has been received successfully and has been applied to the receiver's navigation solution. For diagnosing L-Band SPARTN reception issues, the UBX INF-DEBUG Information message can also be useful. Refer to the [F9P Interface Manual](https://www.u-blox.com/sites/default/files/documents/u-blox-F9-HPG-1.50_InterfaceDescription_UBXDOC-963802114-12815.pdf) for further details on the meaning of the various UBX NAV, RXM and INF message types and data attributes.
- If, having enabled RXM-COR or RXM-RTCM message types, you see none in the console, this may mean the RTK correction data is not making its way through to your receiver. This could be due to a configuration or connection error of some kind e.g.
  - If the RTK service requires client authentication, ensure you are using correct and current credentials (PyGPSClient will generally report an HTTP 4nn Not Authorized error in these circumstances).
  - Some RTK services are "geofenced" and will only provide data to clients within a specified geographical area. Check with the service provider.
  - If the NTRIP caster requires NMEA GGA position data (signified by a '1' in the 11th position of the sourcetable - the one after Longitude), ensure you have this enabled in the NTRIP client configuration panel.

    ![sourcetable gga marker](https://github.com/semuconsulting/PyGPSClient/blob/master/images/sourcetable_ggamarker.png?raw=true)
  - If the RTK data is encrypted (as with Thingstream PointPerfect SPARTN MQTT or L-Band services), ensure that the latest decryption keys have been uploaded to the receiver via an RXM-SPARTN-KEY message. SPARTN decryption keys are typically only valid for a 4 week period and need to be refreshed regularly.
  - If using an internet RTK service (NTRIP or MQTT), ensure you have active internet connectivity and that the service's IP port (typically 2101, 2102, 443 or 8883) is not being blocked by a firewall.
  - Ensure that your F9P is configured to allow incoming RTCM3 data on the designated port - this is the default setting, but it may have been overwritten.

### 8. "FLOAT" vs "FIXED"

- It is important to understand that these RTK status values are based, in essence, on a statistical analysis (using the principles of [Kalman Filtering](https://en.wikipedia.org/wiki/Kalman_filter)) of the [various errors](https://www.semuconsulting.com/gnsswiki/#Errors) ('residuals') which affect the calculation of carrier phase pseudorange, and hence the accuracy of the navigation solution.
- The receiver's firmware applies a complex proprietary algorithm to determine if this statistical analysis is within a certain tolerance. If it is, the receiver will report an 'RTK-FIXED' status. If it is outside the designated tolerance, the receiver may report an 'RTK-FLOAT' status. This doesn't *necessarily* mean that the solution is less accurate - it just means that the *confidence* level is lower than 'FIXED'.
- An 'RTK-FLOAT' status will therefore generally yield a lower accuracy estimation (`hAcc`, `vAcc`) than 'RTK-FIXED'.

### <a name="caveats">9. Some caveats on "hAcc" and "vAcc"</a>

- **NB:** `hAcc` and `vAcc` values are *not* available from the default cohort of NMEA messages output by most GNSS receivers (including the F9P). In order to receive these values, you will need to enable either proprietary NMEA sentences like u-blox's UBX00, or UBX messages like NAV-PVT.
- Much is made of reported horizontal (hAcc) and vertical (vAcc) accuracy figures, but they are **merely estimates** based on a statistical analysis of:
  - Number of satellites (`sip`)
  - Signal strengths (`CN₀`)
  - Geometric distribution of the satellites (`dop`)
  - Pseudorange residuals ([UERE](https://en.wikipedia.org/wiki/Error_analysis_for_the_Global_Positioning_System))
- In the case of the F9P receiver, the analysis itself is proprietary and is performed within the F9P's firmware, rather than in client software.
- Ultimately, the only *definitive* way of establishing the accuracy of an RTK (or PPK) navigation solution is to compare it with a known fixed reference point whose 3D coordinates have been independently verified via high precision surveying techniques.
- Note that the 7th and 8th decimal places of a decimal lat/lon coordinate are equivalent to about 1.1cm and 1.1mm respectively, which represents the practical limit of any RTK or PPK GNSS application - anything more than this would be spurious.

---
## <a name="example">Illustrated Example</a>

The following screen shot illustrates an RTK fix obtained using a [SparkFun GPS-RTK-SMA](https://www.sparkfun.com/products/16481) GNSS module and [u-blox ANN-MB-00](https://www.sparkfun.com/products/15192) antenna mounted on a steel car roof (approximately 1.5m high with a base altitude of 66m) at a location with more-or-less 360° unrestricted visibility of the sky, around late afternoon in good weather conditions. The RTK source was a [EUREF NTRIP](https://www.euref.eu/euref-services) 2.0 reference station (mountpoint) situated some 28km to the west. [EUREF](https://epncb.oma.be/) uses the [European Terrestrial Reference System 89 or ETRS89](http://etrs89.ensg.ign.fr/), which at time of writing is coincident with the [ITRS](https://en.wikipedia.org/wiki/International_Terrestrial_Reference_System_and_Frame) at epoch 1989.0. The source had been active for approximately 60 seconds prior to the screenshot being taken.

- The incoming RTCM data may be seen in the console with the tag `NTRIP>>`.
- The UBX NAV-PVT messages are reporting `diffSoln=1` ("differential corrections were applied"), `carrSoln=2` ("carrier phase range solution with fixed
ambiguities" i.e. 'RTK-FIXED') and `lastCorrectionAge=3` ("Age between 2 and 5 seconds").
- The UBX RXM-COR messages are reporting `errStatus=1` ("Error-free"),`msgUsed=2` ("Used") and `msgInputHandle=1` ("Receiver has input handling support for this
message").
- The 'Satellites' widget indicates broad sky visibility, with plenty of satellites with strong signals visible at or near the horizon.
- The 'Levels' widget indicates that we are receiving at least 15 satellites with a CN₀ of 45dB or better.
- The 'Spectrum' widget indicates that the receiver has good reception on both L1 and L2 frequencies.
- The 'Scatter Plot' widget indicates position variability well within the 0.1m radius.
- The 'Rover Plot' widget indicates the relative position of reference station (centre of plot) and receiver antenna (orange vector).

The *indicated* horizontal accuracy (`hacc`) is 1.4cm but *note [caveats](#caveats) above*.

![full app screenshot ubx](https://github.com/semuconsulting/PyGPSClient/blob/master/images/app.png?raw=true)


---
## <a name="glossary">Glossary of Terms and Abbreviations</a>

|            |                     |                      |
| ---------- | ------------------- | -------------------- |
| **Term**   | **Definition**      | **Comments**         |
| ARP        | Antenna Reference Point | The identifier for a specific RTK data source |
| BNC        | Bayonet Neill–Concelman | A standard bayonet antenna connector type |
| CN₀        | Carrier to noise ratio | A measure of GNSS signal strength |
| CORS       | Continuously Operating Reference Station | A term denoting an RTK correction source e.g. NTRIP server |
| DGPS/DGNSS | Differential GPS/GNSS | A [high resolution positioning technique](https://en.wikipedia.org/wiki/Differential_GPS) that enhances the positional data available from GNSS systems by reference to a network of fixed position, ground-based (or "virtual") reference stations |
| DOP        | Dilution of Precision | A measure of the effect of the geometric distribution of visible GNSS satellites on positional accuracy |
| HACC       | Horizontal Accuracy | A statistical estimate of horizontal positional accuracy based on a number of factors |
| ITRF       | International Terrestrial Reference Frame | A [reference frame](https://itrf.ign.fr/en/homepage) which takes into account tectonic plate movement and gravitational/magnetic displacements, necessary for mm level accuracy. The “earth-fixed” ITRF is typically not regarded as a “datum” – rather it is the international standard reference framework to which national geocentric datums are aligned |
| L1         | | Original GPS C/A carrier frequency 1575.42 MHz |
| L2         | | Original GPS P(Y) carrier frequency 1227.60 MHz |
| L5         | | A more modern GNSS carrier frequency 1176.45 MHz |
| L-Band     | | A radio frequency band covering the spectrum 1 GHz to 2 GHz |
| LNA        | Low-noise Amplifier | A signal booster built into some active GNSS antennae |
| NTRIP      | Networked Transport of RTCM via Internet Protocol | A proprietary RTK DGPS protocol published by the RTCM | 
| PPK        | Post-processing kinematics | A [high resolution surveying technique](https://www.advancednavigation.com/tech-articles/benefits-of-using-post-processing-kinematic-ppk-software-in-gnss-based-and-inertial-navigation-solutions/), similar in principal to RTK but with corrections being applied retrospectively to a set of captured raw GNSS navigation and observation data, typically converted to RINEX format |
| RF         | Radio Frequency | In the context of GNSS this generally refers to the L-Band |
| RF240      | | A higher quality solid-core RF coaxial cable specification which offers reduced attenuation over longer distances than RG58 |
| RG58       | | A common specification of stranded-core RF coaxial cable suitable for short cable runs |
| RINEX      | Receiver Independent Exchange Format | A proprietary vendor-agnostic GNSS data protocol published by the RTCM and commonly used for PPK |
| RTCM       | Radio Technical Commission for Maritime Services | The not-for-profit body which publishes the NTRIP, RTCM3 and RINEX protocols |
| RTK        | Real-time kinematics | A real-time [high resolution surveying technique](https://en.wikipedia.org/wiki/Real-time_kinematic_positioning) which corrects for [common errors](https://www.semuconsulting.com/gnsswiki/#Errors) in GNSS positional data using measurements of the phase of the signal's carrier wave in addition to the information content of the signal. It relies on a single reference station or interpolated virtual station to provide real-time corrections, providing up to centimeter-level accuracy.
| RTN        | Real-time Network | A real-time [high resolution surveying technique](https://water.usgs.gov/osw/gps/real-time_network.html), similar in principle to RTK but using a computed or "virtual" reference station rather than a physical reference station | 
| SIP        | Satellites in Position | The number of satellites actually used in the receiver's navigation solution |
| SIV        | Satellites in View | The number of satellites the receiver can see |
| SMA        | Subminiature version A | A standard miniature threaded antenna connector type |
| SPARTN     | Secure Position Augmentation for Real Time Navigation | An open-source RTK DGPS protocol published by u-blox |
| TNC        | Threaded Neill-Concelman | A standard threaded antenna connector type commonly used in surveying equipment |
| UERE       | User equivalent range errors | Collective term for a [range of errors](https://www.semuconsulting.com/gnsswiki/#Errors) which must be compensated for in GNSS pseudorange calculations, sometimes referred to as pseudorange 'residuals' |
| U.FL       | Ultra-fine Fluorinated | An ultra-miniature antenna connector type common in hobbyist equipment |
| URA        | User range error | See UERE |
| VACC       | Vertical Accuracy | A statistical estimate of vertical positional accuracy based on a number of factors |

---
## <a name="references">References and Further Reading</a>

1. [GNSS Positioning - A Reviser](https://www.semuconsulting.com/gnsswiki/)
1. [Differential GPS](https://en.wikipedia.org/wiki/Differential_GPS)
1. [Real-time kinematic positioning](https://en.wikipedia.org/wiki/Real-time_kinematic_positioning)
1. [GNSS Pseudorange Estimation - the 'Integer Ambiguity' Problem](https://www.youtube.com/watch?v=2gJrUlEhQ0Q&ab_channel=semuadmin)
1. [RTK Fundamentals](https://gssc.esa.int/navipedia/index.php/RTK_Fundamentals)
1. [Error analysis for the Global Positioning System](https://en.wikipedia.org/wiki/Error_analysis_for_the_Global_Positioning_System)
1. [u-blox GNSS Antennas Paper](https://www.ardusimple.com/wp-content/uploads/2022/04/GNSS-Antennas_AppNote_UBX-15030289.pdf)
1. [GPS Antenna and Coaxial Cable Specifications](https://www.gps-repeaters.com/blog/gps-repeater-antenna-and-coaxial-cable-specification/)
1. [Importance of Ground Planes](https://novotech.com/pages/ground-plane)
1. [Ardusimple GNSS Antenna Installation Guide](https://www.ardusimple.com/gps-gnss-antenna-installation-guide/)
1. [RTCM DGNSS standards](https://rtcm.myshopify.com/collections/differential-global-navigation-satellite-dgnss-standards)
1. [International Terrestial Reference Frame System](https://itrf.ign.fr/en/homepage)


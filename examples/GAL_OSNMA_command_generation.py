"""
GAL_OSNMA_command_generation.py

This Python script illustrates how to generate Galileo OSNMA Merkle and PublicKey
MGA commands using PyGPSClient's ubx2preset utility.

*** Use the latest keys from the relevant u-blox XML OSNMA credentials file ***

The serialized messages can be sent directly to the receiver.

Alternatively, the preset command string can be inserted into the "ubxpresets_l" section of
the PyGPSClient json configuration file and invoked from the UBX Configuration dialog via a
'single-click'.

https://content.u-blox.com/sites/default/files/documents/OSNMA_configuration_using_u-center_AppNote_UBXDOC-963802114-12194.pdf

Created by semuadmin on 10 Oct 2026.
"""

# pylint: disable=line-too-long

from pyubx2 import UBXMessage, SET
from pygpsclient import ubx2preset

# Merkle as defined in XML file as space-delimited hexadecimal string
MERKLE = "83 2E 15 ED E5 56 55 EA C6 E3 99 A5 39 47 7B 7C 03 4C CE 24 C3 C9 3F FC 90 4A CD 9B F8 42 F0 4E"
treenode = int.from_bytes(bytes.fromhex(MERKLE.replace(" ", "")), "little")
msg1 = UBXMessage(
    "MGA",
    "MGA-GAL-OSNMA-MERKLE",
    SET,
    type=0x08,
    applicabilityTime=1,
    treeNode=treenode,
)

# Public Key as defined in XML file as space-delimited hexadecimal string
PUBKEY = "02 21 92 04 B5 CA 6C 46 B6 23 EE ED 6C DD 2C DD B1 F7 D6 A7 53 27 67 E5 B8 DA 0D E1 EB D6 95 FC 99"
pubkeypoint = int.from_bytes(bytes.fromhex(PUBKEY.replace(" ", "")), "little")
msg2 = UBXMessage(
    "MGA",
    "MGA-GAL-OSNMA-PUBKEY",
    SET,
    type=0x07,
    pubKeyId=0x12, # amend as required
    pubKeyType=0,
    pubKeyPoint=pubkeypoint,
)

print(f"\nSerialized UBX Messages:\n{msg1.serialize()}\n{msg2.serialize()}")
preset = ubx2preset((msg1, msg2), "Upload Galileo OSNMA Merkle & Public Key")
print(f"\nPreset command string:\n{preset}")

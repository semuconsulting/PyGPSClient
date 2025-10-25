"""
Illustration of how to create UBX configuration database
messages and convert them to a UBX preset entry which can
be inserted into the ubxpresets_l section of a .json config
file.

Created on 21 Feb 2024

@author: semuadmin
"""

from pyubx2 import SET_LAYER_BBR, TXN_NONE, UBXMessage

from pygpsclient import ubx2preset

layers = SET_LAYER_BBR  # battery-backed RAM (non-volatile)
transaction = TXN_NONE
cfgdata = [("CFG_MSGOUT_UBX_RXM_RAWX_UART1", 1), ("CFG_MSGOUT_UBX_RXM_SFRBX_UART1", 1)]

msg = UBXMessage.config_set(layers, transaction, cfgdata)
print(msg)
preset = ubx2preset(msg, "Enable RAWX and SFRBX messages on UART1")
print(preset)

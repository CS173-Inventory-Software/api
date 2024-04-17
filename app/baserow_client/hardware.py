from . import baserow, BASEROW_TABLE_MAP

class Hardware:
    table = baserow.get_table(BASEROW_TABLE_MAP['HARDWARE'])

class HardwareInstance:
    table = baserow.get_table(BASEROW_TABLE_MAP['HARDWARE_INSTANCE'])

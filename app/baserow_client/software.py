from . import baserow, BASEROW_TABLE_MAP

class Software:
    table = baserow.get_table(BASEROW_TABLE_MAP['SOFTWARE'])

class SoftwareInstance:
    table = baserow.get_table(BASEROW_TABLE_MAP['SOFTWARE_INSTANCE'])

class SoftwareSubscription:
    table = baserow.get_table(BASEROW_TABLE_MAP['SOFTWARE_SUBSCRIPTION'])
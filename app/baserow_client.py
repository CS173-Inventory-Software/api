from inventory import settings
from baserowapi import Baserow

baserow = Baserow(url='https://baserow.kimpalao.com', token=settings.BASEROW_TOKEN)

users_table = baserow.get_table(513)
hardware_table = baserow.get_table(514)
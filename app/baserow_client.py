from inventory import settings
from baserowapi import Baserow

baserow = Baserow(url='https://baserow.kimpalao.com', token=settings.BASEROW_TOKEN)

users_table = baserow.get_table(513)
hardware_table = baserow.get_table(514)
hardware_instance_table = baserow.get_table(539)
status_table = baserow.get_table(515)

def get_baserow_operator(op):
    match op:
        case 'equals':
            return 'equal'
        case 'contains':
            return 'contains'
        case 'dateIs':
            return 'date_equal'
        case 'dateIsNot':
            return 'date_not_equal'
        case 'dateBefore':
            return 'date_before'
        case 'dateAfter':
            return 'date_after'
        case _:
            return op
from . import baserow, BASEROW_TABLE_MAP
from enum import Enum

class User:
    table = baserow.get_table(BASEROW_TABLE_MAP['USERS'])

    @classmethod
    def create(cls, email: str, type: int):
        new_row = {
            'email': email,
            'type': [type],
        }

        print(new_row)

        return cls.table.add_row(new_row)


class UserType:
    table = baserow.get_table(BASEROW_TABLE_MAP['USER_TYPES'])

class UserTypeEnum(Enum):
    _ignore_ = ['table']

    ROOT_ADMIN = 1
    SUPER_ADMIN = 2
    ADMIN = 3
    CLERK = 4
    VIEWER = 5

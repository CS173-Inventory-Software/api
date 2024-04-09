from . import baserow

class AssignmentLog:
    table = baserow.get_table(541)

    @staticmethod
    def assign(user: int, hardware: int=None, software: int=None, assignment_type: int=1):
        row = {
            'user': [user],
            'assignment_type': [assignment_type],
        }
        if hardware:
            row['hardware_instance'] = [hardware]
        if software:
            row['software_instance'] = [software]
        return AssignmentLog.table.add_row(row)
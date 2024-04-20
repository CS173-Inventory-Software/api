from . import baserow, BASEROW_TABLE_MAP

class Hardware:
    table = baserow.get_table(BASEROW_TABLE_MAP['HARDWARE'])

    @staticmethod
    def create(name: str, brand: str, type: str, model_number: str, description: str, instances: list):
        new_row = Hardware.table.add_row({
            'name': name,
            'brand': brand,
            'type': type,
            'model_number': model_number,
            'description': description,
        })

        for instance in instances:
            HardwareInstance.create(new_row.id, instance['serial_number'], instance['procurement_date'], instance.get('status', None))

        return new_row

class HardwareInstance:
    table = baserow.get_table(BASEROW_TABLE_MAP['HARDWARE_INSTANCE'])

    @staticmethod
    def create(hardware: int, serial_number: str, procurement_date: str, status: str=None):
        return HardwareInstance.table.add_row({
            'hardware': [hardware],
            'serial_number': serial_number,
            'procurement_date': procurement_date,
            'status': [status] if status else [],
        })
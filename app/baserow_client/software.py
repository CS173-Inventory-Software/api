from . import baserow, BASEROW_TABLE_MAP

class Software:
    table = baserow.get_table(BASEROW_TABLE_MAP['SOFTWARE'])

    @staticmethod
    def create(name: str, brand: str, version_number: str, description: str, expiration_date: str, instances: list, subscriptions: list):
        new_row = Software.table.add_row({
            'name': name,
            'brand': brand,
            'version_number': version_number,
            'description': description,
            'expiration_date': expiration_date,
        })

        for instance in instances:
            SoftwareInstance.create(
                new_row.id, 
                instance['serial_key'], 
                instance.get('status', None))
            
        for subscription in subscriptions:
            SoftwareSubscription.create(
                new_row.id, 
                subscription['start'], 
                subscription['end'], 
                subscription['number_of_licenses']
            )

        return new_row

class SoftwareInstance:
    table = baserow.get_table(BASEROW_TABLE_MAP['SOFTWARE_INSTANCE'])

    @staticmethod
    def create(software: int, serial_key: str, status: str=None):
        return SoftwareInstance.table.add_row({
            'software': [software],
            'serial_key': serial_key,
            'status': [status] if status else [],
        })

class SoftwareSubscription:
    table = baserow.get_table(BASEROW_TABLE_MAP['SOFTWARE_SUBSCRIPTION'])

    @staticmethod
    def create(software: int, start: str, end: str, number_of_licenses: int):
        return SoftwareSubscription.table.add_row({
            'software': [software],
            'start': start,
            'end': end,
            'number_of_licenses': number_of_licenses,
        })
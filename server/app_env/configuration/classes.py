import json


class Fields:
    def __init__(self):
        self.name = ""


class Table:
    def __init__(self):
        self.name = ""
        self.fields: [Fields] = []


class DataBase:
    def __init__(self):
        self.name = ""
        self.host = "localhost"
        self.port = 3036
        self.username = "root"
        self.password = ""
        self.tables: [Table] = []


class DataBaseJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DataBase):
            return {
                "name": obj.name,
                "host": obj.host,
                "port": obj.port,
                "username": obj.username,
                "password": obj.password,
                "tables": [
                    {
                        "name": table.name,
                        "fields": [
                            {"name": field.name, "type": field.type} for field in table.fields
                        ]
                    } for table in obj.tables
                ]
            }
        elif isinstance(obj, Table):
            return {
                "name": obj.name,
                "fields": [
                    {"name": field.name, "type": field.type} for field in obj.fields
                ]
            }
        elif isinstance(obj, Fields):
            return {
                "name": obj.name,
            }
        return super(DataBaseJSONEncoder, self).default(obj)


if __name__ == "__main__":
    pass

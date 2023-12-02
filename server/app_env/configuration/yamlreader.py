import yaml

from server.app_env.configuration.classes import DataBase, Table, Fields


def read_config(file):
    try:
        config_data = yaml.safe_load(file)

        database = DataBase()
        if config_data['database'] is not None:
            dbconfig = config_data['database']
            database.name = dbconfig['name']
            database.host = dbconfig['host']
            database.port = dbconfig['port']
            database.username = dbconfig['username']
            database.password = dbconfig['password']

            if dbconfig['tables'] is not None:
                for table_data in dbconfig['tables']:
                    table = Table()
                    table.name = table_data['name']

                    if table_data['fields'] is not None:
                        for field_data in table_data['fields']:
                            field = Fields()
                            field.name = field_data['name']
                            field.type = field_data['type']
                            table.fields.append(field)

                    database.tables.append(table)

        return database
    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")
        return None

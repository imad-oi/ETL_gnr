import yaml

from server.app_env.configuration.classes import DataBase, Table, Fields


def read_config(file):
    try:
        config_data = yaml.safe_load(file)

        database = DataBase()
        database.name = config_data['database']['name']
        database.host = config_data['database']['host']
        database.port = config_data['database']['port']
        database.username = config_data['database']['username']
        database.password = config_data['database']['password']

        for table_data in config_data['database']['tables']:
            table = Table()
            table.name = table_data['name']

            for field_data in table_data['fields']:
                field = Fields()
                field.name = field_data['name']
                field.type = field_data['type']
                table.fields.append(field)

            database.tables.append(table)

        print(database)
        return database

    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")
        return None

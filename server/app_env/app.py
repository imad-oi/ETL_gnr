import io

import mysql.connector
import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from server.app_env.configuration.classes import DataBase
from server.app_env.configuration.yamlreader import read_config

app = Flask(__name__)
CORS(app)

config: DataBase = DataBase()
dataframe: pd.DataFrame
uploaded_columns = []


@app.route('/')
def hello():
    return 'Hello, World!'


def fetch_columns(file):
    global dataframe
    try:
        if file.filename == '':
            return {'error': 'No file selected'}, 400

        dataframe = pd.read_excel(file)
        uploaded_columns.extend(dataframe.columns.tolist())
        return True, uploaded_columns, None
    except Exception as e:
        return False, [], str(e)


def fetch_config(file):
    global config

    try:
        if file.filename != '':
            config = read_config(file)
            fields = [f.name for f in config.tables[0].fields]

            return True, fields
    except RuntimeError as e:
        raise RuntimeError("Error processing the file") from e


@app.route('/upload', methods=['POST'])
def upload_file():
    global config, uploaded_columns

    if 'data' not in request.files or 'config' not in request.files:
        return {'error': 'Both data and config files are required'}, 400

    data_file = request.files['data']
    config_file = request.files['config']

    success, columns, error = fetch_columns(data_file)

    if not success:
        return {'error': error}, 500

    try:
        success, fields = fetch_config(config_file)
        if not success:
            raise RuntimeError("Error processing the file")
    except RuntimeError as e:
        return {'error': str(e)}, 500

    return jsonify({
        "config": fields,
        "data": columns
    }), 200


def convert(fields_columns: {}) -> []:
    mapped_columns_df = dataframe[list(fields_columns.values())]
    return mapped_columns_df.to_dict(orient='records')


def insert(data) -> []:
    # Connexion à la base de données MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user='root',
        password='',
        database='etl'
    )
    cursor = conn.cursor()

    # create the table
    table = config.tables[0]
    fields = ", ".join([f"`{field.name}` {field.type}" for field in table.fields])
    insert_query = f"""
    CREATE TABLE IF NOT EXISTS `{table.name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        {fields}
    );
    """
    cursor.execute(insert_query)

    # insert data to the table
    errors_data = []
    for row in data:
        try:
            insert_query = (f"INSERT INTO `{table.name}` "
                            f"({', '.join(map(lambda k: f'`{k}`', row.keys()))}) "
                            f"VALUES ({', '.join(['%s'] * len(row))})")
            values = list(row.values())
            cursor.execute(insert_query, tuple(values))
            conn.commit()
        except Exception:
            errors_data.append(row)
    conn.close()
    return errors_data


@app.route('/save', methods=['POST'])
def save_data():
    fields_columns = request.json
    data = convert(fields_columns)
    errors = insert(data)
    errors_df = pd.DataFrame(errors)

    # Save DataFrame to CSV in-memory
    csv_data = io.BytesIO()
    errors_df.to_csv(csv_data, index=False)
    csv_data.seek(0)

    # Send CSV file back to the client
    return send_file(
        csv_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name='errors.csv'
    )


if __name__ == '__main__':
    app.run(debug=True)

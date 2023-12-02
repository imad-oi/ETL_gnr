import pandas as pd
from flask import Flask, request
from flask_cors import CORS

from server.app_env.configuration.classes import DataBase
from server.app_env.configuration.yamlreader import read_config

app = Flask(__name__)

CORS(app)

config: [DataBase]
uploaded_columns = []


@app.route('/')
def hello():
    return 'Hello, World!'


def fetch_columns(file):
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    try:
        df = pd.read_excel(file)
        uploaded_columns.extend(df.columns.tolist())
        return True, uploaded_columns, None
    except Exception as e:
        return False, [], str(e)


def upload_yaml(file):
    global config

    if file.filename != '':
        config = read_config(file)
        fields = [f.name for f in config.tables[0].fields]

        if config is not None:
            return True, fields
        else:
            raise RuntimeError("Error processing the file")


@app.route('/upload', methods=['POST'])
def upload_file():
    global config, uploaded_columns
    if 'data' not in request.files:
        return {'error': 'No data provided'}, 400

    if 'config' not in request.files:
        return {'error': 'No config provided'}, 400

    data_file = request.files['data']
    config_file = request.files['config']

    if data_file.filename == '':
        return {'error': 'No data selected'}, 400

    try:
        df = pd.read_excel(data_file)
        uploaded_columns.extend(df.columns.tolist())
    except Exception as e:
        return {'error': str(e)}, 500

    try:
        config = read_config(config_file)
        fields = [f.name for f in config.tables[0].fields]
    except RuntimeError as e:
        return {'error': str(e)}, 500

    return {
        "config": fields,
        "data": uploaded_columns
    }, 200


if __name__ == '__main__':
    # activate debug mode
    app.debug = True
    app.run()

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

from server.app_env.configuration.yamlreader import read_config

app = Flask(__name__)
CORS(app)

config = None
uploaded_columns = []


@app.route('/')
def hello():
    return 'Hello, World!'


def fetch_columns(file):
    try:
        if file.filename == '':
            return {'error': 'No file selected'}, 400

        df = pd.read_excel(file)
        uploaded_columns.extend(df.columns.tolist())
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


if __name__ == '__main__':
    # activate debug mode
    app.run(debug=True)

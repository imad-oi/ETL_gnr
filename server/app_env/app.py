from flask import Flask, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)

CORS(app)
@app.route('/')
def hello():
    return 'Hello, World!'

uploaded_columns = []  # Initialisez la liste des noms de colonnes

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    file = request.files['file']

    if file.filename == '':
        return {'error': 'No file selected'}, 400

    try:
        # Lire le fichier Excel avec pandas
        df = pd.read_excel(file)

        # Stocker les noms de colonnes dans la liste uploaded_columns
        uploaded_columns.extend(df.columns.tolist())

        # Convertir le DataFrame en liste de dictionnaires si nécessaire
        data_array = df.to_dict('records')

        # Faites quelque chose avec data_array, comme le stocker dans une base de données
        # Ou effectuer des opérations spécifiques sur les données

        return {'success': True, 'uploaded_columns': uploaded_columns}, 200

    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    # activate debug mode
    app.debug = True
    app.run()

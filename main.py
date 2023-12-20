from flask import Flask, request, Response, jsonify
import json
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from collections import OrderedDict
import os

load_dotenv()

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('DB_NAME')

mysql = MySQL(app)

data = pd.read_csv('https://storage.googleapis.com/livingaura/Dataset.csv')

features = ['ID', 'society', 'location', 'price', 'total_sqft', 'surface_area', 'bedroom', 'bathroom', 'carport']
numeric_features = ['price', 'total_sqft', 'surface_area', 'bedroom', 'bathroom', 'carport']

numeric_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

nlp_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('nlp', nlp_transformer, ['location']),
        ('num', numeric_transformer, numeric_features)
    ]
)

search_model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('search', NearestNeighbors(n_neighbors=3, algorithm='ball_tree'))
])

search_model.fit(data[features])

def fetch_table_data(table_name, identifiers):
   
    column_names = [
        "identifier_project",
        "name_project",
        "type_project",
        "ready",
        "indent",
        "location_project",
        "price_list_project_cash",
        "price_list_project_credit",
        "promo",
        "description_project",
        "bedroom",
        "bathroom",
        "carport",
        "building_area",
        "surface_area",
        "facility",
        "name_developer",
        "contact_developer",
        "loan_bank",
        "handover"
    ]

    query = f"SELECT * FROM {table_name} WHERE identifier_project IN ({', '.join(map(str, identifiers))})"

    cur = mysql.connection.cursor()
    cur.execute(query)
    fetchdata = cur.fetchall()
    cur.close()


    formatted_data = [
        OrderedDict((column, row[i]) for i, column in enumerate(column_names))
        for row in fetchdata
    ]

    return formatted_data

@app.route('/search', methods=['POST'])
def search_houses():
    query = request.json  # Ambil input pencarian dari permintaan POST JSON
    query_transformed = preprocessor.transform(pd.DataFrame([query], columns=features))
    _, indices = search_model.named_steps['search'].kneighbors(query_transformed)
    result_houses = data.iloc[indices[0]][features]
    modified_data = [{"identifier_project": entry["ID"]} for entry in result_houses.to_dict(orient='records')]
    
    table_name = 'tb_projects'
    result = fetch_table_data(table_name, [data['identifier_project'] for data in modified_data])

    json_data = json.dumps(result, sort_keys=False)

    response = Response(response=json_data, status=200, mimetype="application/json")

    return response
    

if __name__ == '__main__':
    app.run(debug=True)
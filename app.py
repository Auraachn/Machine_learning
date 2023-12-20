from flask import Flask, request, jsonify
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

app = Flask(__name__)

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

@app.route('/search', methods=['POST'])
def search_houses():
    query = request.json  # Ambil input pencarian dari permintaan POST JSON
    query_transformed = preprocessor.transform(pd.DataFrame([query], columns=features))
    _, indices = search_model.named_steps['search'].kneighbors(query_transformed)
    result_houses = data.iloc[indices[0]][features]
    return jsonify(result_houses.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

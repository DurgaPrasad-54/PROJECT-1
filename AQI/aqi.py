from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_aqi_bucket(aqi_value):
    if aqi_value <= 50:
        return "Good"
    elif aqi_value <= 100:
        return "Satisfactory"
    elif aqi_value <= 200:
        return "Moderate"
    elif aqi_value <= 300:
        return "Poor"
    elif aqi_value <= 400:
        return "Very Poor"
    else:
        return "Severe"

# Load dataset
df = pd.read_csv(r"C:\Users\prasa\OneDrive\Desktop\AQI\city_day_cleaned.csv")

# Drop unnecessary columns
df = df.drop(columns=["City", "Date", "AQI_Bucket"], errors="ignore")

# Convert all columns to numeric, ignoring errors
df = df.apply(pd.to_numeric, errors="coerce")

# Fill missing values
df.fillna(df.mean(), inplace=True)

# Select features and target variable
X = df[["PM2.5", "PM10", "NO2", "SO2", "O3"]]
y = df["AQI"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        input_values = ["PM2.5", "PM10", "NO2", "SO2", "O3"]
        
        # Validate input data
        if not all(param in data for param in input_values):
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Convert inputs to float
        user_input = np.array([[float(data[param]) for param in input_values]])
        
        # Predict AQI
        predicted_aqi = rf_model.predict(user_input)[0]
        aqi_bucket = get_aqi_bucket(predicted_aqi)

        return jsonify({
            "Predicted_AQI": round(predicted_aqi),
            "AQI_Category": aqi_bucket
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

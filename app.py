"""
=============================================================================
Home Rent Prediction System - Flask Web Application Backend
=============================================================================
Routes:
- GET /            : Interactive Prediction Form (Home Page)
- POST /predict    : Form submission, Preprocessing & Rent Prediction Result
- GET /about       : Project background, dataset details, methodology
- GET /model-info  : Model accuracy metrics, comparison table, graphs
- POST /api/predict: JSON REST API endpoint for integration
=============================================================================
"""

import sys
import io
import os
import json
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response, make_response

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)
app.secret_key = "home_rent_prediction_secret_key_2026"

# File paths
MODEL_PATH = "model/rent_prediction_model.pkl"
METADATA_PATH = "model/model_metadata.json"

# Load the trained machine learning pipeline
model_pipeline = None
model_metadata = {
    'best_model': 'Random Forest Regressor',
    'r2_score': 0.93,
    'accuracy_percent': 93.0,
    'rmse': 2850.0,
    'mae': 1950.0,
    'dataset_size': 1600,
    'models_comparison': [],
    'top_features': []
}

def load_saved_model():
    """Loads the pre-trained pipeline and metadata from disk."""
    global model_pipeline, model_metadata
    if os.path.exists(MODEL_PATH):
        try:
            model_pipeline = joblib.load(MODEL_PATH)
            print(f"✅ Loaded ML pipeline successfully from {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    else:
        print(f"⚠️ Warning: Model file {MODEL_PATH} not found. Please run train.py first.")

    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r") as f:
                model_metadata = json.load(f)
            print(f"✅ Loaded model metadata from {METADATA_PATH}")
        except Exception as e:
            print(f"⚠️ Could not load metadata: {e}")

# Initial load
load_saved_model()

# Valid choices for dropdowns & validations (Mymensingh, Bangladesh)
VALID_LOCATIONS = [
    'Charpara', 'Town Hall', 'Kachijhuli', 'Ganginar Par',
    'Maskanda', 'Notun Bazar', 'Shehora', 'Akua',
    'Sankipara', 'Choto Bazar', 'Kewatkhali', 'Panditpara'
]

VALID_PROPERTY_TYPES = ['Apartment', 'House', 'Duplex', 'Studio']
VALID_YES_NO = ['Yes', 'No']


def validate_input(form_data):
    """
    Validates input features from form or JSON payload.
    Returns: (is_valid: bool, error_message: str or None, cleaned_dict: dict)
    """
    errors = []
    
    # 1. Location
    location = str(form_data.get('location', '')).strip()
    if location not in VALID_LOCATIONS:
        errors.append(f"Invalid location selected. Choose from: {', '.join(VALID_LOCATIONS)}")

    # 2. Property Type
    property_type = str(form_data.get('property_type', '')).strip()
    if property_type not in VALID_PROPERTY_TYPES:
        errors.append(f"Invalid property type. Choose from: {', '.join(VALID_PROPERTY_TYPES)}")

    # 3. Numeric: Bedrooms
    try:
        bedrooms = int(form_data.get('bedrooms', 0))
        if bedrooms < 1 or bedrooms > 20:
            errors.append("Bedrooms must be between 1 and 20.")
    except (ValueError, TypeError):
        errors.append("Bedrooms must be a valid integer.")

    # 4. Numeric: Bathrooms
    try:
        bathrooms = int(form_data.get('bathrooms', 0))
        if bathrooms < 1 or bathrooms > 20:
            errors.append("Bathrooms must be between 1 and 20.")
    except (ValueError, TypeError):
        errors.append("Bathrooms must be a valid integer.")

    # 5. Numeric: House Size (sqft)
    try:
        house_size = float(form_data.get('house_size', 0))
        if house_size < 100:
            errors.append("House size must be at least 100 sqft.")
        elif house_size > 15000:
            errors.append("House size cannot exceed 15,000 sqft.")
    except (ValueError, TypeError):
        errors.append("House size must be a valid number.")

    # 6. Numeric: Floor & Total Floors
    try:
        floor = int(form_data.get('floor', 1))
        total_floors = int(form_data.get('total_floors', 1))
        if floor < 1:
            errors.append("Floor number must be at least 1 (Ground/1st Floor).")
        if total_floors < 1:
            errors.append("Total floors must be at least 1.")
        if floor > total_floors:
            errors.append("Floor cannot be greater than Total Floors of the building.")
    except (ValueError, TypeError):
        errors.append("Floor and Total Floors must be valid positive integers.")

    # 7. Categorical options (Furnished, Parking, Balcony)
    furnished = str(form_data.get('furnished', '')).strip().capitalize()
    if furnished not in VALID_YES_NO:
        furnished = 'No'

    parking = str(form_data.get('parking', '')).strip().capitalize()
    if parking not in VALID_YES_NO:
        parking = 'No'

    balcony = str(form_data.get('balcony', '')).strip().capitalize()
    if balcony not in VALID_YES_NO:
        balcony = 'No'

    # 8. House Age
    try:
        age = int(form_data.get('age', 0))
        if age < 0 or age > 100:
            errors.append("House age must be between 0 and 100 years.")
    except (ValueError, TypeError):
        errors.append("House age must be a valid non-negative integer.")

    if errors:
        return False, " | ".join(errors), None

    cleaned_dict = {
        'location': location,
        'property_type': property_type,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'house_size': house_size,
        'floor': floor,
        'total_floors': total_floors,
        'furnished': furnished,
        'parking': parking,
        'balcony': balcony,
        'age': age
    }
    return True, None, cleaned_dict


# =============================================================================
# WEB ROUTES
# =============================================================================

@app.route('/')
def home():
    """Renders Home page with prediction form."""
    return render_template(
        'index.html',
        locations=VALID_LOCATIONS,
        property_types=VALID_PROPERTY_TYPES,
        metadata=model_metadata
    )


@app.route('/predict', methods=['POST'])
def predict():
    """Processes user form submission and renders prediction result."""
    global model_pipeline
    if model_pipeline is None:
        load_saved_model()
        if model_pipeline is None:
            flash("Model is not loaded. Please train the model first by running `python train.py`.", "danger")
            return redirect(url_for('home'))

    # Validate form input
    is_valid, error_message, cleaned_data = validate_input(request.form)
    if not is_valid:
        flash(error_message, "danger")
        return render_template(
            'index.html',
            locations=VALID_LOCATIONS,
            property_types=VALID_PROPERTY_TYPES,
            form_data=request.form,
            metadata=model_metadata
        )

    try:
        # Convert dictionary to single-row DataFrame matching training format
        input_df = pd.DataFrame([cleaned_data])

        # Predict rent using the trained sklearn Pipeline
        prediction_val = model_pipeline.predict(input_df)[0]

        # Round predicted rent to nearest 100 BDT
        predicted_rent = int(round(max(5000, prediction_val) / 100.0) * 100)
        formatted_rent = f"{predicted_rent:,}"

        # Approximate range based on RMSE
        rmse = model_metadata.get('rmse', 2500)
        lower_bound = max(4000, int(round((predicted_rent - rmse) / 100.0) * 100))
        upper_bound = int(round((predicted_rent + rmse) / 100.0) * 100)

        return render_template(
            'result.html',
            prediction=predicted_rent,
            formatted_rent=formatted_rent,
            lower_bound=f"{lower_bound:,}",
            upper_bound=f"{upper_bound:,}",
            input_data=cleaned_data,
            metadata=model_metadata
        )
    except Exception as e:
        flash(f"Error during prediction: {str(e)}", "danger")
        return redirect(url_for('home'))


@app.route('/about')
def about():
    """Renders About page explaining the system architecture and dataset."""
    return render_template('about.html', metadata=model_metadata)


@app.route('/model-info')
def model_info():
    """Renders Model Evaluation page with graphs and metrics."""
    return render_template('model_info.html', metadata=model_metadata)


# =============================================================================
# BATCH CSV PREDICTION ROUTES
# =============================================================================

@app.route('/batch-predict', methods=['GET', 'POST'])
def batch_predict():
    """Handles CSV upload and batch rent prediction."""
    global model_pipeline
    if request.method == 'GET':
        return render_template('batch_predict.html', metadata=model_metadata)

    if model_pipeline is None:
        load_saved_model()
        if model_pipeline is None:
            flash("Model not loaded. Please train model using `python train.py` first.", "danger")
            return redirect(url_for('batch_predict'))

    if 'csv_file' not in request.files:
        flash("No CSV file selected. Please choose a valid .csv file.", "danger")
        return redirect(url_for('batch_predict'))

    file = request.files['csv_file']
    if file.filename == '' or not file.filename.endswith('.csv'):
        flash("Invalid file format. Please upload a .csv file.", "danger")
        return redirect(url_for('batch_predict'))

    try:
        df = pd.read_csv(file)
        required_cols = ['location', 'property_type', 'bedrooms', 'bathrooms', 'house_size', 
                         'floor', 'total_floors', 'furnished', 'parking', 'balcony', 'age']
        
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            flash(f"CSV is missing required column(s): {', '.join(missing_cols)}", "danger")
            return redirect(url_for('batch_predict'))

        if len(df) == 0:
            flash("The uploaded CSV file is empty.", "danger")
            return redirect(url_for('batch_predict'))

        # Prepare feature subset
        df_features = df[required_cols].copy()

        # Fill potential NaNs with sensible defaults
        df_features['furnished'] = df_features['furnished'].fillna('No')
        df_features['parking'] = df_features['parking'].fillna('No')
        df_features['balcony'] = df_features['balcony'].fillna('Yes')
        df_features['bedrooms'] = pd.to_numeric(df_features['bedrooms'], errors='coerce').fillna(2).astype(int)
        df_features['bathrooms'] = pd.to_numeric(df_features['bathrooms'], errors='coerce').fillna(2).astype(int)
        df_features['house_size'] = pd.to_numeric(df_features['house_size'], errors='coerce').fillna(1000).astype(float)
        df_features['floor'] = pd.to_numeric(df_features['floor'], errors='coerce').fillna(1).astype(int)
        df_features['total_floors'] = pd.to_numeric(df_features['total_floors'], errors='coerce').fillna(6).astype(int)
        df_features['age'] = pd.to_numeric(df_features['age'], errors='coerce').fillna(5).astype(int)

        # Batch prediction
        raw_predictions = model_pipeline.predict(df_features)
        
        # Round predictions to nearest 100 BDT
        predicted_rents = [int(round(max(5000, p) / 100.0) * 100) for p in raw_predictions]
        df_features['predicted_monthly_rent'] = predicted_rents

        # Calculate statistics
        total_records = len(df_features)
        avg_rent = float(df_features['predicted_monthly_rent'].mean())
        min_rent = float(df_features['predicted_monthly_rent'].min())
        max_rent = float(df_features['predicted_monthly_rent'].max())

        raw_csv_output = df_features.to_csv(index=False)
        rows = df_features.to_dict(orient='records')

        return render_template(
            'batch_result.html',
            total_records=total_records,
            avg_rent=avg_rent,
            min_rent=min_rent,
            max_rent=max_rent,
            rows=rows,
            raw_csv_output=raw_csv_output,
            metadata=model_metadata
        )
    except Exception as e:
        flash(f"Error processing CSV: {str(e)}", "danger")
        return redirect(url_for('batch_predict'))


@app.route('/download-sample-csv')
def download_sample_csv():
    """Generates and serves a sample CSV file for users to test batch prediction."""
    sample_data = {
        'location': ['Charpara', 'Kachijhuli', 'Town Hall', 'Shehora', 'Maskanda'],
        'property_type': ['Apartment', 'Duplex', 'Apartment', 'Studio', 'House'],
        'bedrooms': [3, 4, 3, 1, 4],
        'bathrooms': [2, 4, 2, 1, 3],
        'house_size': [1250, 2600, 1400, 450, 1800],
        'floor': [4, 6, 3, 2, 2],
        'total_floors': [7, 10, 6, 5, 5],
        'furnished': ['No', 'Yes', 'Yes', 'No', 'No'],
        'parking': ['Yes', 'Yes', 'Yes', 'No', 'Yes'],
        'balcony': ['Yes', 'Yes', 'Yes', 'No', 'Yes'],
        'age': [4, 2, 3, 1, 6]
    }
    df_sample = pd.DataFrame(sample_data)
    csv_str = df_sample.to_csv(index=False)
    
    response = make_response(csv_str)
    response.headers["Content-Disposition"] = "attachment; filename=sample_house_properties.csv"
    response.headers["Content-type"] = "text/csv"
    return response


@app.route('/download-batch-result', methods=['POST'])
def download_batch_result():
    """Downloads the predicted batch results CSV."""
    csv_data = request.form.get('csv_data', '')
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=predicted_house_rents.csv"
    response.headers["Content-type"] = "text/csv"
    return response


# =============================================================================
# REST API ENDPOINT
# =============================================================================

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    JSON API endpoint for rent prediction.
    Example Request Payload:
    {
        "location": "Charpara",
        "property_type": "Apartment",
        "bedrooms": 3,
        "bathrooms": 2,
        "house_size": 1200,
        "floor": 4,
        "total_floors": 7,
        "furnished": "Yes",
        "parking": "Yes",
        "balcony": "Yes",
        "age": 4
    }
    """
    global model_pipeline
    if model_pipeline is None:
        load_saved_model()
        if model_pipeline is None:
            return jsonify({
                "status": "error",
                "message": "Model not loaded. Please train model using train.py."
            }), 503

    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Content-Type must be application/json"
        }), 400

    data = request.get_json()
    is_valid, error_msg, cleaned_data = validate_input(data)
    if not is_valid:
        return jsonify({
            "status": "error",
            "message": "Validation failed",
            "errors": error_msg
        }), 422

    try:
        input_df = pd.DataFrame([cleaned_data])
        raw_pred = model_pipeline.predict(input_df)[0]
        predicted_rent = int(round(max(5000, raw_pred) / 100.0) * 100)

        return jsonify({
            "status": "success",
            "currency": "BDT (৳)",
            "predicted_rent": predicted_rent,
            "formatted_rent": f"৳ {predicted_rent:,}",
            "model_used": model_metadata.get('best_model', 'Random Forest'),
            "model_r2_score": model_metadata.get('r2_score', 0.93),
            "input_features": cleaned_data
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Prediction computation failed: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Start Flask development server
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Starting Home Rent Prediction Flask Server on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)

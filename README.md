# 🏠 Home Rent Prediction System (ML + Flask Web App)

An end-to-end Machine Learning web application designed to predict residential monthly home rent in Mymensingh, Bangladesh (in BDT ৳). Built with **Python, Scikit-Learn, and Flask**, this project is structured for academic presentations, school/college submissions, and viva examinations.

---

## 📌 Project Overview
- **Domain:** Real Estate Valuation & Machine Learning Regression
- **Target Currency:** Bangladeshi Taka (৳ BDT)
- **Focus Area:** Mymensingh City (Charpara, Kachijhuli, Town Hall, Ganginar Par, Maskanda, Notun Bazar, Shehora, Akua, Sankipara, Choto Bazar, Kewatkhali, Panditpara)
- **Objective:** Enable tenants and landlords to calculate fair market rental estimates based on multi-feature property specifications.

---

## 🚀 Key Features
- **100% Pipeline Consistency:** Uses `ColumnTransformer` + `Pipeline` (OneHotEncoder + StandardScaler) saved via `joblib`, preventing data leakage and preprocessing mismatches.
- **Multi-Algorithm Evaluation:** Automatically trains and compares 4 algorithms:
  1. Linear Regression
  2. Decision Tree Regressor
  3. Random Forest Regressor
  4. Gradient Boosting Regressor
- **Automatic Best Model Selection:** Deploys the model with the highest $R^2$ Score (95.64%) and lowest RMSE.
- **Modern Responsive UI:** Glassmorphic card design, quick-test profile presets, real-time input validation, and detailed breakdown cards with PNG image export.
- **Exploratory & Evaluation Graphs:** Automatically exports 5 visualization charts to `static/graphs/`.
- **RESTful API Endpoint:** `POST /api/predict` for mobile or frontend integrations.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.9+, Flask
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **Visualizations:** Matplotlib, Seaborn
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (ES6), Jinja2, html2canvas
- **Model Serialization:** Joblib

---

## 📁 Project Folder Structure
```text
home-rent-prediction/
│
├── app.py                     # Flask web server & REST API
├── train.py                   # ML Training Pipeline & Graph Generator
├── generate_dataset.py        # Synthetic Mymensingh housing dataset generator
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
│
├── data/
│   └── house_rent.csv         # Housing dataset (1600+ records)
│
├── model/
│   ├── rent_prediction_model.pkl  # Serialized Scikit-Learn Pipeline
│   └── model_metadata.json        # Evaluation metrics & top features
│
├── static/
│   ├── css/
│   │   └── style.css          # Responsive styling & design system
│   ├── js/
│   │   └── script.js          # Interactive presets & validation
│   └── graphs/
│       ├── actual_vs_predicted.png
│       ├── feature_importance.png
│       ├── rent_distribution.png
│       ├── correlation_heatmap.png
│       └── model_comparison.png
│
└── templates/
    ├── base.html              # Base Jinja2 layout (Navbar + Footer)
    ├── index.html             # Prediction form & hero section
    ├── result.html            # Prediction result card & breakdown with PNG download
    ├── about.html             # Project background & API documentation
    └── model_info.html        # Model evaluation table & charts
```

---

## ⚙️ Installation & How to Run

### Step 1: Clone or Navigate to Project Directory
```bash
cd f:/test/home-rent
```

### Step 2: Create and Activate Virtual Environment
**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Generate Realistic Dataset
```bash
python generate_dataset.py
```
*Creates `data/house_rent.csv` containing 1,600+ realistic Mymensingh rental listings.*

### Step 5: Train Machine Learning Models
```bash
python train.py
```
*Trains 4 regression algorithms, evaluates MAE/RMSE/R², exports `model/rent_prediction_model.pkl`, and creates 5 evaluation graphs.*

### Step 6: Start the Flask Web Server
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔌 REST API Documentation

### Endpoint:
`POST /api/predict`

### Request Headers:
`Content-Type: application/json`

### Example Request Body:
```json
{
    "location": "Charpara",
    "property_type": "Apartment",
    "bedrooms": 3,
    "bathrooms": 2,
    "house_size": 1250,
    "floor": 4,
    "total_floors": 7,
    "furnished": "Yes",
    "parking": "Yes",
    "balcony": "Yes",
    "age": 3
}
```

### Example JSON Response:
```json
{
    "status": "success",
    "currency": "BDT (৳)",
    "predicted_rent": 23500,
    "formatted_rent": "৳ 23,500",
    "model_used": "Gradient Boosting",
    "model_r2_score": 0.9564
}
```

---

## 📈 Evaluation Metrics Summary
| Model | MAE (৳) | RMSE (৳) | $R^2$ Score | Status |
|---|---|---|---|---|
| **Gradient Boosting** | **~1,815** | **~2,451** | **0.9564** | 🏆 **Best Model** |
| Linear Regression | ~2,104 | ~2,685 | 0.9477 | Evaluated |
| Random Forest Regressor | ~2,395 | ~3,286 | 0.9216 | Evaluated |
| Decision Tree Regressor | ~3,392 | ~4,642 | 0.8436 | Baseline |

---

## 🔮 Future Improvements
1. Integration of real-time geospatial coordinates & proximity to Mymensingh Medical College & BAU campus.
2. User authentication for landlords to save and manage listings.
3. Integration with a live database like PostgreSQL / SQLite for persistent user reviews.
4. Image recognition model to score interior aesthetic quality.

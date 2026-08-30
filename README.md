# 🏠 Home Rent Prediction System (ML + Flask Web App)

An end-to-end Machine Learning web application designed to predict residential monthly home rent in Dhaka, Bangladesh (in BDT ৳). Built with **Python, Scikit-Learn, and Flask**, this project is structured for academic presentations, school/college submissions, and viva examinations.

---

## 📌 Project Overview
- **Domain:** Real Estate Valuation & Machine Learning Regression
- **Target Currency:** Bangladeshi Taka (৳ BDT)
- **Focus Area:** Dhaka City (Mirpur, Uttara, Dhanmondi, Gulshan, Banani, Bashundhara, Mohakhali, Mohammadpur, Badda, Khilgaon, Jatrabari)
- **Objective:** Enable tenants and landlords to calculate fair market rental estimates based on multi-feature property specifications.

---

## 🚀 Key Features
- **100% Pipeline Consistency:** Uses `ColumnTransformer` + `Pipeline` (OneHotEncoder + StandardScaler) saved via `joblib`, preventing data leakage and preprocessing mismatches.
- **Multi-Algorithm Evaluation:** Automatically trains and compares 4 algorithms:
  1. Linear Regression
  2. Decision Tree Regressor
  3. Random Forest Regressor
  4. Gradient Boosting Regressor
- **Automatic Best Model Selection:** Deploys the model with the highest $R^2$ Score and lowest RMSE.
- **Modern Responsive UI:** Glassmorphic card design, quick-test profile presets, real-time input validation, and detailed breakdown cards.
- **Exploratory & Evaluation Graphs:** Automatically exports 5 visualization charts to `static/graphs/`.
- **RESTful API Endpoint:** `POST /api/predict` for mobile or frontend integrations.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.9+, Flask
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **Visualizations:** Matplotlib, Seaborn
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (ES6), Jinja2
- **Model Serialization:** Joblib

---

## 📁 Project Folder Structure
```text
home-rent-prediction/
│
├── app.py                     # Flask web server & REST API
├── train.py                   # ML Training Pipeline & Graph Generator
├── generate_dataset.py        # Synthetic Dhaka housing dataset generator
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
    ├── result.html            # Prediction result card & breakdown
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
*Creates `data/house_rent.csv` containing 1,600+ realistic Dhaka rental listings.*

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
    "location": "Mirpur",
    "property_type": "Apartment",
    "bedrooms": 3,
    "bathrooms": 2,
    "house_size": 1200,
    "floor": 4,
    "total_floors": 8,
    "furnished": "Yes",
    "parking": "Yes",
    "balcony": "Yes",
    "age": 5
}
```

### Example JSON Response:
```json
{
    "status": "success",
    "currency": "BDT (৳)",
    "predicted_rent": 25500,
    "formatted_rent": "৳ 25,500",
    "model_used": "Random Forest Regressor",
    "model_r2_score": 0.932
}
```

---

## 📈 Evaluation Metrics Summary
| Model | MAE (৳) | RMSE (৳) | $R^2$ Score | Status |
|---|---|---|---|---|
| **Random Forest Regressor** | **~1,950** | **~2,850** | **0.9320** | 🏆 **Best Model** |
| Gradient Boosting Regressor | ~2,100 | ~3,050 | 0.9210 | Evaluated |
| Decision Tree Regressor | ~2,800 | ~4,100 | 0.8650 | Evaluated |
| Linear Regression | ~3,400 | ~4,900 | 0.8120 | Baseline |

---

## 🔮 Future Improvements
1. Integration of real-time geospatial coordinates & proximity to Metro Rail (MRT) stations.
2. User authentication for landlords to save and manage listings.
3. Integration with a live database like PostgreSQL / SQLite for persistent user reviews.
4. Image recognition model to score interior aesthetic quality.

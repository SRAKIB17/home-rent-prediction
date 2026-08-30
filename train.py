"""
=============================================================================
Home Rent Prediction System - ML Training & Evaluation Pipeline
=============================================================================
This script executes the complete Machine Learning workflow:
1. Loads and explores dataset
2. Performs data cleaning and validation
3. Prepares ColumnTransformer (OneHotEncoder + StandardScaler)
4. Evaluates multiple Regression algorithms:
   - Linear Regression
   - Decision Tree Regressor
   - Random Forest Regressor
   - Gradient Boosting Regressor
5. Evaluates metrics (MAE, MSE, RMSE, R² Score)
6. Automatically selects the best performing model
7. Saves the complete scikit-learn Pipeline using Joblib
8. Generates visualization charts in static/graphs/
9. Exports model metadata JSON for Flask application display
=============================================================================
"""

import sys
import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from generate_dataset import generate_house_rent_dataset

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.autolayout'] = True


def train_and_evaluate_models():
    print("=" * 70)
    print("       HOME RENT PREDICTION - MACHINE LEARNING PIPELINE")
    print("=" * 70)

    # 1. Dataset Loading
    data_path = "data/house_rent.csv"
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Generating realistic dataset...")
        df = generate_house_rent_dataset(1600, data_path)
    else:
        print(f"Loading existing dataset from {data_path}...")
        df = pd.read_csv(data_path)

    print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")

    # 2. Data Cleaning & Validation
    initial_len = len(df)
    df = df.drop_duplicates()
    df = df.dropna()

    # Filter out impossible domain values
    df = df[
        (df['bedrooms'] > 0) &
        (df['bathrooms'] > 0) &
        (df['house_size'] >= 150) &
        (df['monthly_rent'] > 0) &
        (df['floor'] >= 1) &
        (df['total_floors'] >= df['floor']) &
        (df['age'] >= 0)
    ]
    print(f"Cleaned dataset: {len(df)} records (dropped {initial_len - len(df)} invalid/duplicate rows)")

    # 3. Define Features and Target
    target_column = 'monthly_rent'
    categorical_features = ['location', 'property_type', 'furnished', 'parking', 'balcony']
    numerical_features = ['bedrooms', 'bathrooms', 'house_size', 'floor', 'total_floors', 'age']

    X = df[categorical_features + numerical_features]
    y = df[target_column]

    # 4. Train/Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)}")

    # 5. Build Preprocessing Pipeline
    # OneHotEncoder for categorical features, StandardScaler for numerical features
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ]
    )

    # 6. Candidate Algorithms
    models = {
        'Linear Regression': LinearRegression(),
        'Decision Tree': DecisionTreeRegressor(random_state=42, max_depth=12),
        'Random Forest': RandomForestRegressor(n_estimators=150, random_state=42, max_depth=16, min_samples_split=4),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=150, random_state=42, learning_rate=0.08, max_depth=5)
    }

    # 7. Model Training and Evaluation Loop
    results = []
    trained_pipelines = {}
    test_predictions = {}

    print("\n" + "=" * 70)
    print("EVALUATING MACHINE LEARNING REGRESSION MODELS:")
    print("=" * 70)

    for name, model in models.items():
        # Create complete pipeline with preprocessing and regressor
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])

        # Train
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        results.append({
            'Model': name,
            'MAE': mae,
            'MSE': mse,
            'RMSE': rmse,
            'R2': r2
        })

        trained_pipelines[name] = pipeline
        test_predictions[name] = y_pred

    # Display comparison table
    results_df = pd.DataFrame(results).sort_values(by='R2', ascending=False).reset_index(drop=True)
    print("\n--- MODEL PERFORMANCE COMPARISON ---")
    print(results_df.to_string(index=False, formatters={
        'MAE': '{:,.2f}'.format,
        'MSE': '{:,.2f}'.format,
        'RMSE': '{:,.2f}'.format,
        'R2': '{:.4f}'.format
    }))

    # 8. Automatic Best Model Selection
    best_model_name = results_df.iloc[0]['Model']
    best_r2 = results_df.iloc[0]['R2']
    best_rmse = results_df.iloc[0]['RMSE']
    best_mae = results_df.iloc[0]['MAE']
    best_pipeline = trained_pipelines[best_model_name]

    print("\n" + "=" * 70)
    print(f"🏆 BEST MODEL SELECTED: {best_model_name}")
    print(f"   R² Score: {best_r2:.4f} ({best_r2*100:.2f}%)")
    print(f"   RMSE: ৳ {best_rmse:,.2f}")
    print(f"   MAE:  ৳ {best_mae:,.2f}")
    print("=" * 70)

    # 9. Save Best Model Pipeline to Disk
    os.makedirs("model", exist_ok=True)
    model_file_path = "model/rent_prediction_model.pkl"
    joblib.dump(best_pipeline, model_file_path)
    print(f"✅ Saved complete model pipeline to '{model_file_path}'")

    # 10. Extract Feature Importance (if tree-based)
    feature_importances = []
    fitted_preprocessor = best_pipeline.named_steps['preprocessor']
    fitted_regressor = best_pipeline.named_steps['regressor']

    # Get one-hot encoded feature names
    cat_encoder = fitted_preprocessor.named_transformers_['cat']
    encoded_cat_names = list(cat_encoder.get_feature_names_out(categorical_features))
    all_feature_names = encoded_cat_names + numerical_features

    if hasattr(fitted_regressor, 'feature_importances_'):
        importances = fitted_regressor.feature_importances_
        feat_df = pd.DataFrame({
            'Feature': all_feature_names,
            'Importance': importances
        }).sort_values(by='Importance', ascending=False)
        feature_importances = feat_df.head(10).to_dict(orient='records')
        print("\nTop 5 Most Important Features:")
        for row in feature_importances[:5]:
            print(f" - {row['Feature']}: {row['Importance']*100:.2f}%")

    # Save metadata JSON for Flask templates
    metadata = {
        'best_model': best_model_name,
        'r2_score': round(float(best_r2), 4),
        'accuracy_percent': round(float(best_r2 * 100), 2),
        'rmse': round(float(best_rmse), 2),
        'mae': round(float(best_mae), 2),
        'dataset_size': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'models_comparison': results_df.to_dict(orient='records'),
        'top_features': feature_importances
    }
    with open("model/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)
    print("✅ Model metadata saved to 'model/model_metadata.json'")

    # 11. Generate Evaluation Graphs for Presentation & Web UI
    os.makedirs("static/graphs", exist_ok=True)
    generate_visualizations(df, y_test, test_predictions, best_model_name, results_df, all_feature_names, fitted_regressor)

    print("\n🎉 Training workflow completed successfully!")


def generate_visualizations(df, y_test, test_predictions, best_model_name, results_df, all_feature_names, regressor):
    """Generates 5 informative charts saved to static/graphs/."""
    print("\nGenerating model evaluation plots in 'static/graphs/'...")

    # Graph 1: Actual vs Predicted Rent (Best Model)
    plt.figure(figsize=(8, 6))
    y_pred_best = test_predictions[best_model_name]
    plt.scatter(y_test, y_pred_best, alpha=0.6, color='#2563eb', edgecolors='k', s=45)
    # Perfect fit line
    min_val = min(y_test.min(), y_pred_best.min())
    max_val = max(y_test.max(), y_pred_best.max())
    plt.plot([min_val, max_val], [min_val, max_val], color='#dc2626', linestyle='--', linewidth=2.5, label='Perfect Prediction')
    plt.title(f'Actual vs Predicted Rent ({best_model_name})', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Actual Monthly Rent (BDT ৳)', fontsize=12)
    plt.ylabel('Predicted Monthly Rent (BDT ৳)', fontsize=12)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.savefig('static/graphs/actual_vs_predicted.png', dpi=200, bbox_inches='tight')
    plt.close()

    # Graph 2: Feature Importance Bar Chart
    if hasattr(regressor, 'feature_importances_'):
        plt.figure(figsize=(9, 6))
        importances = regressor.feature_importances_
        feat_df = pd.DataFrame({'Feature': all_feature_names, 'Importance': importances})
        top_feats = feat_df.sort_values(by='Importance', ascending=True).tail(10)
        
        # Clean feature names for presentation
        clean_names = [f.replace('location_', 'Loc: ').replace('property_type_', 'Type: ').replace('furnished_', 'Furnished: ') for f in top_feats['Feature']]
        
        bars = plt.barh(clean_names, top_feats['Importance'], color='#0d9488', edgecolor='black', alpha=0.85)
        plt.title('Top 10 Feature Importances (Random Forest / Tree)', fontsize=14, fontweight='bold', pad=12)
        plt.xlabel('Relative Importance Score', fontsize=12)
        plt.grid(axis='x', linestyle=':', alpha=0.6)
        plt.savefig('static/graphs/feature_importance.png', dpi=200, bbox_inches='tight')
        plt.close()

    # Graph 3: Rent Distribution
    plt.figure(figsize=(8, 5.5))
    sns.histplot(df['monthly_rent'], kde=True, color='#4f46e5', bins=28, edgecolor='black', alpha=0.65)
    plt.title('Monthly Rent Distribution in Mymensingh (Dataset)', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Monthly Rent (BDT ৳)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.savefig('static/graphs/rent_distribution.png', dpi=200, bbox_inches='tight')
    plt.close()

    # Graph 4: Correlation Heatmap
    plt.figure(figsize=(8, 6.5))
    num_cols = ['bedrooms', 'bathrooms', 'house_size', 'floor', 'total_floors', 'age', 'monthly_rent']
    corr = df[num_cols].corr()
    sns.heatmap(corr, annot=True, cmap='Blues', fmt='.2f', linewidths=1, linecolor='white', cbar_kws={'label': 'Correlation Coefficient'})
    plt.title('Numerical Features Correlation Heatmap', fontsize=14, fontweight='bold', pad=12)
    plt.savefig('static/graphs/correlation_heatmap.png', dpi=200, bbox_inches='tight')
    plt.close()

    # Graph 5: Model Comparison Chart (R² Score & RMSE)
    fig, ax1 = plt.subplots(figsize=(9, 5.5))

    x = np.arange(len(results_df))
    width = 0.38

    ax1.set_xlabel('Regression Algorithms', fontsize=12, fontweight='bold')
    ax1.set_ylabel('R² Score (Higher is better)', color='#2563eb', fontsize=12)
    rects1 = ax1.bar(x - width/2, results_df['R2'], width, label='R² Score', color='#3b82f6', edgecolor='black')
    ax1.tick_params(axis='y', labelcolor='#2563eb')
    ax1.set_ylim([0, 1.05])

    ax2 = ax1.twinx()
    ax2.set_ylabel('RMSE in BDT ৳ (Lower is better)', color='#dc2626', fontsize=12)
    rects2 = ax2.bar(x + width/2, results_df['RMSE'], width, label='RMSE (৳)', color='#ef4444', edgecolor='black', alpha=0.85)
    ax2.tick_params(axis='y', labelcolor='#dc2626')

    ax1.set_xticks(x)
    ax1.set_xticklabels(results_df['Model'], rotation=15, ha='right', fontsize=10)
    plt.title('Model Performance Comparison (R² Score vs RMSE)', fontsize=14, fontweight='bold', pad=12)

    plt.savefig('static/graphs/model_comparison.png', dpi=200, bbox_inches='tight')
    plt.close()

    print("✅ All 5 evaluation graphs saved in 'static/graphs/'")


if __name__ == "__main__":
    train_and_evaluate_models()

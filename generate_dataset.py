"""
=============================================================================
Home Rent Prediction System - Dataset Generator (Mymensingh, Bangladesh)
=============================================================================
This script generates a realistic synthetic dataset for rental housing
across different prominent areas in Mymensingh, Bangladesh.

The dataset includes realistic correlations:
- Prime locations (Kachijhuli, Charpara, Town Hall, Ganginar Par) have higher base rates per sqft
- Proximity to Mymensingh Medical College Hospital (Charpara) and Bangladesh Agricultural University (Kewatkhali)
- Size (sqft), bedrooms, and bathrooms scale logically
- Furnishing, parking, and balcony add realistic premiums
- Floor level impacts price (middle floors preferred over ground/top floors)
- House age slightly depreciates rent
=============================================================================
"""

import sys
import os
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Set fixed random seed for reproducibility
np.random.seed(42)

def generate_house_rent_dataset(num_samples: int = 1600, output_path: str = "data/house_rent.csv"):
    """Generates synthetic Mymensingh home rent dataset and saves to CSV."""
    
    # Location configurations with base price per sqft (in BDT) for Mymensingh
    locations_config = {
        'Kachijhuli': {'base_rate': 19.0, 'prob': 0.12},
        'Charpara': {'base_rate': 18.5, 'prob': 0.16},
        'Town Hall': {'base_rate': 17.5, 'prob': 0.12},
        'Ganginar Par': {'base_rate': 16.5, 'prob': 0.10},
        'Notun Bazar': {'base_rate': 15.5, 'prob': 0.08},
        'Shehora': {'base_rate': 14.5, 'prob': 0.10},
        'Panditpara': {'base_rate': 14.0, 'prob': 0.06},
        'Sankipara': {'base_rate': 14.0, 'prob': 0.08},
        'Choto Bazar': {'base_rate': 13.5, 'prob': 0.04},
        'Maskanda': {'base_rate': 13.0, 'prob': 0.06},
        'Akua': {'base_rate': 12.5, 'prob': 0.05},
        'Kewatkhali': {'base_rate': 12.0, 'prob': 0.03}
    }
    
    locations = list(locations_config.keys())
    location_probs = [locations_config[loc]['prob'] for loc in locations]
    
    # Property types
    property_types = ['Apartment', 'House', 'Duplex', 'Studio']
    prop_type_probs = [0.72, 0.13, 0.08, 0.07]
    
    data = []
    
    for _ in range(num_samples):
        # 1. Location selection
        location = np.random.choice(locations, p=location_probs)
        base_rate = locations_config[location]['base_rate']
        
        # 2. Property Type
        prop_type = np.random.choice(property_types, p=prop_type_probs)
        
        # 3. Size, Bedrooms, Bathrooms based on Property Type
        if prop_type == 'Studio':
            house_size = int(np.random.normal(450, 80))
            house_size = max(250, min(650, house_size))
            bedrooms = 1
            bathrooms = 1
            balcony = np.random.choice(['Yes', 'No'], p=[0.4, 0.6])
        elif prop_type == 'Duplex':
            house_size = int(np.random.normal(2400, 400))
            house_size = max(1800, min(3800, house_size))
            bedrooms = np.random.choice([4, 5, 6], p=[0.4, 0.4, 0.2])
            bathrooms = bedrooms + np.random.choice([0, 1], p=[0.6, 0.4])
            balcony = 'Yes'
        elif prop_type == 'House':
            house_size = int(np.random.normal(1600, 350))
            house_size = max(900, min(2800, house_size))
            bedrooms = np.random.choice([3, 4, 5], p=[0.5, 0.35, 0.15])
            bathrooms = max(2, bedrooms - np.random.choice([0, 1], p=[0.7, 0.3]))
            balcony = np.random.choice(['Yes', 'No'], p=[0.8, 0.2])
        else: # Apartment
            house_size = int(np.random.normal(1200, 300))
            house_size = max(500, min(2400, house_size))
            if house_size < 800:
                bedrooms = np.random.choice([1, 2], p=[0.3, 0.7])
                bathrooms = 1
            elif house_size < 1400:
                bedrooms = np.random.choice([2, 3], p=[0.3, 0.7])
                bathrooms = np.random.choice([2, 3], p=[0.7, 0.3])
            else:
                bedrooms = np.random.choice([3, 4], p=[0.6, 0.4])
                bathrooms = np.random.choice([3, 4], p=[0.7, 0.3])
            balcony = np.random.choice(['Yes', 'No'], p=[0.85, 0.15])
            
        # 4. Floors
        total_floors = int(np.random.choice([4, 5, 6, 7, 8, 9, 10, 12, 14, 16], 
                                           p=[0.1, 0.15, 0.2, 0.15, 0.15, 0.1, 0.05, 0.05, 0.03, 0.02]))
        floor = int(np.random.randint(1, total_floors + 1))
        
        # 5. Amenities
        furnished = np.random.choice(['Yes', 'No'], p=[0.25, 0.75])
        parking = np.random.choice(['Yes', 'No'], p=[0.60 if house_size > 1000 else 0.25, 
                                                     0.40 if house_size > 1000 else 0.75])
        
        # 6. Age of building (years)
        age = int(np.random.exponential(scale=6))
        age = min(30, max(0, age))
        
        # 7. Rent Calculation Model with realistic domain rules
        rent = house_size * base_rate
        
        # Property type multiplier
        if prop_type == 'Duplex':
            rent *= 1.15
        elif prop_type == 'Studio':
            rent *= 1.10
        elif prop_type == 'House':
            rent *= 1.05
            
        # Bedroom & Bathroom adjustments
        rent += (bedrooms * 1500)
        rent += (bathrooms * 1000)
        
        # Furnishing bonus
        if furnished == 'Yes':
            rent += (house_size * 6.5) + 3000
            
        # Parking bonus
        if parking == 'Yes':
            rent += 3000
            
        # Balcony bonus
        if balcony == 'Yes':
            rent += 1200
            
        # Floor preference (2nd to 6th floor preferred over ground floor or very top floor)
        if floor == 1:
            rent *= 0.95
        elif 2 <= floor <= 6:
            rent *= 1.03
        elif floor == total_floors:
            rent *= 0.96
            
        # Age depreciation (about 0.7% per year of age up to 15%)
        depreciation = min(0.18, age * 0.007)
        rent *= (1.0 - depreciation)
        
        # Add realistic market variance / random noise (approx +- 6%)
        noise = np.random.normal(1.0, 0.05)
        rent = rent * noise
        
        # Round rent to nearest 500 BDT for realistic listing prices
        rent = int(round(rent / 500.0) * 500)
        rent = max(4000, rent) # minimum floor (affordable studios/bachelor units)
        
        data.append({
            'location': location,
            'property_type': prop_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'house_size': house_size,
            'floor': floor,
            'total_floors': total_floors,
            'furnished': furnished,
            'parking': parking,
            'balcony': balcony,
            'age': age,
            'monthly_rent': rent
        })
        
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Generated {len(df)} records saved successfully to '{output_path}'")
    print("\nSample Data (First 5 records):")
    print(df.head())
    print("\nDataset Summary Statistics:")
    print(df.describe())
    return df

if __name__ == "__main__":
    generate_house_rent_dataset()

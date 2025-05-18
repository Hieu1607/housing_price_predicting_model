# Vietnam Housing Price Prediction Model

This project contains a machine learning model for predicting housing prices in Vietnam based on various features such as area, location, number of bedrooms, etc.

## Dataset

The dataset (vietnam_housing_dataset.csv) contains housing data with the following features:
- Address: The complete address of the property
- Area: The total area of the property in square meters
- Frontage: The width of the front side of the property in meters
- Access Road: The width of the road providing access to the property in meters
- House Direction: The cardinal direction the front of the house is facing
- Balcony Direction: The cardinal direction the balcony is facing
- Floors: The total number of floors in the property
- Bedrooms: The number of bedrooms in the property
- Bathrooms: The number of bathrooms in the property
- Legal Status: Indicates the legal status of the property
- Furniture State: Indicates the state of furnishing in the property
- Price: The price of the property in billions of Vietnamese Dong (VND)

## Setup Instructions

### Prerequisites
- Python 3.10 (recommended for TensorFlow compatibility)
- pip (Python package installer)

### Setting Up Virtual Environment

1. Open a terminal or command prompt
2. Navigate to the project directory:
   ```
   cd "C:\Users\Admin\Desktop\housing_price_predicting_model"
   ```

3. Create a virtual environment with Python 3.10:
   ```
   python -m venv venv --python=3.10
   ```

4. Activate the virtual environment:
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

5. Install required packages with specific versions to avoid compatibility issues:
   ```
   pip install pandas==1.5.3 numpy==1.22.4 matplotlib==3.7.1 seaborn==0.12.2 scikit-learn==1.2.2 xgboost==1.7.5 scipy==1.10.1 jupyter
   ```
   
### Running the Project

1. Make sure your virtual environment is activated (you should see "(venv)" at the beginning of your command prompt)

2. Launch Jupyter Notebook:
   ```
   jupyter notebook
   ```

3. In the browser window that opens, click on "model.ipynb" to open the notebook

4. You can run each cell in the notebook by clicking the cell and pressing Shift+Enter or by using the Run button in the toolbar

### Model Overview

This project implements and compares several regression models:
- Linear Regression (Simple, Ridge, Lasso)
- Decision Tree models (Decision Tree, Random Forest, XGBoost)
- K-Nearest Neighbors Regression
- Neural Network

Each model is evaluated using cross-validation with the following metrics:
- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)
- R² Score
- Training Time

## Implementation Notes

### Random Forest and XGBoost
For these models, we use cross_validate instead of cross_val_predict to get proper evaluation metrics. This avoids redundant training and ensures accurate measurement of performance. The RandomizedSearchCV is used to find the optimal hyperparameters.

### Neural Network
For the Neural Network implementation, make sure you have the appropriate deep learning library installed. If using TensorFlow, include it in the package installation:
```
pip install tensorflow==2.12.0
```

## Deactivating the Virtual Environment

When you're done working with the project, you can deactivate the virtual environment by running:
```
deactivate
```

## Notes

- The notebook contains data preprocessing steps including handling missing values, outlier removal, and feature engineering.
- The models are optimized using either GridSearchCV or RandomizedSearchCV to find the best hyperparameters.
- For the best performance, make sure the CSV data file is in the same directory as the notebook.
- If you encounter memory issues with large models like XGBoost, consider reducing the parameter search space or using fewer estimators.

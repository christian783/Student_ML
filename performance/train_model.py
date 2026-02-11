import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score

def train():
    print("Loading dataset...")
    df = pd.read_csv('dataset.csv')

    # Preprocessing
    print("Preprocessing data...")
    le = LabelEncoder()
    df['extracurricular'] = le.fit_transform(df['extracurricular'])

    X = df.drop('Performance Index', axis=1)
    y = df['Performance Index']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model Selection: Gradient Boosting Regressor
    # Why? It often provides better predictive accuracy than Random Forest by optimizing the loss function sequentially.
    gb_reg = GradientBoostingRegressor(random_state=42)

    # Hyperparameter Tuning
    print("Starting Hyperparameter Tuning (this may take a moment)...")
    param_dist = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'max_depth': [3, 4, 5],
        'min_samples_split': [2, 5, 10],
        'subsample': [0.8, 0.9, 1.0]
    }

    random_search = RandomizedSearchCV(
        estimator=gb_reg,
        param_distributions=param_dist,
        n_iter=10,  # Number of parameter settings that are sampled
        cv=3,       # 3-fold cross-validation
        n_jobs=-1,  # Use all available cores
        verbose=1,
        random_state=42,
        scoring='r2'
    )

    random_search.fit(X_train, y_train)

    best_model = random_search.best_estimator_
    print(f"Best Parameters found: {random_search.best_params_}")

    # Evaluation
    print("Evaluating model...")
    y_pred = best_model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\nModel Performance Metrics:")
    print(f"--------------------------")
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    print(f"--------------------------")

    # Save the best model
    joblib.dump(best_model, 'performance/model.pkl')
    print("Best model trained and saved to performance/model.pkl")

if __name__ == "__main__":
    train()
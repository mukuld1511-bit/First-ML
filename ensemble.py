import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load Dataset
# -------------------------------
df = pd.read_csv("data/house_prices.csv")

X = df.drop("SalePrice", axis=1)
y = df["SalePrice"]

# Train-Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Models
# -------------------------------
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(max_depth=20, random_state=50),
    "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=20, random_state=50),
    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=3,
        random_state=50
    )
}

# Store predictions
all_predictions = []

print("=" * 60)

for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    all_predictions.append(predictions)

    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print(f"{name}")
    print(f"MSE : {mse:.2f}")
    print(f"R2  : {r2:.4f}")
    print("-" * 60)

# Ensemble Average Prediction
# -------------------------------
ensemble_prediction = np.mean(all_predictions, axis=0)

ensemble_mse = mean_squared_error(y_test, ensemble_prediction)
ensemble_r2 = r2_score(y_test, ensemble_prediction)

print("\n========== Final Ensemble (Average) ==========")
print(f"MSE : {ensemble_mse:.2f}")
print(f"R2  : {ensemble_r2:.4f}")

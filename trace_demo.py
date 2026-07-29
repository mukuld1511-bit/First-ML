import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

# Load dataset
df = pd.read_csv("data/house_prices.csv")
X = df.drop("SalePrice", axis=1)
y = df["SalePrice"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Enable automatic MLflow Tracing / Logging
mlflow.autolog()

mlflow.set_experiment("House Price Prediction Tracing")

with mlflow.start_run() as run:
    # Custom tracing span using mlflow.trace
    @mlflow.trace(name="train_house_price_model")
    def train_pipeline(estimators, depth):
        model = RandomForestRegressor(n_estimators=estimators, max_depth=depth, random_state=42)
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        return {"r2_score": score, "model": model}

    result = train_pipeline(estimators=100, depth=15)
    print(f"Tracing completed! Model R2 score: {result['r2_score']:.4f}")

#Home price to predict .

------------------
Train a simple ML model

Track metrics

Save model

Serve locally

End to end Deployment


1. Create Virtual Environment

##python3.11

  python3.11 -m venv /home/hadoop/venv-mlflow
  
  source /home/hadoop/venv-mlflow/bin/activate
  
  deactivate

2. Install Required Packages

  pip install -r requirements.txt
  
  mlflow --version
  
    >mlflow, version 3.11.0

3. Create Project Structure

mlflow-homePrice/
│
├── data/
│   └── house_prices.csv
│
├── train.py
├── predict.py
├── requirements.txt
│
└── mlruns/

4. Default sqlite      sqlite:///mlflow.db   

#Local
 /home/hadoop/workspace/mlflow-homePrice$  mlflow ui      
 
  http://127.0.0.1:5000
  
  Parameters
  Metrics
  Models
  Artifacts
  Experiment history
 
- OR

#production
>mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --default-artifact-root ./mlruns
  
 http://127.0.0.1:5000
 

5. Training Script  train.py

(venv-mlflow) /home/hadoop/workspace/mlflow-homePrice $python train.py

change in train.py 
n_estimators = 50
n_estimators = 100
n_estimators = 200



6. Inside MLflow UI:
Open experiment
Open run
Copy artifact path

OR ---------------------

7. Model Deployment Directly 
- 
#Open another cmd/Terminal

  run_id: 0724aded5f00431592973ca08e5796d9  
  
  --Get this value from /home/hadoop/workspace/mlflow-homePrice/mlruns/1/models/m-5bafd1af7f574fcab291bd157d1a29bc/artifacts/MLmodel
  cat MLmodel
 
/home/hadoop/workspace/mlflow-homePrice> mlflow models serve -m ./mlruns/1/models/m-b7aab1b135cf466c942b10dc3e7b7ad2/artifacts -p 1234 --no-conda

http://127.0.0.1:1234

#test
curl -X POST http://127.0.0.1:1234/invocations \
-H "Content-Type: application/json" \
-d '{
  "dataframe_records": [
    {
      "LotArea":9000,
      "OverallQual":7,
      "OverallCond":5,
      "YearBuilt":2010,
      "GrLivArea":1900,
      "GarageCars":2
    }
  ]
}'


8. Test deployed model 

python predict.py

9. Deploy 
--make Dockefile -- check models in Dockerfile

docker build -t house-price:v1 .

docker run -d \
-p 1235:1234 \
--name house-api \
house-price:v1

docker images

http://127.0.0.1:1235

#test inside container
curl -X POST http://localhost:1234/invocations \
-H "Content-Type: application/json" \
-d '{
"dataframe_records":[
{
"LotArea":9000,
"OverallQual":7,
"OverallCond":5,
"YearBuilt":2010,
"GrLivArea":1900,
"GarageCars":2
}
]
}'

#push image  change Docker ID
docker tag house-price:v1 mukuld1511/house-price:v1

docker push mukuld1511/house-price:v1


#k8-------------
kind create cluster --config kind-config.yml
kind get clusters

-- Load Image in kind
kind load docker-image house-price:v1


kubectl apply -f deployment.yml
kubectl get pods

kubectl apply -f service.yml
kubectl get svc

kubectl port-forward service/house-price-service 8080:80

-- 
kubectl delete -f deployment.yml 
kubectl describe pod house-price-c74455855-28rbm

-- test pod deployment
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{
  "dataframe_records":[
    {
      "LotArea":9000,
      "OverallQual":7,
      "OverallCond":5,
      "YearBuilt":2010,
      "GrLivArea":1900,
      "GarageCars":2
    }
  ]
}'


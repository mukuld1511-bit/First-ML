#method 1

Download and install jenkins

OR

docker run -d \
  --name jen-mvn \
  --user root \
  -p 8081:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/mukul/projects/mlops/First-ML:/workspace/mlflow-homePrice \
  jenkins/jenkins

 
#url
http://0.0.0.0:8081/

#inside container
apt-get update
apt-get install -y python3-pip
apt install python3.13-venv

sudo apt update  
apt-get install -y docker.io



#method2 custom 

docker build -t jenkins-maven-docker .

docker run -d \
  --name jen-mvn \
  --user root \
  -p 8081:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/mukul/projects/mlops/First-ML:/workspace/mlflow-homePrice \
  jenkins-maven-docker






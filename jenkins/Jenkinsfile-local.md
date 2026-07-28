pipeline {
    agent any

    parameters {
        choice(
            name: 'MODEL_SOURCE',
            choices: ['latest', 'manual'],
            description: 'latest = auto-pick newest MLflow model dir after training. manual = build from a specific model ID you already have.'
        )
        string(
            name: 'MODEL_ID',
            defaultValue: '',
            description: 'Only used when MODEL_SOURCE=manual. Paste the m-<hash> folder name from mlruns/<exp>/models/'
        )
        booleanParam(
            name: 'TRAIN_MODEL',
            defaultValue: true,
            description: 'Run train.py before selecting a model. Turn off to just rebuild the container from an already-trained model.'
        )
    }

    environment {
        // Path INSIDE the jen-mvn container, from: -v /home/mukul/projects/mlops/First-ML:/workspace/mlflow-homePrice
        PROJECT_DIR    = "/workspace/mlflow-homePrice"
        EXPERIMENT_ID  = "1"
        IMAGE_NAME     = "house-price"
        CONTAINER_NAME = "house-api"
    }

    stages {

        stage('Verify Project') {
            steps {
                dir("${PROJECT_DIR}") {
                    sh '''
                    pwd
                    ls -la
                    '''
                }
            }
        }

        stage('Debug') {
            steps {
                sh '''
                whoami
                echo "PATH=$PATH"
                which python3 || echo "python3 still not found - update PATH above"
                python3 --version || true
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                dir("${PROJECT_DIR}") {
                    sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Train Model') {
            when { expression { return params.TRAIN_MODEL } }
            steps {
                dir("${PROJECT_DIR}") {
                    sh '''
                    . venv/bin/activate
                    python3 train.py
                    '''
                }
            }
        }

        stage('Select Model') {
            steps {
                dir("${PROJECT_DIR}") {
                    script {
                        if (params.MODEL_SOURCE == 'manual') {
                            if (!params.MODEL_ID?.trim()) {
                                error "MODEL_SOURCE=manual but MODEL_ID was not provided."
                            }
                            env.SELECTED_MODEL_ID = params.MODEL_ID.trim()
                        } else {
                            env.SELECTED_MODEL_ID = sh(
                                script: """
                                    ls -td mlruns/${EXPERIMENT_ID}/models/*/ \
                                      | head -n 1 \
                                      | xargs -n1 basename
                                """,
                                returnStdout: true
                            ).trim()
                        }

                        env.MODEL_DIR = "mlruns/${EXPERIMENT_ID}/models/${env.SELECTED_MODEL_ID}/artifacts"

                        sh """
                        echo "Selected model: ${env.SELECTED_MODEL_ID}"
                        test -f "${env.MODEL_DIR}/model.pkl" || { echo "model.pkl not found in ${env.MODEL_DIR}"; exit 1; }
                        ls -la "${env.MODEL_DIR}"
                        """

                        // Tag the image with the model id so it's traceable to the exact training run
                        env.IMAGE_TAG = "${env.SELECTED_MODEL_ID}-${env.BUILD_NUMBER}"
                    }
                }
            }
        }

        stage('Stage Model into Build Context') {
            steps {
                dir("${PROJECT_DIR}") {
                    sh '''
                    mkdir -p model_artifact
                    rm -f model_artifact/*
                    cp "${MODEL_DIR}/model.pkl" model_artifact/model.pkl
                    # copy along conda/env metadata too, in case the app or Dockerfile wants it
                    cp "${MODEL_DIR}/MLmodel" model_artifact/ 2>/dev/null || true
                    cp "${MODEL_DIR}/python_env.yaml" model_artifact/ 2>/dev/null || true
                    '''
                }
                // NOTE: your Dockerfile must COPY model_artifact/model.pkl into the image
                // (e.g. `COPY model_artifact/model.pkl /app/model.pkl`) so each build picks up
                // whatever is staged here.
            }
        }

        stage('Build Docker Image') {
            steps {
                dir("${PROJECT_DIR}") {
                    sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker rm -f ${CONTAINER_NAME} || true

                docker run -d \
                  --name ${CONTAINER_NAME} \
                  -p 8080:1234 \
                  --label model_id=${SELECTED_MODEL_ID} \
                  ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }
    }

    post {
        success {
            echo "Deployed ${IMAGE_NAME}:${IMAGE_TAG} (model ${SELECTED_MODEL_ID}) as container ${CONTAINER_NAME}"
        }
        failure {
            echo "Pipeline failed - container ${CONTAINER_NAME} left untouched (not swapped)."
        }
    }
}

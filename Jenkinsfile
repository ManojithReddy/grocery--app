pipeline {
    agent any

    environment {
        AWS_REGION  = 'us-east-2'
        ECR_REPO    = '068889455146.dkr.ecr.us-east-2.amazonaws.com/grocery-app'
        ECS_CLUSTER = 'grocery-app-cluster'
        ECS_SERVICE = 'grocery-app'
        TASK_FAMILY = 'grocery-app'
        // Help Jenkins on a Mac find docker, aws and the docker login helper
        PATH = "/opt/homebrew/bin:/usr/local/bin:/Applications/Docker.app/Contents/Resources/bin:${env.PATH}"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.IMAGE     = "${env.ECR_REPO}:${env.IMAGE_TAG}"
                }
                echo "Building image ${env.IMAGE}"
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build --platform linux/amd64 -t $IMAGE .'
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                  aws ecr get-login-password --region $AWS_REGION | \
                    docker login --username AWS --password-stdin ${ECR_REPO%/*}
                  docker push $IMAGE
                '''
            }
        }

        stage('Deploy to ECS') {
            steps {
                sh '''
                  # 1. Get the current recipe card
                  aws ecs describe-task-definition --task-definition $TASK_FAMILY \
                    --region $AWS_REGION --query taskDefinition > current.json

                  # 2. Put the new lunchbox on it, and remove fields AWS won't accept back
                  jq --arg IMG "$IMAGE" '.containerDefinitions[0].image = $IMG
                     | del(.taskDefinitionArn, .revision, .status, .requiresAttributes,
                           .compatibilities, .registeredAt, .registeredBy)' \
                     current.json > new.json

                  # 3. Save it as a new recipe card (new revision)
                  NEW_ARN=$(aws ecs register-task-definition --cli-input-json file://new.json \
                    --region $AWS_REGION --query taskDefinition.taskDefinitionArn --output text)
                  echo "New task definition: $NEW_ARN"

                  # 4. Give the new card to the shop manager (starts the rolling update)
                  aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE \
                    --task-definition $NEW_ARN --region $AWS_REGION --query service.serviceName

                  # 5. Wait until the new counter is healthy
                  aws ecs wait services-stable --cluster $ECS_CLUSTER --services $ECS_SERVICE \
                    --region $AWS_REGION
                '''
            }
        }
    }

    post {
        success { echo "Deployed ${env.IMAGE} to ECS Fargate!" }
        failure { echo 'Deploy failed - check the console log, ECS service events and CloudWatch logs' }
        always  { cleanWs() }
    }
}

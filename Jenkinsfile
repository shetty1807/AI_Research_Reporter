pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Code checked out successfully'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t ai-devops-analyzer .'
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker rm -f ai-devops-container || exit 0'
                bat 'docker run -d -p 8501:8501 --name ai-devops-container ai-devops-analyzer'
            }
        }
    }

    post {
        success {
            echo 'Deployment completed successfully'
        }
        failure {
            echo 'Pipeline failed. Check console output.'
        }
    }
}
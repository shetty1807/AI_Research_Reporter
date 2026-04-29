pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking code from GitHub...'
            }
        }

        stage('Test') {
            steps {
                bat 'python --version'
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t ai-research-reporter .'
            }
        }

        stage('Deploy Container') {
            steps {
                bat 'docker rm -f ai-research-container || exit 0'
                bat 'docker run -d -p 8501:8501 --name ai-research-container ai-research-reporter'
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check console logs.'
        }
    }
}
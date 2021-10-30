pipeline {
    agent any

    stages {
        stage('build from Dockerfile') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
         stage('run') {
            steps {
                sh 'docker-compose up --abort-on-container-exit'
            }
        }
    }
}
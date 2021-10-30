pipeline {
    agent any

    stages {
        stage('build myapp from Dockerfile') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }
         stage('local opencart configure') {
            steps {
                sh """
				    OPENCART_HOST=`hostname -I | awk '{print $1}'`
				    docker-compose up
                """
            }
        }
         stage('run') {
            steps {
                sh 'docker-compose up --abort-on-container-exit'
            }
        }
    }
}
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
                HOST_IP=`hostname -I | awk '{print \$1}'`
                docker-compose up -d
                """
            }
        }
         stage('run myapp') {
            steps {
                sh 'docker run --env EXECUTOR_IP=192.168.17.2 --env OPENCART_HOST=192.168.17.9 --env OPENCART_PORT=80 myapp:latest tests/test_admin_page.py::test_admin_page -v --selenoid_run --bversion 92.0 --browser chrome'
            }
        }
    }
    post {
        always {
            sh 'docker-compose down -v'
        }
    }
}
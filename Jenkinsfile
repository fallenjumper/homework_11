pipeline {
    agent any

    stages {
        stage('build myapp from Dockerfile') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }

        stage('Configure environment') {
             steps {
                       sh """
                          if [ $OPENCART_HOST = "local" ]; then
                            export HOST_IP=`hostname -I | awk '{print \$1}'`
                            docker-compose up -d
                           fi
                       """
             }
        }
        stage('run myapp') {
             steps {
                    sh """
                       if [ $OPENCART_HOST = "local" ]; then
                            docker run --env EXECUTOR_IP=$EXECUTOR_IP --env OPENCART_HOST=`hostname -I | awk '{print \$1}'` --env OPENCART_PORT=$OPENCART_PORT myapp:latest -n $THREADS -v --selenoid_run --bversion $BROWSER_VERSION --browser $BROWSER
                       else
                            docker run --env EXECUTOR_IP=$EXECUTOR_IP --env OPENCART_HOST=$OPENCART_HOST --env OPENCART_PORT=$OPENCART_PORT myapp:latest -n $THREADS -v --selenoid_run --bversion $BROWSER_VERSION --browser $BROWSER
                       fi
                     """
             }
        }

        stage('generate allure report') {
            steps {
                script {
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'allure-results']]
                    ])
                }
            }
        }
    }
    post {
        always {
            sh 'docker-compose down -v'
        }
    }
}

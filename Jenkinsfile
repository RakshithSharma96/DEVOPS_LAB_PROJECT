// CLI commands work on a Windows agent (bat) or Linux/container agent (sh).
def dockerCommand(String command, boolean statusOnly = false) {
    if (isUnix()) {
        return sh(script: command, returnStatus: statusOnly)
    }
    return bat(script: command, returnStatus: statusOnly)
}

pipeline {
    agent any
    options {
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }
    parameters {
        string(name: 'LOCAL_PROJECT_PATH', defaultValue: '',
               description: 'No Git? Absolute source folder visible to this Jenkins agent. Leave blank for SCM/workspace.')
    }
    stages {
        stage('Source') {
            steps {
                script {
                    if (params.LOCAL_PROJECT_PATH?.trim()) {
                        withEnv(["LOCAL_SOURCE=${params.LOCAL_PROJECT_PATH.trim()}"]) {
                            if (isUnix()) {
                                sh '''
                                    set -eu
                                    cp -R -- "$LOCAL_SOURCE/app" "$LOCAL_SOURCE/tests" .
                                    cp -- "$LOCAL_SOURCE/requirements.txt" "$LOCAL_SOURCE/Dockerfile" "$LOCAL_SOURCE/docker-compose.yml" .
                                '''
                            } else {
                                bat '''powershell -NoProfile -NonInteractive -Command "$ErrorActionPreference = 'Stop'; foreach ($item in @('app','tests','requirements.txt','Dockerfile','docker-compose.yml')) { Copy-Item -LiteralPath (Join-Path $env:LOCAL_SOURCE $item) -Destination $env:WORKSPACE -Recurse -Force }"'''
                            }
                        }
                    }
                    // Declarative Pipeline checks out configured SCM automatically.
                    // Script-only jobs instead copy local source or reuse the workspace.
                    if (!fileExists('docker-compose.yml')) {
                        error('Source missing. Configure SCM or set LOCAL_PROJECT_PATH to the project folder.')
                    }
                    // Isolate CI containers from the manually started demonstration.
                    env.COMPOSE_PROJECT_NAME = "login-ci-${env.JOB_NAME}-${env.BUILD_NUMBER}".toLowerCase().replaceAll('[^a-z0-9-]', '-')
                    env.TEST_CONTAINER = "${env.COMPOSE_PROJECT_NAME}-tests"
                    env.APP_PORT = '0'
                    // Remove old report files so they can never appear as this build's results.
                    dir('reports') { deleteDir() }
                    dockerCommand('docker version')
                    dockerCommand('docker compose version')
                }
            }
        }
        stage('Build image') {
            steps { script { dockerCommand('docker compose build app') } }
        }
        stage('Start and wait') {
            steps {
                script {
                    dockerCommand('docker compose up -d --wait --wait-timeout 180 app selenium')
                }
            }
        }
        stage('Selenium tests') {
            steps {
                script {
                    // Keep the stopped runner until post copies its report, even on failure.
                    dockerCommand("docker compose run --no-deps --name ${env.TEST_CONTAINER} tests")
                }
            }
        }
    }
    post {
        always {
            script {
                try {
                    if (env.TEST_CONTAINER) {
                        dockerCommand("docker cp ${env.TEST_CONTAINER}:/project/reports .", true)
                    }
                    if (fileExists('reports/results.xml')) {
                        junit 'reports/results.xml'
                    }
                    archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
                } finally {
                    if (env.COMPOSE_PROJECT_NAME) {
                        dockerCommand('docker compose logs --no-color app selenium', true)
                        if (env.TEST_CONTAINER) {
                            dockerCommand("docker rm -f ${env.TEST_CONTAINER}", true)
                        }
                        def cleanupStatus = dockerCommand('docker compose --profile testing down --remove-orphans', true)
                        if (cleanupStatus != 0) {
                            error('Container cleanup failed; inspect Console Output and run Compose down manually.')
                        }
                    }
                }
            }
        }
        success { echo 'SUCCESS: all login tests passed.' }
        failure { echo 'FAILURE: inspect Console Output and the test report.' }
    }
}

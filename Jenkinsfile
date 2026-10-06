pipeline {
    agent any

    environment {
        // =====================================================
        // APPLICATION
        // =====================================================
        APP_NAME = 'inventory-api'
        IMAGE_NAME = 'inventory-api'
        VERSION = "1.0.${BUILD_NUMBER}"

        // =====================================================
        // CONTAINERS
        // =====================================================
        STAGING_CONTAINER = 'inventory-api-staging'
        PRODUCTION_CONTAINER = 'inventory-api-production'

        // =====================================================
        // PORTS
        // =====================================================
        STAGING_PORT = '8001'
        PRODUCTION_PORT = '8000'

        // =====================================================
        // JENKINS PATH
        // Docker is installed at /Users/rickyrenado/.docker/bin/docker
        // =====================================================
        PATH = "/Users/rickyrenado/.docker/bin:/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.14/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
    }

    stages {

        // =====================================================
        // STAGE 1 - BUILD
        // =====================================================
        stage('Build') {
            steps {

                echo '=========================================='
                echo 'STAGE 1: BUILD'
                echo '=========================================='

                sh '''
                    set -e

                    echo "===== ENVIRONMENT ====="

                    echo "PATH:"
                    echo "$PATH"

                    echo ""
                    echo "Docker location:"
                    which docker

                    echo ""
                    echo "Docker version:"
                    docker --version

                    echo ""
                    echo "Python location:"
                    which python3

                    echo ""
                    echo "Python version:"
                    python3 --version

                    echo ""
                    echo "Pip version:"
                    python3 -m pip --version

                    echo ""
                    echo "===== INSTALL DEPENDENCIES ====="

                    python3 -m pip install -r requirements.txt

                    echo ""
                    echo "===== BUILD DOCKER IMAGE ====="

                    docker build \
                        -t ${IMAGE_NAME}:${VERSION} \
                        -t ${IMAGE_NAME}:latest \
                        .

                    echo ""
                    echo "===== DOCKER IMAGE CREATED ====="

                    docker images ${IMAGE_NAME}

                    echo ""
                    echo "Build stage completed successfully."
                '''
            }
        }


        // =====================================================
        // STAGE 2 - AUTOMATED TESTING
        // =====================================================
        stage('Test') {
            steps {

                echo '=========================================='
                echo 'STAGE 2: AUTOMATED TESTING'
                echo '=========================================='

                sh '''
                    set -e

                    echo "Running automated tests..."

                    python3 -m pytest -v

                    echo ""
                    echo "All automated tests passed."
                '''
            }
        }


        // =====================================================
        // STAGE 3 - CODE QUALITY
        // =====================================================
        stage('Code Quality') {
            steps {

                echo '=========================================='
                echo 'STAGE 3: CODE QUALITY'
                echo '=========================================='

                withSonarQubeEnv('SonarQube') {

                    sh '''
                        set -e

                        echo "Checking SonarScanner..."

                        which sonar-scanner || true

                        echo ""
                        echo "Running SonarQube analysis..."

                        sonar-scanner \
                            -Dsonar.projectKey=SIT753-Inventory-DevOps \
                            -Dsonar.projectName=SIT753-Inventory-DevOps \
                            -Dsonar.sources=app \
                            -Dsonar.tests=tests \
                            -Dsonar.python.version=3.12

                        echo ""
                        echo "SonarQube analysis completed."
                    '''
                }
            }
        }


        // =====================================================
        // STAGE 4 - SECURITY
        // =====================================================
        stage('Security') {
            steps {

                echo '=========================================='
                echo 'STAGE 4: SECURITY'
                echo '=========================================='

                sh '''
                    set +e

                    echo "=========================================="
                    echo "BANDIT SECURITY SCAN"
                    echo "=========================================="

                    which bandit

                    bandit \
                        -r app \
                        -f txt \
                        -o bandit-report.txt

                    BANDIT_STATUS=$?

                    echo ""
                    echo "Bandit exit code: ${BANDIT_STATUS}"

                    echo ""
                    echo "=========================================="
                    echo "PIP-AUDIT DEPENDENCY SCAN"
                    echo "=========================================="

                    which pip-audit

                    pip-audit \
                        -r requirements.txt \
                        -f columns \
                        > pip-audit-report.txt

                    AUDIT_STATUS=$?

                    echo ""
                    echo "pip-audit exit code: ${AUDIT_STATUS}"

                    echo ""
                    echo "=========================================="
                    echo "TRIVY DOCKER SECURITY SCAN"
                    echo "=========================================="

                    which trivy

                    trivy image \
                        --severity HIGH,CRITICAL \
                        ${IMAGE_NAME}:${VERSION} \
                        > trivy-report.txt

                    TRIVY_STATUS=$?

                    echo ""
                    echo "Trivy exit code: ${TRIVY_STATUS}"

                    echo ""
                    echo "=========================================="
                    echo "SECURITY SCAN SUMMARY"
                    echo "=========================================="

                    echo "Bandit: ${BANDIT_STATUS}"
                    echo "pip-audit: ${AUDIT_STATUS}"
                    echo "Trivy: ${TRIVY_STATUS}"

                    echo ""
                    echo "Security reports generated."

                    # Continue pipeline so discovered issues
                    # can be reviewed and documented.
                    exit 0
                '''

                archiveArtifacts artifacts:
                    'bandit-report.txt,pip-audit-report.txt,trivy-report.txt',
                    allowEmptyArchive: true
            }
        }


        // =====================================================
        // STAGE 5 - DEPLOY TO STAGING
        // =====================================================
        stage('Deploy to Staging') {
            steps {

                echo '=========================================='
                echo 'STAGE 5: DEPLOY TO STAGING'
                echo '=========================================='

                sh '''
                    set -e

                    echo "Removing previous staging container..."

                    docker rm -f ${STAGING_CONTAINER} 2>/dev/null || true

                    echo ""
                    echo "Starting staging container..."

                    docker run -d \
                        --name ${STAGING_CONTAINER} \
                        -p ${STAGING_PORT}:8000 \
                        ${IMAGE_NAME}:${VERSION}

                    echo ""
                    echo "Waiting for staging application..."

                    sleep 10

                    echo ""
                    echo "Checking staging health..."

                    curl --fail \
                        http://localhost:${STAGING_PORT}/health

                    echo ""
                    echo ""
                    echo "Checking staging metrics..."

                    curl --fail \
                        http://localhost:${STAGING_PORT}/metrics

                    echo ""
                    echo ""
                    echo "Staging deployment successful."
                '''
            }
        }


        // =====================================================
        // STAGE 6 - RELEASE TO PRODUCTION
        // =====================================================
        stage('Release to Production') {
            steps {

                echo '=========================================='
                echo 'STAGE 6: RELEASE TO PRODUCTION'
                echo '=========================================='

                sh '''
                    set -e

                    echo "Releasing version ${VERSION} to production..."

                    echo ""
                    echo "Removing previous production container..."

                    docker rm -f ${PRODUCTION_CONTAINER} 2>/dev/null || true

                    echo ""
                    echo "Starting production container..."

                    docker run -d \
                        --name ${PRODUCTION_CONTAINER} \
                        -p ${PRODUCTION_PORT}:8000 \
                        ${IMAGE_NAME}:${VERSION}

                    echo ""
                    echo "Waiting for production application..."

                    sleep 10

                    echo ""
                    echo "Checking production health..."

                    curl --fail \
                        http://localhost:${PRODUCTION_PORT}/health

                    echo ""
                    echo ""
                    echo "Production release successful."
                '''
            }
        }


        // =====================================================
        // STAGE 7 - MONITORING AND ALERTING
        // =====================================================
        stage('Monitoring') {
            steps {

                echo '=========================================='
                echo 'STAGE 7: MONITORING AND ALERTING'
                echo '=========================================='

                sh '''
                    set -e

                    echo "Checking production health..."

                    curl --fail \
                        http://localhost:${PRODUCTION_PORT}/health

                    echo ""
                    echo "Checking production metrics..."

                    curl --fail \
                        http://localhost:${PRODUCTION_PORT}/metrics

                    echo ""
                    echo "Checking production container..."

                    docker ps \
                        --filter "name=${PRODUCTION_CONTAINER}"

                    echo ""
                    echo "Production monitoring checks completed successfully."
                '''
            }
        }
    }


    // =========================================================
    // POST PIPELINE ACTIONS
    // =========================================================
    post {

        // =====================================================
        // SUCCESS → DISCORD
        // =====================================================
        success {

            echo '=========================================='
            echo 'PIPELINE SUCCESS'
            echo '=========================================='

            echo "Application: ${APP_NAME}"
            echo "Version: ${VERSION}"
            echo "Build number: ${BUILD_NUMBER}"

            echo "All seven DevOps stages completed successfully."

            withCredentials([
                string(
                    credentialsId: 'Discord_Webhook',
                    variable: 'DISCORD_WEBHOOK'
                )
            ]) {

                sh '''
                    curl -sS \
                        -H "Content-Type: application/json" \
                        --data-binary @- \
                        "$DISCORD_WEBHOOK" <<EOF
{"content":"Jenkins Pipeline SUCCESS - Application: ${APP_NAME} - Version: ${VERSION} - Build #${BUILD_NUMBER} - All 7 DevOps stages completed successfully."}
EOF
                '''
            }
        }


        // =====================================================
        // FAILURE → DISCORD ALERT
        // =====================================================
        failure {

            echo '=========================================='
            echo 'PIPELINE FAILED'
            echo '=========================================='

            echo "Application: ${APP_NAME}"
            echo "Build number: ${BUILD_NUMBER}"

            echo "Check Jenkins Console Output for the failed stage."

            withCredentials([
                string(
                    credentialsId: 'Discord_Webhook',
                    variable: 'DISCORD_WEBHOOK'
                )
            ]) {

                sh '''
                    curl -sS \
                        -H "Content-Type: application/json" \
                        --data-binary @- \
                        "$DISCORD_WEBHOOK" <<EOF
{"content":"Jenkins Pipeline FAILED - Application: ${APP_NAME} - Build #${BUILD_NUMBER} - Check Jenkins Console Output for details."}
EOF
                '''
            }
        }


        // =====================================================
        // ALWAYS
        // =====================================================
        always {

            echo '=========================================='
            echo 'PIPELINE EXECUTION FINISHED'
            echo '=========================================='
        }
    }
}
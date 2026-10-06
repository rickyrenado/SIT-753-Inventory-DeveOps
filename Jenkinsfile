pipeline {
    agent any

    environment {
        APP_NAME = 'inventory-api'
        IMAGE_NAME = 'inventory-api'
        VERSION = "1.0.${BUILD_NUMBER}"

        STAGING_CONTAINER = 'inventory-api-staging'
        PRODUCTION_CONTAINER = 'inventory-api-production'

        STAGING_PORT = '8001'
        PRODUCTION_PORT = '8000'
    }

    stages {

        // =====================================================
        // 1. BUILD
        // =====================================================
        stage('Build') {
            steps {
                echo '=========================================='
                echo 'STAGE 1: BUILD'
                echo '=========================================='

                sh '''
                    set -e

                    echo "Python version:"
                    python3 --version

                    echo "Docker version:"
                    docker --version

                    echo "Installing Python dependencies..."
                    python3 -m pip install -r requirements.txt

                    echo "Building Docker image..."

                    docker build \
                        -t ${IMAGE_NAME}:${VERSION} \
                        -t ${IMAGE_NAME}:latest \
                        .

                    echo "Docker image created successfully."

                    docker images ${IMAGE_NAME}
                '''
            }
        }


        // =====================================================
        // 2. AUTOMATED TESTING
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

                    echo "All automated tests passed."
                '''
            }
        }


        // =====================================================
        // 3. CODE QUALITY
        // =====================================================
        stage('Code Quality') {
            steps {
                echo '=========================================='
                echo 'STAGE 3: CODE QUALITY'
                echo '=========================================='

                withSonarQubeEnv('SonarQube') {

                    sh '''
                        set -e

                        echo "Running SonarQube analysis..."

                        sonar-scanner \
                            -Dsonar.projectKey=SIT753-Inventory-DevOps \
                            -Dsonar.projectName=SIT753-Inventory-DevOps \
                            -Dsonar.sources=app \
                            -Dsonar.tests=tests \
                            -Dsonar.python.version=3.12

                        echo "SonarQube analysis completed."
                    '''
                }
            }
        }


        // =====================================================
        // 4. SECURITY
        // =====================================================
        stage('Security') {
            steps {
                echo '=========================================='
                echo 'STAGE 4: SECURITY'
                echo '=========================================='

                sh '''
                    set +e

                    echo "=========================================="
                    echo "Bandit Security Scan"
                    echo "=========================================="

                    bandit \
                        -r app \
                        -f txt \
                        -o bandit-report.txt

                    BANDIT_STATUS=$?

                    echo "=========================================="
                    echo "Dependency Security Scan"
                    echo "=========================================="

                    pip-audit \
                        -r requirements.txt \
                        -f columns \
                        > pip-audit-report.txt

                    AUDIT_STATUS=$?

                    echo "=========================================="
                    echo "Trivy Docker Image Scan"
                    echo "=========================================="

                    trivy image \
                        --severity HIGH,CRITICAL \
                        ${IMAGE_NAME}:${VERSION} \
                        > trivy-report.txt

                    TRIVY_STATUS=$?

                    echo "=========================================="
                    echo "Security Scan Results"
                    echo "=========================================="

                    echo "Bandit exit code: ${BANDIT_STATUS}"
                    echo "pip-audit exit code: ${AUDIT_STATUS}"
                    echo "Trivy exit code: ${TRIVY_STATUS}"

                    echo "Security reports generated."

                    exit 0
                '''

                archiveArtifacts artifacts:
                    'bandit-report.txt,pip-audit-report.txt,trivy-report.txt',
                    allowEmptyArchive: true
            }
        }


        // =====================================================
        // 5. DEPLOY TO STAGING
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

                    echo "Starting staging container..."

                    docker run -d \
                        --name ${STAGING_CONTAINER} \
                        -p ${STAGING_PORT}:8000 \
                        ${IMAGE_NAME}:${VERSION}

                    echo "Waiting for staging application..."

                    sleep 10

                    echo "Checking staging health..."

                    curl --fail \
                        http://localhost:${STAGING_PORT}/health

                    echo ""

                    echo "Staging deployment successful."
                '''
            }
        }


        // =====================================================
        // 6. RELEASE TO PRODUCTION
        // =====================================================
        stage('Release to Production') {
            steps {
                echo '=========================================='
                echo 'STAGE 6: RELEASE TO PRODUCTION'
                echo '=========================================='

                sh '''
                    set -e

                    echo "Releasing version ${VERSION}..."

                    echo "Removing previous production container..."

                    docker rm -f ${PRODUCTION_CONTAINER} 2>/dev/null || true

                    echo "Starting production container..."

                    docker run -d \
                        --name ${PRODUCTION_CONTAINER} \
                        -p ${PRODUCTION_PORT}:8000 \
                        ${IMAGE_NAME}:${VERSION}

                    echo "Waiting for production application..."

                    sleep 10

                    echo "Checking production health..."

                    curl --fail \
                        http://localhost:${PRODUCTION_PORT}/health

                    echo ""

                    echo "Production release successful."
                '''
            }
        }


        // =====================================================
        // 7. MONITORING AND ALERTING
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

                    echo "Production monitoring checks completed."
                '''
            }
        }
    }


    // =========================================================
    // POST PIPELINE
    // =========================================================
    post {

        // -----------------------------------------------------
        // SUCCESS → DISCORD
        // -----------------------------------------------------
        success {
            echo '=========================================='
            echo 'PIPELINE SUCCESS'
            echo '=========================================='

            echo "Application: ${APP_NAME}"
            echo "Version: ${VERSION}"
            echo 'All seven DevOps stages completed successfully.'

            withCredentials([
                string(
                    credentialsId: 'Discord_Webhook',
                    variable: 'DISCORD_WEBHOOK'
                )
            ]) {

                sh '''
                    curl \
                        -H "Content-Type: application/json" \
                        -d "{\"content\":\"✅ Jenkins Pipeline SUCCESS\\nApplication: ${APP_NAME}\\nVersion: ${VERSION}\\nAll 7 DevOps stages completed successfully.\"}" \
                        "$DISCORD_WEBHOOK"
                '''
            }
        }


        // -----------------------------------------------------
        // FAILURE → DISCORD ALERT
        // -----------------------------------------------------
        failure {
            echo '=========================================='
            echo 'PIPELINE FAILED'
            echo '=========================================='

            echo 'Check Jenkins Console Output for the failed stage.'

            withCredentials([
                string(
                    credentialsId: 'Discord_Webhook',
                    variable: 'DISCORD_WEBHOOK'
                )
            ]) {

                sh '''
                    curl \
                        -H "Content-Type: application/json" \
                        -d "{\"content\":\"🚨 Jenkins Pipeline FAILED\\nApplication: ${APP_NAME}\\nBuild: #${BUILD_NUMBER}\\nCheck Jenkins Console Output for details.\"}" \
                        "$DISCORD_WEBHOOK"
                '''
            }
        }


        // -----------------------------------------------------
        // ALWAYS
        // -----------------------------------------------------
        always {
            echo '=========================================='
            echo 'PIPELINE EXECUTION FINISHED'
            echo '=========================================='
        }
    }
}
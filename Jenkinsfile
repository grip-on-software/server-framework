pipeline {
    agent { label 'docker' }

    environment {
        GITLAB_TOKEN = credentials('server-framework-gitlab-token')
        SCANNER_HOME = tool name: 'SonarQube Scanner 3', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
    }
    options {
        gitLabConnection('gitlab')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    triggers {
        gitlab(triggerOnPush: true, triggerOnMergeRequest: true, branchFilterType: 'All', secretToken: env.GITLAB_TOKEN)
        cron('H H * * H/3')
    }

    post {
        failure {
            updateGitlabCommitStatus name: env.JOB_NAME, state: 'failed'
        }
        aborted {
            updateGitlabCommitStatus name: env.JOB_NAME, state: 'canceled'
        }
        always {
            publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: true, reportDir: 'mypy-report/', reportFiles: 'index.html', reportName: 'Typing', reportTitles: ''])
            junit allowEmptyResults: true, testResults: 'mypy-report/junit.xml'
        }
    }

    stages {
        stage('Start') {
            when {
                not {
                    triggeredBy 'TimerTrigger'
                }
            }
            steps {
                updateGitlabCommitStatus name: env.JOB_NAME, state: 'running'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'pypi-repository', variable: 'PIP_REGISTRY'), file(credentialsId: 'pypi-certificate', variable: 'PIP_CERTIFICATE')]) {
                    withPythonEnv('System-CPython-3') {
                        pysh 'python -m pip install lxml certifi'
                        pysh 'python -m pip install $(python make_pip_args.py $PIP_REGISTRY $PIP_CERTIFICATE) -r requirements-analysis.txt'
                        pysh 'make mypy_html'
                        pysh 'make pylint'
                    }
                }
                withSonarQubeEnv('SonarQube') {
                    sh '${SCANNER_HOME}/bin/sonar-scanner -Dsonar.projectKey=server-framework:$BRANCH_NAME -Dsonar.projectName="Server framework $BRANCH_NAME"'
                }
            }
        }
        stage('Build') {
            agent {
                docker {
                    image 'python:3.8-alpine3.18'
                    reuseNode true
                }
            }
            steps {
                sh 'make build'
            }
        }
        stage('Push') {
            when { branch 'master' }
            steps {
                withPythonEnv('System-CPython-3') {
                    pysh 'make setup_release'
                    withCredentials([usernamePassword(credentialsId: 'pypi-credentials', passwordVariable: 'TWINE_PASSWORD', usernameVariable: 'TWINE_USERNAME'), string(credentialsId: 'pypi-repository', variable: 'TWINE_REPOSITORY_URL'), file(credentialsId: 'pypi-certificate', variable: 'TWINE_CERT')]) {
                        pysh 'make upload'
                    }
                }
            }
        }
        stage('Status') {
            when {
                not {
                    triggeredBy 'TimerTrigger'
                }
            }
            steps {
                updateGitlabCommitStatus name: env.JOB_NAME, state: 'success'
            }
        }
    }
}

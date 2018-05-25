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
    }

    stages {
        stage('Start') {
            when {
                expression {
                    currentBuild.rawBuild.getCause(hudson.triggers.TimerTrigger$TimerTriggerCause) == null
                }
            }
            steps {
                updateGitlabCommitStatus name: env.JOB_NAME, state: 'running'
            }
        }
        stage('SonarQube Analysis') {
            when {
                anyOf {
                    expression {
                        currentBuild.rawBuild.getCause(hudson.triggers.TimerTrigger$TimerTriggerCause) != null
                    }
                    not { branch 'master' }
                }
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    withPythonEnv('System-CPython-3') {
                        pysh 'python -m pip install pylint'
                        pysh 'python -m pip install -r requirements.txt'
                        pysh 'sed -i "1s|.*|#!/usr/bin/env python|" `which pylint`'
                        pysh '${SCANNER_HOME}/bin/sonar-scanner -Dsonar.branch=$BRANCH_NAME -Dsonar.python.pylint=`which pylint`'
                    }
                }
            }
        }
        stage('Build') {
            agent {
                docker {
                    image '$AGENT_IMAGE'
                    reuseNode true
                }
            }
            steps {
                sh 'python setup.py sdist'
                sh 'python setup.py bdist_wheel'
            }
        }
        stage('Push') {
            when { branch 'master' }
            steps {
                withPythonEnv('System-CPython-3') {
                    pysh 'python -m pip install twine'
                    withCredentials([usernamePassword(credentialsId: 'pypi-credentials', passwordVariable: 'TWINE_PASSWORD', usernameVariable: 'TWINE_USERNAME'), string(credentialsId: 'pypi-repository', variable: 'TWINE_REPOSITORY_URL'), file(credentialsId: 'pypi-certificate', variable: 'TWINE_CERT')]) {
                        pysh 'python -m twine upload dist/*'
                    }
                }
            }
        }
        stage('Status') {
            when {
                expression {
                    currentBuild.rawBuild.getCause(hudson.triggers.TimerTrigger$TimerTriggerCause) == null
                }
            }
            steps {
                updateGitlabCommitStatus name: env.JOB_NAME, state: 'success'
            }
        }
    }
}

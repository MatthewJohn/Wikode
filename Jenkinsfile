node {
    environment {
        SONAR_KEY = credentials('wikode-sonar-key')
    }
    stage('Checkout') {
        checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[url: 'ssh://git@gitlab.dockstudios.co.uk:2222/pub/wikode.git']]])
    }
    stage('Code Analyse') {
        sh 'sonar-scanner -Dsonar.projectKey=Wikode -Dsonar.sources=. -Dsonar.host.url=http://sonarqube.dock.studios -Dsonar.login=$SONAR_KEY'
    }

    stage('Build') {
        sh 'docker build .'
    }

    stage('Clean Up') {
        step([$class: 'WsCleanup'])
    }
}


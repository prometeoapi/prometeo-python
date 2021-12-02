pipeline {
    agent any
    stages {
        stage("Run tests") {
            steps {
                sh("python3 -m venv env")
                sh("source ./env/bin/activate")
                sh("which python3")
                sh("which python")
                sh("which pip")
                sh("which pip3")
                sh("pip3 install -r dev-requirements.txt")
                sh("tox")
            }
        }

        stage("Publish to PyPI") {
           // when {
           //      expression {
           //          return env.BRANCH_NAME ==~ /(master|develop)/
           //      }
           //  }
            steps {
                sh("python3 -m venv env")
                sh("source ./env/bin/activate")
                sh("pip3 install twine")
                sh("python3 setup.py sdist bdist_wheel")
                sh("twine check dist/*")
                // sh("twine upload dist/*")
            }
        }
    }
}

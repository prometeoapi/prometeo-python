pipeline {
    agent any
    stages {
        stage("Run tests") {
            steps {
                sh("pip install -r dev-requirements.txt")
                sh("tox")
            }
        }

        stage("Publish to PyPI") {
           when {
                expression {
                    return env.BRANCH_NAME ==~ /(master|develop)/
                }
            }
            steps {
                sh("pip install twine")
                sh("python setup.py sdist bdist_wheel")
                sh("twine check dist/*")
                sh("twine upload dist/*")
            }
        }
    }
}

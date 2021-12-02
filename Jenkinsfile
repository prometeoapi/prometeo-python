pipeline {
    agent any
    environment {
        if (env.BRANCH_NAME == "master") {
            TWINE_USERNAME = credentials("prod-pypi-username")
            TWINE_PASSWORD = credentials("prod-pypi-password")
            TWINE_REPOSITORY_URL = "https://upload.pypi.org/legacy/"
        } else if (env.BRANCH_NAME == "develop") {
            TWINE_USERNAME = credentials("test-pypi-username")
            TWINE_PASSWORD = credentials("test-pypi-password")
            TWINE_REPOSITORY_URL = "https://test.pypi.org/legacy/"
        }
    }
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

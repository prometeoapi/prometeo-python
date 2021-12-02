pipeline {
    agent any
    environment {
        // Prod credentials
        TWINE_PROD_USERNAME = credentials("prod-pypi-username")
        TWINE_PROD_PASSWORD = credentials("prod-pypi-password")
        TWINE_PROD_REPOSITORY_URL = "https://upload.pypi.org/legacy/"

        // Dev credentials
        TWINE_DEV_USERNAME = credentials("test-pypi-username")
        TWINE_DEV_PASSWORD = credentials("test-pypi-password")
        TWINE_DEV_REPOSITORY_URL = "https://test.pypi.org/legacy/"

        TWINE_USERNAME = "${env.BRANCH_NAME == 'master' ? env.TWINE_PROD_USERNAME : env.TWINE_DEV_USERNAME}"
        TWINE_PASSWORD = "${env.BRANCH_NAME == 'master' ? env.TWINE_PROD_PASSWORD : env.TWINE_DEV_PASSWORD}"
        TWINE_REPOSITORY_URL = "${env.BRANCH_NAME == 'master' ? env.TWINE_PROD_REPOSITORY_URL : env.TWINE_DEV_REPOSITORY_URL}"
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

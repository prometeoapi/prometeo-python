pipeline {
    agent any

    stages {
        stage("Run tests") {
            steps {
                sh("python3 -m venv .venv")
                sh("""
                   source ./.venv/bin/activate
                   pip install --upgrade pip
                   pip install -r dev-requirements.txt
                   tox
                   """)
            }
        }

        stage("Publish to PyPI") {
           // when {
           //      expression {
           //          return env.BRANCH_NAME ==~ /(master|develop)/
           //      }
           //  }
            environment {
                TWINE_USERNAME = credentials("${env.CHANGE_TARGET}-pypi-username")
                TWINE_PASSWORD = credentials("${env.CHANGE_TARGET}-pypi-password")
                TWINE_REPOSITORY_URL = credentials("${env.CHANGE_TARGET}-pypi-repository")
            }
            steps {
                sh("python3 -m venv .venv")
                sh("""
                    source ./.venv/bin/activate
                    pip install --upgrade pip
                    pip install twine wheel
                    python setup.py sdist bdist_wheel
                    twine check dist/*
                    twine upload dist/* --verbose
                    """)
            }
        }
    }
}

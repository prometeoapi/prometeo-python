pipeline {
    agent any

    environment {
        TWINE_USERNAME = credentials("test-pypi-username")
        TWINE_PASSWORD = credentials("test-pypi-password")
        TWINE_REPOSITORY_URL = credentials("test-pypi-repository")
    }

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

        stage("Publish DEV to Pypi") {
            // when {
            //     expression {
            //         return env.BRANCH_NAME ==~ /(develop)/
            //     }
            // }
            //
            steps {
                sh("echo $env.BRANCH_NAME")
                sh("echo ${env.BRANCH_NAME}")
                publishToPypi()
            }
        }

        stage("Publish PROD to Pypi") {
            // when {
            //     expression {
            //         return env.BRANCH_NAME ==~ /(master)/
            //     }
            // }
            //
            environment {
                TWINE_USERNAME = credentials("prod-pypi-username")
                TWINE_PASSWORD = credentials("prod-pypi-password")
                TWINE_REPOSITORY_URL = credentials("prod-pypi-repository")
            }
            steps {
                publishToPypi()
            }
        }
    }
}


def publishToPypi() {
    sh("python3 -m venv .venv")
    sh("""
        source ./.venv/bin/activate
        pip install --upgrade pip
        pip install twine wheel
        python setup.py sdist bdist_wheel
        twine check dist/*
        twine upload dist/* --repository-url $TWINE_REPOSITORY_URL -u $TWINE_USERNAME -p $TWINE_PASSWORD --verbose
        """)
}

pipeline {
    agent any

    environment {
        TWINE_USERNAME = getCredential("pypi-username")
        TWINE_PASSWORD = getCredential("pypi-password")
        TWINE_REPOSITORY_URL = getCredential("pypi-repository")
    }

    stages {
        stage("Check env") {
            steps {
                sh("printenv")
            }
        }

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

def getCredential(varName) {
    switch(env.BRANCH_NAME) {
        case "master": return credentials("master-${varName}"); break
        case "develop": return credentials("develop-${varName}"); break
        default: return "some-default"; break
    }
}

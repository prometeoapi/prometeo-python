pipeline {
    agent any

    environment {
        TWINE_USERNAME = getCredential("pypi-username")
        TWINE_PASSWORD = getCredential(""pypi-password"")
        TWINE_REPOSITORY_URL = getCredential(""pypi-repository"")
    }

    stages {
        stage("Run tests") {
            steps {
                sh("python3 -m venv env")
                sh("""
                   source ./env/bin/activate
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
                sh("python3 -m venv venv")
                sh("""
                   source ./venv/bin/activate
                   pip install twine
                   python setup.py sdist bdist_wheel
                   twine check dist/*
                   """)
                // sh("twine upload dist/*")
            }
        }
    }
}

def getCredential(varName) {
    if (env.BRANCH_NAME == "master") {
        return credentials("prod-${varName}")
    } else (env.BRANCH_NAME == "develop") {
        return credentials("test-${varName}")
    } else {
        return "";
    }
}

pipeline {
    agent any
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
                sh("python3 -m venv env")
                sh("""
                   source ./env/bin/activate
                   pip install twine
                   python setup.py sdist bdist_wheel
                   twine check dist/*
                   """)
                // sh("twine upload dist/*")
            }
        }
    }
}

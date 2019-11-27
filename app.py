from flask import Flask

__author__ = 'Lena Zhao'

# setup flask
app = Flask(__name__)
# give a secret key
app.secret_key = "secret_key"

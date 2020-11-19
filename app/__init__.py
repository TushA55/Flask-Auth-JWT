from flask import Flask
from mongoengine import connect

try:
    connect(host='mongodb+srv://admin:TushA55@nodejscluster.pujjv.mongodb.net/flaskJWT?retryWrites=true&w=majority')
except Exception as e:
    print(e)
    exit(0)
finally:
    app = Flask(__name__)

    from .views import *

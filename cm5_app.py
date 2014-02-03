from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')

Bootstrap(app)

db = SQLAlchemy(app)

import views

if __name__ == '__main__':
  app.run(debug=True)
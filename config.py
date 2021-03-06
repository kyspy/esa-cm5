CSRF_ENABLED = True
SECRET_KEY = '#X@tEs/~au*DEJYR:!8D0a/%jHa%A]%qcYgD~6oDGA|:PtqG90^1HsX#;bv9zv_'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

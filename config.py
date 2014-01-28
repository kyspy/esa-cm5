CSRF_ENABLED = True
SECRET_KEY = '#X@tEs/~au*DEJYR:!8D0a/%jHa%A]%qcYgD~6oDGA|:PtqG90^1HsX#;bv9zv_'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'esa_app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_esa_repository')
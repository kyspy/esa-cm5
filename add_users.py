"""

from cm5_app import db
from models import User
from sqlalchemy.orm.exc import NoResultFound

def add_users_db():

    first_names = [
        'Kyla', 'Oleg', 'David', 'Test'
    ]
    last_names = [
        'Farrell', 'Moskovich', 'Deisadze', 'Tester'
    ]
    email = [
        'kfarrell@mtacc-esa.info', 'omoshkov@mtacc-esa.info', 'ddeisadze@mtacc-esa.info', 'test@gmail.com'
    ]
    password = [
        'Esalirovc123', 'Esalirovc1', 'Esalirovc12', 'testtesttest'
    ]

    for i in range(len(first_names)):
        try:
            User.query.filter(User.email == email[i]).one()
        except NoResultFound:
            user = User()
            user.firstname = first_names[i]
            user.lastname = last_names[i]
            user.email = email[i]
            user.password = password[i]
            db.session.add(user)

    db.session.commit()
    return
"""
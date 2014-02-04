from cm5_app import db
from models import User

def build_user_db():
    """
    Rebuild the user db with users
    """

    db.drop_all()
    db.create_all()
    test_user = User(login="test", password="test")
    db.session.add(test_user)

    first_names = [
        'Kyla', 'Oleg'
    ]
    last_names = [
        'Farrell', 'Moshkov'
    ]

    for i in range(len(first_names)):
        user = User()
        user.first_name = first_names[i]
        user.last_name = last_names[i]
        user.login = user.first_name[0] + user.last_name.lower()
        user.email = user.login + "@mtacc-esa.info"
        user.password = 'Esalirovc1'
        db.session.add(user)

    db.session.commit()
    return
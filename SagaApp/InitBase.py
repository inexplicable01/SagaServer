from SagaApp.UserModel import User, Role

def InitBase(user_manager,db):
    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(email='member@example.com',
                    # email_confirmed_at=datetime.datetime.utcnow(),
                    password='Password1')
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(
            email='admin@example.com',
            # email_confirmed_at=datetime.datetime.utcnow(),
            password='Password1',
        )
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'agent@example.com').first():
        user = User(email='agent@example.com',
                    password='Password1')
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'agent2@example.com').first():
        user = User(email='agent2@example.com',
                    password='Password1')
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'usercemail@gmail.com').first():
        user = User(email='usercemail@gmail.com',
                    password='passwordC')
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'userdemail@gmail.com').first():
        user = User(email='userdemail@gmail.com',
                    password='passwordD')
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'usereemail@gmail.com').first():
        user = User(email='usereemail@gmail.com',
                    password='passwordE')
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'userbemail@gmail.com').first():
        user = User(email='userbemail@gmail.com',
                    password='passwordB')
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'useraemail@gmail.com').first():
        user = User(email='useraemail@gmail.com',
                    password='passwordA')
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()
from SagaUser.UserModel import User, Role

worldmapid = 'fc925b23-30b8-4d77-9310-289b85ef8eb0'
worldmapgroupname='WorldMap'

privateworldid = 'c752575b-7cc2-47e7-ae3a-97fe1ea5aeeb'
privateworldname='PrivateMap'

def InitBase(db):
    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(email='member@example.com',
                    # email_confirmed_at=datetime.datetime.utcnow(),
                    password='Password1',
                    sectionid=worldmapid,
                    section_name=worldmapgroupname)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(
            email='admin@example.com',
            # email_confirmed_at=datetime.datetime.utcnow(),
            password='Password1',
            sectionid = worldmapid,
            section_name = worldmapgroupname

        )
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'agent@example.com').first():
        user = User(email='agent@example.com',
                    password='Password1',
                    sectionid = worldmapid,
                    section_name = worldmapgroupname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'agent2@example.com').first():
        user = User(email='agent2@example.com',
                    password='Password1',
            sectionid = worldmapid,
            section_name = worldmapgroupname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'usercemail@gmail.com').first():
        user = User(email='usercemail@gmail.com',
                    password='passwordC',
            sectionid = worldmapid,
            section_name = worldmapgroupname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'waichak.luk@gmail.com').first():
        user = User(email='waichak.luk@gmail.com',
                    password='passwordW',
            sectionid = worldmapid,
            section_name = worldmapgroupname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'userdemail@gmail.com').first():
        user = User(email='userdemail@gmail.com',
                    password='passwordD',
            sectionid = worldmapid,
            section_name = worldmapgroupname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'usereemail@gmail.com').first():
        user = User(email='usereemail@gmail.com',
                    password='passwordE',
            sectionid = worldmapid,
            section_name = worldmapgroupname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'userbemail@gmail.com').first():
        user = User(email='userbemail@gmail.com',
                    password='passwordB',
            sectionid = worldmapid,
            section_name = worldmapgroupname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'useraemail@gmail.com').first():
        user = User(email='useraemail@gmail.com',
                    password='passwordA',
            sectionid = worldmapid,
            section_name = worldmapgroupname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'private@gmail.com').first():
        user = User(email='private@gmail.com',
                    password='private',
            sectionid = privateworldid,
            section_name = privateworldname)
        agentrole = Role.query.filter(Role.name == 'Agent').first()
        user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()
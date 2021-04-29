from SagaUser.UserModel import User, Role, Section

worldmapid = 'fc925b23-30b8-4d77-9310-289b85ef8eb0'
worldmapgroupname='WorldMap'

privateworldid = 'c752575b-7cc2-47e7-ae3a-97fe1ea5aeeb'
privateworldname='PrivateMap'

mechdemoid='102a7375-b8a7-4bb6-9368-e292a2389acc'
mechdemoname= 'MECHDEMO'

sagafolderid = '359b0947-0e8b-4d96-a4c7-3b1ade4b170f'
sagafoldername = 'SAGAFolder'

def InitBase(db):
    if not Section.query.filter(Section.sectionid == worldmapid).first():
        section = Section(
            sectionid=worldmapid,
            sectionname=worldmapgroupname,
        )
        db.session.add(section)
        db.session.commit()

    if not Section.query.filter(Section.sectionid == privateworldid).first():
        section = Section(
            sectionid=privateworldid,
            sectionname=privateworldname,
        )
        db.session.add(section)
        db.session.commit()

    if not Section.query.filter(Section.sectionid == sagafolderid).first():
        section = Section(
            sectionid=sagafolderid,
            sectionname=sagafoldername,
        )
        db.session.add(section)
        db.session.commit()

    if not Section.query.filter(Section.sectionid == mechdemoid).first():
        section = Section(
            sectionid=mechdemoid,
            sectionname=mechdemoname,
        )
        db.session.add(section)
        db.session.commit()

    if not Role.query.filter(Role.name == 'Agent').first():
        roles = Role(name = 'Agent')
        db.session.add(roles)
        db.session.commit()
    if not Role.query.filter(Role.name == 'Admin').first():
        roles = Role(name = 'Admin')
        db.session.add(roles)
        db.session.commit()

    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(email='member@example.com',
                    # email_confirmed_at=datetime.datetime.utcnow(),
                    password='Password1',
                    sectionid=worldmapid,
                    sectionname=worldmapgroupname,
                    role='Agent'
                    )
        # user.sections.append(Section(id=worldmapid,sectionname=worldmapgroupname))
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(
            email='admin@example.com',
            # email_confirmed_at=datetime.datetime.utcnow(),
            password='Password1',
            role='Admin',
            sectionid=worldmapid,
            sectionname=worldmapgroupname
        )
        # user.sections.append(Section(sectionid=worldmapid,sectionname=worldmapgroupname))
        # user.roles.append(Role(name='Admin'))
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'agent@example.com').first():
        user = User(email='agent@example.com',
                    password='Password1',
                    sectionid=worldmapid,
                    sectionname=worldmapgroupname,
                    role='Agent'
                    )

        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'agent2@example.com').first():
        user = User(email='agent2@example.com',
                    password='Password1',
                    sectionid=worldmapid,
                    sectionname=worldmapgroupname,
                    role='Agent'
                    )
        # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
        #
        # agentrole = Role.query.filter(Role.name == 'Agent').first()
        # user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'usercemail@gmail.com').first():
        user = User(email='usercemail@gmail.com',
                    password='passwordC',
                    sectionid=worldmapid,
                    sectionname=worldmapgroupname,
                    role='Agent'
                    )
        # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
        #
        # agentrole = Role.query.filter(Role.name == 'Agent').first()
        # user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'waichak.luk@gmail.com').first():
        user = User(email='waichak.luk@gmail.com',
                    password='passwordW',
                    sectionid=sagafolderid,
                    sectionname=sagafoldername,
                    role='Agent'
                    )
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'jimmyleong113@gmail.com').first():
        user = User(email='jimmyleong113@gmail.com',
                    password='passwordJ',
                    sectionid=sagafolderid,
                    sectionname=sagafoldername,
                    role='Agent'
                    )
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'userdemail@gmail.com').first():
        user = User(email='userdemail@gmail.com',
                    password='passwordD',
                    sectionid=worldmapid,
                    sectionname=worldmapgroupname,
                    role='Agent'
                    )
        # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
        #
        # agentrole = Role.query.filter(Role.name == 'Agent').first()
        # user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'usereemail@gmail.com').first():
        user = User(email='usereemail@gmail.com',
                    password='passwordE',
                    sectionid=worldmapid,
                    sectionname=worldmapgroupname,
                    role='Agent'
                    )
        # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
        #
        # agentrole = Role.query.filter(Role.name == 'Agent').first()
        # user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'userbemail@gmail.com').first():
        user = User(email='userbemail@gmail.com',
                    password='passwordB',
                    sectionid=worldmapid,
                    sectionname=worldmapgroupname,
                    role='Agent'
                    )
        # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
        #
        # agentrole = Role.query.filter(Role.name == 'Agent').first()
        # user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'useraemail@gmail.com').first():
        user = User(email='useraemail@gmail.com',
                    password='passwordA',
                    sectionid=worldmapid,
                    sectionname=worldmapgroupname,
                    role='Agent'
                    )
        # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
        #
        # agentrole = Role.query.filter(Role.name == 'Agent').first()
        # user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'private@gmail.com').first():
        user = User(email='private@gmail.com',
                    password='private',
                    sectionid=privateworldid,
                    sectionname=privateworldname,
                    role='Agent')
        # user.sections.append(Section(, ))
        #
        # agentrole = Role.query.filter(Role.name == 'Agent').first()
        # user.roles.append(agentrole)
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'user1@mechdemo.com').first():
        user = User(email='user1@mechdemo.com',
                    password='user1password',
                    sectionid=mechdemoid,
                    sectionname=mechdemoname,
                    first_name='Bob',
                    last_name='Smith',
                    role='Agent')
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'user2@mechdemo.com').first():
        user = User(email='user2@mechdemo.com',
                    password='user2password',
                    sectionid=mechdemoid,
                    sectionname=mechdemoname,
                    first_name='Jane',
                    last_name='Doe',
                    role='Agent')
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'o.petrenko@gmail.com').first():
        user = User(email='o.petrenko@gmail.com',
                    password='password',
                    sectionid=mechdemoid,
                    sectionname=mechdemoname,
                    first_name='Oleg',
                    last_name='Petrenko',
                    role='Agent')
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'bob@bob.com').first():
        user = User(email='bob@bob.com',
                    password='password',
                    sectionid=mechdemoid,
                    sectionname=mechdemoname,
                    first_name='Bob',
                    last_name='Structure',
                    role='Agent')
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'jane@jane.com').first():
        user = User(email='jane@jane.com',
                    password='password',
                    sectionid=mechdemoid,
                    sectionname=mechdemoname,
                    first_name='Aero',
                    last_name='Jane',
                    role='Agent')
        db.session.add(user)
        db.session.commit()
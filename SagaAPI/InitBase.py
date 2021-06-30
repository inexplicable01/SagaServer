from SagaDB.UserModel import User, Role, Section
from SagaDB.FileRecordModel import FileRecord

worldmapid = 'fc925b23-30b8-4d77-9310-289b85ef8eb0'
worldmapgroupname='WorldMap'

privateworldid = 'c752575b-7cc2-47e7-ae3a-97fe1ea5aeeb'
privateworldname='PrivateMap'

mechdemoid='102a7375-b8a7-4bb6-9368-e292a2389acc'
mechdemoname= 'MechExample'

sagafolderid = '359b0947-0e8b-4d96-a4c7-3b1ade4b170f'
sagafoldername = 'SAGAFolder'

electricalid = '0867eb8f-c9e5-4dbb-a58f-da82b5685c8b'
ElectricalDemoname = 'ElectricalDemo'

CADDemoid = '5a4cdb98-ca23-4d36-93e0-74c49fa7d1fc'
CADDemoname = 'CADDemo'
#
ManufacturingDemoid = '7f172a4c-a378-4b30-8e4b-242ab7853381'
ManufacturingDemoname = 'ManufacturingDemo'

MovieDemoid = '8ebbfab3-565e-4ce6-bb62-488033cb437e'
MovieDemoname = 'MovieDemo'
ArchitectDemoid = '028b524a-1459-4b3a-a1c0-c3694e259318'
ArchitectDemoname = 'ArchitectDemo'
AccountingDemoid = 'a19df2b1-4f53-4265-8e9c-16d9a8b441c5'
AccountingDemoname = 'AccountingDemo'

basesectionids = [worldmapid,privateworldid,mechdemoid,sagafolderid,electricalid,CADDemoid,ManufacturingDemoid,
MovieDemoid,ArchitectDemoid,AccountingDemoid]
basesectiondescrip=[worldmapgroupname,privateworldname,mechdemoname,sagafoldername,ElectricalDemoname,
CADDemoname,ManufacturingDemoname,MovieDemoname,ArchitectDemoname,AccountingDemoname]


def InitBase(db, sagauserdb):
    for sectionnum, sectiondetails in sagauserdb.sectionids.items():
        if not Section.query.filter(Section.sectionid == sectiondetails['sectionid']).first():
            section = Section(
                sectionid=sectiondetails['sectionid'],
                sectionname=sectiondetails['sectionname'],
            )
            db.session.add(section)
            db.session.commit()

    for rolenum, roledetails in sagauserdb.rolenames.items():
            if not Role.query.filter(Role.name == roledetails['name']).first():
                roles = Role(name = roledetails['name'])
                db.session.add(roles)
                db.session.commit()
    # if not Role.query.filter(Role.name == 'Admin').first():
    #     roles = Role(name = 'Admin')
    #     db.session.add(roles)
    #     db.session.commit()

    for usernum, userdetails in sagauserdb.users.items():
        if not User.query.filter(User.email == userdetails['email']).first():
            user = User(email=userdetails['email'],
                        password=userdetails['password'],
                        sectionid=userdetails['sectionid'],
                        sectionname=userdetails['sectionname'],
                        role=userdetails['role']
                        )
            # user.sections.append(Section(id=worldmapid,sectionname=worldmapgroupname))
            for ind, sectionid in enumerate(userdetails['sections']):
                sect = Section.query.filter(Section.sectionid == sectionid).first()
                user.sections.append(sect)
            db.session.add(user)
    db.session.commit()

    # if not User.query.filter(User.email == 'admin@example.com').first():
    #     user = User(
    #         email='admin@example.com',
    #         # email_confirmed_at=datetime.datetime.utcnow(),
    #         password='Password1',
    #         role='Admin',
    #         sectionid=worldmapid,
    #         sectionname=worldmapgroupname
    #     )
    #     # user.sections.append(Section(sectionid=worldmapid,sectionname=worldmapgroupname))
    #     # user.roles.append(Role(name='Admin'))
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'agent@example.com').first():
    #     user = User(email='agent@example.com',
    #                 password='Password1',
    #                 sectionid=worldmapid,
    #                 sectionname=worldmapgroupname,
    #                 role='Agent'
    #                 )
    #
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'agent2@example.com').first():
    #     user = User(email='agent2@example.com',
    #                 password='Password1',
    #                 sectionid=worldmapid,
    #                 sectionname=worldmapgroupname,
    #                 role='Agent'
    #                 )
    #     # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
    #     #
    #     # agentrole = Role.query.filter(Role.name == 'Agent').first()
    #     # user.roles.append(agentrole)
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'usercemail@gmail.com').first():
    #     user = User(email='usercemail@gmail.com',
    #                 password='passwordC',
    #                 sectionid=worldmapid,
    #                 sectionname=worldmapgroupname,
    #                 role='Agent'
    #                 )
    #     # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
    #     #
    #     # agentrole = Role.query.filter(Role.name == 'Agent').first()
    #     # user.roles.append(agentrole)
    #     for ind, sectionid in enumerate(basesectionids):
    #         sect = Section.query.filter(Section.sectionid == sectionid).first()
    #         user.sections.append(sect)
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'jcasteret.usperson@c-s-inc.us').first():
    #     user = User(email='jcasteret.usperson@c-s-inc.us',
    #                 password='passwordJ',
    #                 sectionid=sagafolderid,
    #                 sectionname=sagafoldername,
    #                 role='Agent',first_name='Jerome',last_name='C'
    #                 )
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'waichak.luk@gmail.com').first():
    #     user = User(email='waichak.luk@gmail.com',
    #                 password='passwordW',
    #                 sectionid=sagafolderid,
    #                 sectionname=sagafoldername,
    #                 role='Admin',first_name='Wai',last_name='Luk'
    #                 )
    #     for ind, sectionid in enumerate(basesectionids):
    #         sect = Section.query.filter(Section.sectionid == sectionid).first()
    #         user.sections.append(sect)
    #     db.session.add(user)
    #     db.session.commit()


    # if not User.query.filter(User.email == 'jimmyleong113@gmail.com').first():
    #     user = User(email='jimmyleong113@gmail.com',
    #                 password='passwordJ',
    #                 sectionid=sagafolderid,
    #                 sectionname=sagafoldername,
    #                 role='Agent',first_name='Jimmy',last_name='Leong'
    #                 )
    #     for ind, sectionid in enumerate(basesectionids):
    #         sect = Section.query.filter(Section.sectionid == sectionid).first()
    #         user.sections.append(sect)
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'userdemail@gmail.com').first():
    #     user = User(email='userdemail@gmail.com',
    #                 password='passwordD',
    #                 sectionid=worldmapid,
    #                 sectionname=worldmapgroupname,
    #                 role='Agent'
    #                 )
    #     # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
    #     #
    #     # agentrole = Role.query.filter(Role.name == 'Agent').first()
    #     # user.roles.append(agentrole)
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'usereemail@gmail.com').first():
    #     user = User(email='usereemail@gmail.com',
    #                 password='passwordE',
    #                 sectionid=worldmapid,
    #                 sectionname=worldmapgroupname,
    #                 role='Agent'
    #                 )
    #     # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
    #     #
    #     # agentrole = Role.query.filter(Role.name == 'Agent').first()
    #     # user.roles.append(agentrole)
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'userbemail@gmail.com').first():
    #     user = User(email='userbemail@gmail.com',
    #                 password='passwordB',
    #                 sectionid=worldmapid,
    #                 sectionname=worldmapgroupname,
    #                 role='Agent'
    #                 )
    #     # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
    #     #
    #     # agentrole = Role.query.filter(Role.name == 'Agent').first()
    #     # user.roles.append(agentrole)
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'useraemail@gmail.com').first():
    #     user = User(email='useraemail@gmail.com',
    #                 password='passwordA',
    #                 sectionid=worldmapid,
    #                 sectionname=worldmapgroupname,
    #                 role='Agent'
    #                 )
    #     # user.sections.append(Section(sectionid=worldmapid, sectionname=worldmapgroupname))
    #     #
    #     # agentrole = Role.query.filter(Role.name == 'Agent').first()
    #     # user.roles.append(agentrole)
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'private@gmail.com').first():
    #     user = User(email='private@gmail.com',
    #                 password='private',
    #                 sectionid=privateworldid,
    #                 sectionname=privateworldname,
    #                 role='Agent')
    #     # user.sections.append(Section(, ))
    #     #
    #     # agentrole = Role.query.filter(Role.name == 'Agent').first()
    #     # user.roles.append(agentrole)
    #     db.session.add(user)
    #     db.session.commit()

    # if not User.query.filter(User.email == 'user1@mechdemo.com').first():
    #     user = User(email='user1@mechdemo.com',
    #                 password='user1password',
    #                 sectionid=mechdemoid,
    #                 sectionname=mechdemoname,
    #                 first_name='Bob',
    #                 last_name='Smith',
    #                 role='Agent')
    #     db.session.add(user)
    #     db.session.commit()
    #
    # if not User.query.filter(User.email == 'user2@mechdemo.com').first():
    #     user = User(email='user2@mechdemo.com',
    #                 password='user2password',
    #                 sectionid=mechdemoid,
    #                 sectionname=mechdemoname,
    #                 first_name='Jane',
    #                 last_name='Doe',
    #                 role='Agent')
    #     db.session.add(user)
    #     db.session.commit()
    #
    # if not User.query.filter(User.email == 'o.petrenko@gmail.com').first():
    #     user = User(email='o.petrenko@gmail.com',
    #                 password='password',
    #                 sectionid=mechdemoid,
    #                 sectionname=mechdemoname,
    #                 first_name='Oleg',
    #                 last_name='Petrenko',
    #                 role='Agent')
    #     db.session.add(user)
    #     db.session.commit()
    #
    # if not User.query.filter(User.email == 'bob@bob.com').first():
    #     user = User(email='bob@bob.com',
    #                 password='password',
    #                 sectionid=mechdemoid,
    #                 sectionname=mechdemoname,
    #                 first_name='Bob',
    #                 last_name='Structure',
    #                 role='Agent')
    #     db.session.add(user)
    #     db.session.commit()
    #
    # if not User.query.filter(User.email == 'jane@jane.com').first():
    #     user = User(email='jane@jane.com',
    #                 password='password',
    #                 sectionid=mechdemoid,
    #                 sectionname=mechdemoname,
    #                 first_name='Aero',
    #                 last_name='Jane',
    #                 role='Agent')
    #     db.session.add(user)
    #     db.session.commit()
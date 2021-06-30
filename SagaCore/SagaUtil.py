import os
import re
import warnings
# from SagaDB.UserModel import User, Role


def latestFrameInBranch(path):
    # add comment
    revnum = 0;
    latestrev= 'Rev0.yaml'
    try:
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml', fn)
            if int(m.group(1)) > revnum:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum
    except:
        return latestrev, revnum


def getFramebyRevnum(path, revnum):
    # add comment

    if revnum:
        if os.path.exists(os.path.join(path, 'Rev' + str(revnum) + ".yaml")):
            # if revnum is a numeric string and that yaml exists, return filepath
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
        else:
            # Code should come here most of the time /
            latestrev, revnum = latestFrameInBranch(path)
            if revnum==0:
                warnings.warn("Cannot find reasonable Rev/Frame in " + path, Warning)
                return latestrev, revnum
            else:
                return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
    else:
        # only gets here if is None,
        if os.path.exists(path):
            latestrev, revnum = latestFrameInBranch(path)
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
        else:
            return os.path.join(path, 'Rev0.yaml'), 0

import yaml

class DatabaseSagaYaml():

    def __init__(self, yamlname):
        self.yamlname = yamlname
        self.rolenames = {}
        self.users = {}
        self.sectionids = {}
        try:
            with open(yamlname, 'r') as yfn:
                dbdict = yaml.load(yfn, Loader=yaml.FullLoader)
            self.rolenames= dbdict['rolenames']
            self.users = dbdict['users']
            self.sectionids = dbdict['sectionids']
        except Exception as e:
            warnings.warn('unable to load dbyaml file')

        # for ind,sectionid in enumerate(basesectionids):
        #     self.sectionids[sectionid] = basesectiondescrip[ind]

    @classmethod
    def initiate(cls, yamlname):
        dbyaml = cls(yamlname)
        return dbyaml

    def updatefromdb(self, User, Role, UserRoles, UserSections, Section):
        for u in User.query.all():
            self.users[u.id] = {'email':u.email,
                                'password':u.password,
                                'first_name':u.first_name,
                                'last_name':u.last_name,
                                'currentsection_id':u.currentsection_id,
                                'sections':[],
                                'roles':[]}
        for role in Role.query.all():
            self.rolenames[role.id]={'name':role.name}
        for sect in Section.query.all():
            self.sectionids[sect.id]={'sectionname':sect.sectionname, 'sectionid':sect.sectionid}
        for userrole in UserRoles.query.all():
            self.users[userrole.user_id]['roles'].append(self.rolenames[userrole.role_id]['name'])
        for usersection in UserSections.query.all():
            self.users[usersection.user_id]['sections'].append(self.sectionids[usersection.section_id]['sectionid'])

    def dictify(self):
        dictout = {}
        for key, value in vars(self).items():
            if key=='yamlname':
                continue
            dictout[key] = value
        return dictout

    def writeoutyamlfile(self):
        outyaml = open(os.path.join(self.yamlname), 'w')
        yaml.dump(self.dictify(), outyaml)
        outyaml.close()



from flask_mail import Message,Mail
from flask import current_app
from SagaCore.Container import Container
from SagaCore.Section import Section
from SagaCore.Track import FileTrack
from datetime import datetime
from SagaDB.UserModel import User

def prepcontent(mailjobs,email, fileheader, filetrack, user, upcont:Container,commitmsg,committime,newrevnum):
    if email in mailjobs.keys():
        mailjobs[email]['updatedfiles'][fileheader]=filetrack
    else:
         mailjobs[email]={
                'title': "Notice your upstream container " + upcont.containerName + "  has been updated",
                'commitmessage': commitmsg,
                'committedby': user.first_name + ' ' + user.last_name + ', ' + user.email,
                'committime': datetime.fromtimestamp(committime).isoformat(),
                'newrev': newrevnum,
                'updatedfiles' :{fileheader: filetrack}
         }
    return mailjobs

class MailSender():
    # This class takes care of sending emails to notify downstream components files are updated.
    def __init__(self):
        self.mail = Mail(current_app)
        self.mailjobs={} ## Mailjobs keys are the emails and the values are the content
        self.thismailjobs={}

    def prepareMailDownstream(self,recipemail, fileheader, filetrack:FileTrack, user, upcont:Container,commitmsg,committime,newrevnum):

        if type(recipemail) is list:
            for email in recipemail:
                self.mailjobs = prepcontent(self.mailjobs, email,fileheader, filetrack, user, upcont,commitmsg,committime,newrevnum)
        elif type(recipemail) is str:
            self.mailjobs = prepcontent(self.mailjobs, recipemail, fileheader, filetrack, user, upcont, commitmsg,
                                        committime, newrevnum)

    def prepareMailthisContainer(self,thiscontainer:Container, updatedfiles,user,commitmsg,committime,newrevnum):

        for email in thiscontainer.allowedUser:
            self.thismailjobs[email] = {
            'title': "Notice your container " + thiscontainer.containerName + "  has been updated",
            'commitmessage': commitmsg,
            'committedby': user.first_name + ' ' + user.last_name + ', ' + user.email,
            'committime': datetime.fromtimestamp(committime).isoformat(),
            'newrev': newrevnum,
            'updatedfiles' : updatedfiles}

    def containerAddSagaUser(self, email, cont:Container, sourceuser: User, timestamp):
        title = "Notice:  You have been added contributor to the Container "+ cont.containerName
        msg = Message( title,
                      recipients=[email])
        emailcontent = title + '\n'
        emailcontent = emailcontent + 'You now have full rights to edit container '+ cont.containerName + '\n'
        emailcontent = emailcontent + 'User ' + sourceuser.first_name + ' ' + sourceuser.last_name + ' added you on UTC Time' + datetime.fromtimestamp(timestamp).isoformat() +  '\n'

        msg.body = emailcontent
        # msg.html = "<b>emailcontent</b>"
        self.mail.send(msg)

    def sectionAddNonSagaUser(self,email, sect:Section, inviteruser:User):
        title = "Notice: You have been invited to a Project in Saga , " + sect.sectionname
        msg = Message(title,
                      recipients=[email])
        emailcontent = title + '\n'
        emailcontent = emailcontent + 'You have been invited to a Saga project ' + sect.sectionname + '\n'

        emailcontent = emailcontent + 'User ' + inviteruser.first_name + ' ' + inviteruser.last_name + ' added you \n'

        msg.body = emailcontent
        # msg.html = "<b>emailcontent</b>"
        self.mail.send(msg)

    def containerAddNonSagaUser(self,email, cont:Container, sourceuser: User, timestamp):
        title = "Notice:  You have been added contributor to the Container " + cont.containerName
        msg = Message(title,
                      recipients=[email])
        emailcontent = title + '\n'
        emailcontent = emailcontent + 'You are being invited to Saga to edit ' + cont.containerName + '\n'

        emailcontent = emailcontent + 'User ' + sourceuser.first_name + ' ' + sourceuser.last_name + ' added you on ' + datetime.fromtimestamp(
            timestamp).isoformat() + '\n'

        msg.body = emailcontent
        # msg.html = "<b>emailcontent</b>"
        self.mail.send(msg)


    def sendMail(self):

        for recipemail, content in self.mailjobs.items():
            msg = Message(content['title'],recipients=[recipemail])
            emailcontent = content['title'] + '\n'
            emailcontent = emailcontent + 'Committed By ' + content['committedby'] + ' on ' + content['committime'] + '\n'
            emailcontent = emailcontent + ' The Commit Message : ' + content['commitmessage'] +  '\n'
            for fileheader, filetrack in content['updatedfiles'].items():
                if type(filetrack)==FileTrack:
                    emailcontent = emailcontent + ' Filehandle  ' + fileheader + ' : ' + filetrack.filename + ' is updated \n'
                else:
                    emailcontent = emailcontent + ' Filehandle  ' + fileheader + ' : ' + filetrack.folderpath + ' is updated \n'


            msg.body = emailcontent
            # msg.html = "<b>emailcontent</b>"
            self.mail.send(msg)

        for recipemail, content in self.thismailjobs.items():
            msg = Message(content['title'],recipients=[recipemail])
            emailcontent = content['title'] + '\n'
            emailcontent = emailcontent + 'Committed By ' + content['committedby'] + ' on ' + content['committime'] + '\n'
            emailcontent = emailcontent + ' The Commit Message : ' + content['commitmessage'] +  '\n'
            for fileheader, filetrack in content['updatedfiles'].items():
                if type(filetrack)==FileTrack:
                    emailcontent = emailcontent + ' File  ' + fileheader + ' : ' + filetrack.entity + ' is updated \n'
                else:
                    emailcontent = emailcontent + ' Folder  ' + fileheader + ' : ' + filetrack.entity + ' is updated \n'

            msg.body = emailcontent
            # msg.html = "<b>emailcontent</b>"
            self.mail.send(msg)

from flask_mail import Message,Mail
from flask import current_app
from SagaCore.Container import Container
from datetime import datetime

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

    def prepareMail(self,recipemail, fileheader, filetrack, user, upcont:Container,commitmsg,committime,newrevnum):

        if type(recipemail) is list:
            for email in recipemail:
                self.mailjobs = prepcontent(self.mailjobs, email,fileheader, filetrack, user, upcont,commitmsg,committime,newrevnum)
        elif type(recipemail) is str:
            self.mailjobs = prepcontent(self.mailjobs, recipemail, fileheader, filetrack, user, upcont, commitmsg,
                                        committime, newrevnum)

    def sendMail(self):

        for recipemail, content in self.mailjobs.items():
            msg = Message(content['title'],recipients=[recipemail])
            emailcontent = content['title'] + '\n'
            emailcontent = emailcontent + 'Committed By ' + content['committedby'] + ' on ' + content['committime'] + '\n'
            emailcontent = emailcontent + ' The Commit Message : ' + content['commitmessage'] +  '\n'
            for fileheader, filetrack in content['updatedfiles'].items():
                emailcontent = emailcontent + ' Filehandle  ' + fileheader + ' : ' + filetrack.file_name + ' is updated \n'


            msg.body = emailcontent
            # msg.html = "<b>emailcontent</b>"
            self.mail.send(msg)
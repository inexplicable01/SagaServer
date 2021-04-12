from flask_restful import Resource
#from flask import Flask, send_file, send_from_directory, safe_join, abort
from flask import render_template
from flask_mail import Message,Mail
from flask import current_app

class MailTestView(Resource):



    def __init__(self, rootpath):
        self.rootpath = rootpath
        self.mail = Mail(current_app)

    def get(self):

        msg = Message("Notice your upstream container has been updated",
                      recipients=["waichak.luk@gmail.com"])
        msg.body = "testing"
        msg.html = "<b>testing</b>"
        self.mail.send(msg)
        return 'Message seems to be sent'


from flask_restful import Resource
#from flask import Flask, send_file, send_from_directory, safe_join, abort
from flask import render_template

Rev = 'Rev'

class HelloView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self):
        message = 'Welcome to Saga Version Control  download Saga here'
        return render_template('index.html', message=message)


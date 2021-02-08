from flask_restful import Resource

Rev = 'Rev'

class HelloView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self):
        return {"response": "Hello World"}


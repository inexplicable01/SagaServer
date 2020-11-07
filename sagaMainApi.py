import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
import json
import gridfs
import re
from SagaApp.Files import Files
from SagaApp.FrameView import FrameView
from SagaApp.ContainerView import ContainerView


app = Flask(__name__)
api = Api(app)

rootpath = os.path.dirname(__file__)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp4'}

app.config["MONGO_URI"] = "mongodb+srv://fatpanda:5WvwwkfDfUm2nqbd@cluster0.pg93y.mongodb.net/blog?retryWrites=true&w=majority"

mongo = PyMongo(app)

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except:
        return False

class HelloWorld(Resource):
    def get(self):
        return{"data":"hello w5orld, yo5u got ge44t"}

class BasicWorld(Resource):
    def get(self):
        return{"data":"Basic"}

api.add_resource(HelloWorld, "/helloworld/")

def allowed_file(file_name):
    return '.' in file_name and \
           file_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Upload_file(Resource):
    def get(self):
        fs = gridfs.GridFS(mongo.db)
        for grid_out in fs.find({"file_name":"LongVideo.mp4"}):
            videofile=grid_out
        fileb = videofile.read()

        return make_response(fileb)

    def post(self):
        # check if the post request has the file part
        print(request)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without file_name
        if file.file_name == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.file_name):
            file_name = secure_filename(file.file_name)
            try:
                # mongo.db.posts.insert_one({})
                fs = gridfs.GridFS(mongo.db)
                fileb = file.read()
                with open('plainold.mp4', 'wb') as newfile:
                    newfile.write(fileb)
                newfile.close()
                storageinfo = fs.put(fileb,
                                     file_name=file_name
                                     )
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
                found = mongo.db.posts.find({"slug": "another-post"})[0]
                stufftoreturn={}
                for key, value in found.items():
                    if is_jsonable(value):
                        stufftoreturn[key] = value
                stufftoreturn = json.dumps(stufftoreturn)
                print(stufftoreturn)
            except:
                return {"balh":os.getcwd()}
            return stufftoreturn
        return {"data": "postingsomething"}

    def delete(self):
        fs = gridfs.GridFS(mongo.db)
        for grid_out in fs.find({"file_name":"LongVideo.mp4"}):
            print(grid_out)
            fs.delete(grid_out._id)
        return {"data":"Todelete"}

class Get_file(Resource):
    def get(self, file_name):
        return {"data":"something"}



api.add_resource(Upload_file, "/UPLOADS")
api.add_resource(ContainerView, "/CONTAINERS",  resource_class_kwargs={'rootpath': rootpath})
api.add_resource(FrameView, "/FRAMES",  resource_class_kwargs={'rootpath': rootpath})
api.add_resource(Files, "/FILES",  resource_class_kwargs={'rootpath': rootpath})




import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import json
import gridfs

app = Flask(__name__)
api = Api(app)


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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Upload_file(Resource):
    def get(self):
        fs = gridfs.GridFS(mongo.db)
        for grid_out in fs.find({"filename":"LongVideo.mp4"}):
            videofile=grid_out
        fileb = videofile.read()

        return make_response(fileb)

    def post(self):
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                # mongo.db.posts.insert_one({})
                fs = gridfs.GridFS(mongo.db)
                fileb = file.read()
                storageinfo = fs.put(fileb,
                                     filename=filename
                                     )
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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
        for grid_out in fs.find({"filename":"LongVideo.mp4"}):
            print(grid_out)
            fs.delete(grid_out._id)
        return {"data":"Todelete"}

class Get_file(Resource):
    def get(self, filename):
        return {"data":"something"}

api.add_resource(Upload_file, "/UPLOADS")

if __name__ == "__main__":
    app.run(debug=True)


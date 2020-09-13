import os
from flask import Flask,flash, request, redirect, url_for,send_from_directory
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename

app = Flask(__name__)
api = Api(app)

UPLOAD_FOLDER = os.getcwd()+'/test'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        return {"data":"getting file"}

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
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except:
                return {"balh":os.path.join(app.config['UPLOAD_FOLDER'], filename)}
            return {"data": "postingsomething"}
            # redirect(url_for('upload_file', filename=filename))
        return  {"data": "postingsomething"}

# class Get_file(Resource):
#     def get(self, filename):
#         return {"data":"something"}

api.add_resource(Upload_file, "/UPLOADS")







# if __name__ == "__main__":
#     app.run(debug=True)


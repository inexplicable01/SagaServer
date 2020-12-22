import os
from flask_restful import Api, Resource
from SagaApp.Files import Files
from SagaApp.FrameView import FrameView
from SagaApp.ContainerView import ContainerView
from SagaApp.ResetView import Reset
from SagaApp import app


if __name__ == "__main__":
    api = Api(app)
    rootpath = os.path.dirname(__file__)

    # api.add_resource(ContainerView, "/CONTAINERS",  methods=['GET', 'POST'], resource_class_kwargs={'rootpath': rootpath})
    api.add_resource(ContainerView, "/CONTAINERS/<command>", methods=['GET', 'POST'],
                     resource_class_kwargs={'rootpath': rootpath})
    api.add_resource(FrameView, "/FRAMES", resource_class_kwargs={'rootpath': rootpath})
    api.add_resource(Files, "/FILES", resource_class_kwargs={'rootpath': rootpath})
    api.add_resource(Reset, "/RESET", resource_class_kwargs={'rootpath': rootpath})
    app.run(debug=True)
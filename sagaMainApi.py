
import logging
from SagaAPI import createSagaApp
# from waitress import serve
# from logging.handlers import RotatingFileHandler
# from datetime import datetime
# import traceback
# import os
from os.path import join, exists
from Config import appdatadir , webserverdir
# logging.basicConfig(filename=join(appdatadir,'info.log'), level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler())


app = createSagaApp()

if __name__ == "__main__":
    logging.info('Containers Being loaded from ' + appdatadir)
    logging.info('Source Code running from ' + webserverdir)
    app.run(debug=True, host='127.0.0.1', port='5000')





import logging
from SagaAPI import createSagaApp

from logging.handlers import RotatingFileHandler
from datetime import datetime
import traceback
import os
# from mypackage import wsgiapp
from waitress import serve
from paste.deploy import loadapp
from paste.translogger import TransLogger

# os.path.getcwd()
# print()
from os.path import join, exists
from Config import appdatadir, port
logging.basicConfig(filename=join(appdatadir,'info.log'), level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())

# blah = loadapp('config:'+ os.path.abspath('config.ini'))
try:
    sagaapp = createSagaApp()
    # serve(blah)
    serve(TransLogger(sagaapp, setup_console_handler=False),listen='*:' + port)
except Exception as e:
    with open(join(appdatadir,'error.txt'),'a+') as errorfile:
        errorfile.write(datetime.utcnow().isoformat() + str(e) + '\n')
        errorfile.write(datetime.utcnow().isoformat() + 'ErrorType' + str(e) + '\n')
        errorfile.write(datetime.utcnow().isoformat() + 'Traceback' + traceback.format_exc() + '\n')
        errorfile.write('\n')
# serve()
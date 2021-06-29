
import logging
from SagaAPI import create_SagaApp
from waitress import serve
from logging.handlers import RotatingFileHandler
from datetime import datetime
import traceback
import os
from os.path import join, exists

appdata = os.getenv('AppData')

print(appdata)
if not exists(join(appdata, 'SagaServer')):
    os.mkdir(join(appdata, 'SagaServer'))

try:
    app = create_SagaApp()

    if __name__ == "__main__":
        logHandler = RotatingFileHandler(join(appdata, 'SagaServer','info.log'), maxBytes=1000, backupCount=1)

        # set the log handler level
        logHandler.setLevel(logging.INFO)

        # set the app logger level
        app.logger.setLevel(logging.INFO)

        app.logger.addHandler(logHandler)
        app.run(debug=True, host='127.0.0.1', port='5001')

except Exception as e:
    with open(join(appdata, 'SagaServer','error.txt'), 'a+') as errorfile:
        # errorfile.write(datetime.now().isoformat() + ': Container: ' + request.form.get('containerID') +'\n')
        errorfile.write(datetime.now().isoformat() + str(e) + '\n')
        errorfile.write(datetime.now().isoformat() + 'ErrorType' + str(e) + '\n')
        errorfile.write(datetime.now().isoformat() + 'Traceback' + traceback.format_exc() + '\n')
        errorfile.write('\n')
    # serve(app)
import os
import yaml
import glob
from SagaCore.Container import Container
from SagaCore.Frame import Frame

def fullFrameHistory(container:Container):
    fullframelist = {}
    yamllist = glob.glob(os.path.join(container.containerworkingfolder, container.currentbranch, '*.yaml'))
    for yamlfn in yamllist:
        pastframe = Frame.loadRefFramefromYaml(yamlfn, container.containerworkingfolder)
        # print(pastframe.commitMessage)
        fullframelist[os.path.basename(yamlfn)] = pastframe.dictify()
        # historyStr = historyStr + pastframe.FrameName + '\t' + pastframe.commitMessage + '\t\t\t\t' + \
        #              time.ctime(pastframe.commitUTCdatetime) + '\t\n'
    return fullframelist
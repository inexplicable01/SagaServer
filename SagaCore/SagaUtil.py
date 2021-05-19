import os
import re
import warnings

def latestFrameInBranch(path):
    # add comment
    revnum = 0;
    latestrev= 'Rev0.yaml'
    try:
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml', fn)
            if int(m.group(1)) > revnum:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum
    except:
        return latestrev, revnum


def FrameNumInBranch(path, revnum):
    # add comment

    if revnum:
        if os.path.exists(os.path.join(path, 'Rev' + str(revnum) + ".yaml")):
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
        else:
            latestrev, revnum = latestFrameInBranch(path)
            if revnum==0:
                warnings.warn("Cannot find reasonable Rev/Frame in " + path, Warning)
            else:
                return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
    else:
        # if none
        if os.path.exists(path):
            latestrev, revnum = latestFrameInBranch(path)
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
        else:
            return os.path.join(path, 'Rev0.yaml'), 0



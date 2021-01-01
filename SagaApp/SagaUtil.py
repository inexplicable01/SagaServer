import os
import re
import warnings

def latestFrameInBranch(path):
    # add comment
    revnum = 0;
    for fn in os.listdir(path):
        m = re.search('Rev(\d+).yaml', fn)
        if int(m.group(1)) > revnum:
            revnum = int(m.group(1))
            latestrev = fn
    return latestrev, revnum


def FrameNumInBranch(path, revnum):
    # add comment
    if revnum:
        if os.path.exists(os.path.join(path, 'Rev')):
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
        else:
            warnings.warn("Rev " + str(revnum) + " doesn't exist in " + path , Warning)
            latestrev, revnum = latestFrameInBranch(path)
            return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum
    else:
        # if none
        latestrev, revnum = latestFrameInBranch(path)
        return os.path.join(path, 'Rev' + str(revnum) + ".yaml"), revnum


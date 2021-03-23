from record.douyu import Douyu
from record.huya import Huya
from record.qie import QieEGame

def RecorderFactory(platform_name):
    if platform_name == "douyu":
        return Douyu()
    elif platform_name == "huya":
        return Huya()
    elif platform_name == "QieEGame":
        return QieEGame()
    else:
        return None

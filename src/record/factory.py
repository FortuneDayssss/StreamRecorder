from record.douyu import Douyu
from record.huya import Huya


def RecorderFactory(platform_name):
    if platform_name == "douyu":
        return Douyu()
    elif platform_name == "huya":
        return Huya()
    else:
        return None

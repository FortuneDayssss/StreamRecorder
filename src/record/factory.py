from record.douyu import Douyu


def RecorderFactory(platform_name):
    if platform_name == "douyu":
        return Douyu()
    else:
        return None

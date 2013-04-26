import commands

def resign(path):
    print commands.getoutput("java -cp re-sign.jar de.troido.resigner.main.Main %s %s" % (path, path.replace('.apk', '-resigned.apk')))
    return path.replace('.apk', '-resigned.apk')

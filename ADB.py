
import commands, sys


sessions = {}
devices = set()

def host(sessionId):
    return sessions[sessionId].host

def quit(sessiondId):
    sessions[sessiondId].quit()

class adb:
    def __init__(self, caps):
        global devices
        if len(devices) > 0:
            # todo, get the api level and compare
            self.device = devices.pop()
        else:
            raise Exception("no devices available")
    def install(self, path):
        cmd("-s %s install \"%s\"" % (self.device[0], path))
    def uninstall(self, package):
        cmd("-s %s uninstall \"%s\"" % (self.device[0], package))
    def instrumentation(self, activity):
        cmd("-s %s shell am instrument -e main_activity %s org.openqa.selendroid/.ServerInstrumentation" % (self.device[0], activity))
    def forward(self):
        cmd("-s %s forward tcp:%d tcp:8080" % self.device)

    @property
    def port(self):
        return self.device[1]

    @property
    def host(self):
        return "http://localhost:%d" % self.device[1]

    @property
    def sessionId(self):
        return self._sessionId

    def setSessionId(self, id):
        global sessions
        print "setting session id with: " + id
        self._sessionId = id
        sessions[id] = self

    def quit(self):
        global sessions
        global devices
        del sessions[self.sessionId]
        devices.add(self.device)

def cmd(c):
    print "adb %s" % c
    out = commands.getoutput("adb %s" % c)
    print out
    return out

def find_devices(port=8090):
    global devices
    for dev in cmd("devices").splitlines()[1:]:
        parts = dev.split("\t")
        if parts[1] == 'device':
            devices.add((parts[0], port))
            port += 1
    if len(devices) == 0:
        raise Exception("no devices found, please make sure you have some connected to your machine: `adb devices`")

if len(sys.argv) > 1:
    try:
        find_devices(int(sys.argv[1]))
    except:
        find_devices()
else:
    find_devices()

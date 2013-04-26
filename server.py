# Apache 2 license... bla bla bla

# Copyright Salesforce.com
# Author: Luke Inman-Semerau

from bottle import redirect, request, response, route, run, template
import ADB, JARSIGN, json, os, requests, time

selendroid_path = JARSIGN.resign(os.path.abspath("selendroid-server.apk"))

@route('/wd/hub/status')
def status():
    return "%d / %d" % (len(ADB.sessions), len(ADB.devices))

@route('/wd/hub/session', method='POST')
def startSession():
    data = request.body.read()
    caps = json.loads(data)['desiredCapabilities']
    adb = ADB.adb(caps)
    adb.uninstall(caps['app.package'])
    adb.uninstall("org.openqa.selendroid")
    if os.path.exists(caps['app.apk']):
        apk_path = caps['app.apk']
    else:
        # todo create apk file from compressed data
        pass

    resigned = JARSIGN.resign(apk_path)
    adb.install(resigned)
    adb.install(selendroid_path)
    adb.instrumentation(caps['app.activity'])
    adb.forward()
    time.sleep(1) # need to give the activity a moment to start up

    print '%s/wd/hub/session' % adb.host
    r = requests.post('%s/wd/hub/session' % adb.host, data=data)
    adb.setSessionId(json.loads(r.text)['sessionId'])
    redirect('/wd/hub/session/' + adb.sessionId)

@route('/wd/hub/session/<path:re:.*>', method=['GET','POST', 'DELETE'])
def forward(path):
    sessionId = path.split("/")[0]
    host = ADB.host(sessionId)
    if request.method == 'GET':
        r = requests.get(host + '/wd/hub/session/' + path)
    elif request.method == 'DELETE':
        r = requests.delete(host + '/wd/hub/session/' + path, data=request.body.read())
        if path == sessionId:
            ADB.quit(sessionId)
    else:
        r = requests.post(host + '/wd/hub/session/' + path, data=request.body.read())
    if "application/json" in r.headers['content-type']:
        return json.loads(r.text)
    return r.text

print "Expecting capabilites in the form of:\n{ 'app.package': 'com.salesforce.chatter', 'app.apk': '/full/path/to/apk', 'app.activity': 'com.salesforce.chatter.Chatter', 'api': 15 }"

run(server='paste', host='0.0.0.0', port=8080)

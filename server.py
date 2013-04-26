# Copyright (c) 2013, Salesforce.com, Inc.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#     Neither the name of Salesforce.com nor the names of its contributors may 
#     be used to endorse or promote products derived from this software without 
#     specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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

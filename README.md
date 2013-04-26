gridb
=====

grid + adb = gridb

for use with (selendroid)[https://github.com/DominikDary/selendroid]

Allows one to control multiple android devices on one host, to be used with selendroid.


Prerequisites
-------------

* pip
* pip install bottle
* pip install Paste
* pip install requests

* JAVA_HOME is set
* adb is on your system path


Running it
----------

    python server.py [port]

port is optional, starts the server on this port, increments number to port forward the adb devices to. Default is 8080 (thus the first device will be on 8081)

Connecting to it
----------------

The desired capabilities need to pass the following values:

    Java:

    DesiredCapabilities caps = DesiredCapabilities.android();
    caps.setCapability("app.apk", new File("myapp.apk").getAbsolutePath()); // this is the path to your apk as it exists on the machine where you are running this gridb server. 
    caps.setCapability("app.package", "com.company.product");
    caps.setCapability("app.activity", "com.company.product.ActivityClass");
    caps.setCapability("api", 15); // not yet being consumed this should be an integer valid values are 10-17
    // caps.setCapability("app.install", false); // assume the app and selendroid are already installed on the apk, will just restart the activity
    
    WebDriver driver = new RemoteWebDriver("http://localhost:8080/wd/hub", caps);
    // note that if you want TouchActions you should use AndroidDriver
    // if you want to FindsById (and not have it translate to xpath) you need to create a new SelendroidDriver Class that 'extends RemoteWebDriver implements HasTouchScreen, TakesScreenshot'

    Python:

    caps = {
        'app.apk' : os.path.abspath('myapp.apk'),
        'app.package' : 'com.company.product',
        'app.activity' : 'com.company.product.ActivityClass',
        'api' : 15,
        # 'app.install' : False
    }
    driver = webdriver.Remote('http://localhost:8080/wd/hub', caps)

Contributing
------------

Pull Requests welcome as long as they are clear on what they are for and add value :)

feel free to discuss anything with me on IRC at freenode in either #selenium or #selendroid

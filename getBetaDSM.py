import os
import sys
import urllib
import httplib
import ConfigParser
from time import sleep


def checkURL(url):
    f = urllib.urlopen(url)
    return f.code == 200


def readConf(confFile) :
    configuration = ConfigParser.ConfigParser()
    file = os.path.join(os.path.dirname(sys.argv[0]), confFile)
    if not os.path.isfile(file):
        sys.exit("Config file not found")
    try:
        fp = open(file, "r")
        configuration.readfp(fp)
        fp.close()
    except IOError:
        sys.exit("Config file not readable")
    return configuration


def pushOver(apiToken, userKey, title, message) :
    cx = httplib.HTTPSConnection("api.pushover.net:443")
    cx.request(
        "POST",
        "/1/messages",
        urllib.urlencode({
            "token": apiToken,
            "user": userKey,
            "title": title,
            "message": message
            }),
        {"Content-type": "application/x-www-form-urlencoded"}
    )


def main():
    # Read config
    conf = readConf('config.cfg')
    interval = int(conf.get('Main', 'interval'))
    model = conf.get('Main', 'model')
    dlPath = conf.get('Synology', 'dlPath')
    dsmFolder = conf.get('Synology', 'dsmFolder')
    PO_api = conf.get("Pushover", "api_token")
    PO_key = conf.get("Pushover", "user_key")

    # Check if DSM is released
    while not checkURL(dlPath + dsmFolder):
        print 'DSM not found. Next try in ' + str(interval) + ' seconds.'
        sleep(interval)

    # If yes, notify
    print 'DSM has been released!!!'
    pushOver(PO_api, PO_key, 'DSM has been released', 'Script will now try to find DSM version')

    # Try to find DSM version and download .pat file
    dsmVersionMin = int(conf.get('Synology', 'dsmVersionMin'))
    dsmVersionMax = int(conf.get('Synology', 'dsmVersionMax'))
    dsmVersion = None
    while not dsmVersion:
        for i in xrange(dsmVersionMin,dsmVersionMax):
            filename = 'DSM_' + model + '_' + str(i) + '.pat'
            if checkURL(dlPath + dsmFolder + filename):
                dsmVersion = i
                urllib.urlretrieve(dlPath + dsmFolder + filename, filename)
                print 'DSM version has been found: ' + str(dsmVersion)
                pushOver(PO_api, PO_key, 'DSM version has been found',
                    'Version: ' + str(dsmVersion) + ' has been downloaded!')
                break
        if not dsmVersion:
            print 'DSM version not found. Next try in ' + str(interval) + ' seconds.'
            sleep(interval)

if __name__ == '__main__':
    main()
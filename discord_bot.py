#!/usr/bin/env python
from datetime import datetime
import Ice
import logging
import os
import pytz
import requests
import sys
Ice.loadSlice('', ['-I' + Ice.getSliceDir(), 'Murmur.ice'])
import Murmur

WEBHOOK_URL = os.environ['MURMUR_WEBHOOK_URL']
HOST = os.environ['MURMUR_HOST']
PORT = os.environ['MURMUR_PORT']

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]  %(message)s')


def sendToDiscord(message):
    data = {'content': message}
    logging.info('Send to Discord: ' + str(data))
    req = requests.post(
        WEBHOOK_URL,
        json=data,
        headers={'Content-type': 'application/json'}
    )
    logging.info(req.status_code)


class ServerCallbackI(Murmur.ServerCallback):
    def __init__(self, server, adapter):
        self.server = server

    def userConnected(self, user, current=None):
        message = user.name + ' has connected'
        sendToDiscord(message)

    def userDisconnected(self, user, current=None):
        message = user.name + ' has disconnected'
        sendToDiscord(message)


if __name__ == "__main__":
    logging.info('Start the script')

    prop = Ice.createProperties(sys.argv)
    prop.setProperty("Ice.ImplicitContext", "Shared")
    prop.setProperty('Ice.Default.EncodingVersion', '1.0')

    idd = Ice.InitializationData()
    idd.properties = prop

    ice = Ice.initialize(idd)

    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy('Meta:tcp -h ' + HOST + ' -p ' + PORT))
    adapter = ice.createObjectAdapterWithEndpoints("Callback.Client", "tcp")
    adapter.activate()

    for server in meta.getBootedServers():
        serverR = Murmur.ServerCallbackPrx.uncheckedCast(adapter.addWithUUID(ServerCallbackI(server, adapter)))
        server.addCallback(serverR)
        logging.info('Initialize callbacks')

    try:
        ice.waitForShutdown()
        logging.info('Waitint for events...')
    except KeyboardInterrupt:
        ice.shutdown()
        logging.info('Shutting down')

    ice.destroy()

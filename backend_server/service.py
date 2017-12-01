# -*- coding: utf-8 -*-

""" Backend service """

import os
import json

import pyjsonrpc

import operations

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "common", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

SERVER_HOST = CONFIG['rpc']['server']['hostname']
SERVER_PORT = CONFIG['rpc']['server']['port']


class RequestHandler(pyjsonrpc.HttpRequestHandler):
    """ RPC request handler """

    @pyjsonrpc.rpcmethod
    def getAverageListingPrices(self):
        """get Average Listing Prices"""
        print "getAverageListingPrices is called"
        return operations.getAverageListingPrices()

    @pyjsonrpc.rpcmethod
    def getListings(self, region):
        """get Listing Prices for the given region"""
        print "getListings(%s) is called" % region
        return operations.getListings(region)


# Threading HTTP-Server.
HTTP_SERVER = pyjsonrpc.ThreadingHttpServer(
    server_address=(SERVER_HOST, SERVER_PORT),
    RequestHandlerClass=RequestHandler
)

print "Starting HTTP server on %s:%d" % (SERVER_HOST, SERVER_PORT)

HTTP_SERVER.serve_forever()

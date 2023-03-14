from abc import ABC
from http.server import HTTPServer
from typing import List
from tornado.httpserver import HTTPServer
CURR_HTTP_SERVER_TYPE=HTTPServer

from .. import mutualcls
from ..webserver.tornado import tornadoserv 


class WebServer(ABC):
    ws_clients:List[mutualcls.WSClient]=[]

class TornadoInterface(WebServer):
    @property
    def ws_clients(self):
        return self.request_callback.wsClients      #TODO костыль убрать!

from tornado.httpserver import HTTPServer
CURR_HTTP_SERVER_TYPE=HTTPServer

def setHTTPServer(params, web_handlers, data)->CURR_HTTP_SERVER_TYPE:
    return tornadoserv.TornadoHTTPServerInit(params, web_handlers, data)

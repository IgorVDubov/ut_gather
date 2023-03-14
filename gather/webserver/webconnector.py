from abc import ABC
from typing import List

from .. import mutualcls
from ..webserver.tornado import tornadoserv 


class WebServer(ABC):
    ws_clients:List[mutualcls.WSClient]=[]

class TornadoInterface(WebServer):
    @property
    def ws_clients(self):
        return self.request_callback.wsClients

def setHTTPServer(params, web_handlers, data):
    return tornadoserv.TornadoHTTPServerInit(params, web_handlers, data)

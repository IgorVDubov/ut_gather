from dataclasses import dataclass
from typing import List

from channels.channelbase import ChannelsBase

@dataclass
class DataContainer():
    '''
    class for HTTP server data exchanging
    '''
    users:List
    channelBase:ChannelsBase
    subscribe_channels:List

class WSClient():
    '''
    web socket client 
    '''
    def __init__(self, ws_client) -> None:
        self.client=ws_client
        self.subscribe=[]
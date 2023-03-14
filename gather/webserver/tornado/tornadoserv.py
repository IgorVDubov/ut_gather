import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os.path  
from logger import logger
import json
from typing import *

from ... import defaults 
users = defaults.users
                            
class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def getUser(self):
        '''
        return dict with user data if user belongs to project with projectId or None
        '''
        if not self.current_user:
            return None
        try:
            userId = int(tornado.escape.xhtml_escape(self.current_user))
            # user=[user for user in self.application.data.users if user['id']==userId][0]
            if  user:=next(filter(lambda user: user['id'] == userId, self.application.data.users)):  
                logger.debug('user '+user['login']+' ok')
                return user
            else:
               return None
        except TypeError or ValueError:
            return None

class MainHtmlHandler(BaseHandler):
    def get(self):
        print ('in MainHtmlHandler')
        if user:=self.getUser():
            print('user '+user['login']+' ok, render stat.html')
            # logger.debug('user '+user['login']+' ok, render stat.html')
            self.render('index.html', user=user['login'],wsserv=self.application.settings['wsParams'])
        else:
            self.redirect("/login")
    
    def post(self):
            pass
      
    
class RequestHtmlHandler(BaseHandler):
    
    def post(self):
        self.set_header("Content-Type", "application/json")
        request=json.loads(self.request.body)
        if user:=self.getUser():
            if request.get('type')=='allStateQuerry':
                logger.log('MESSAGE',f'client {user["login"]} do allStateQuerry from ip:{self.request.remote_ip}.')
                self.write(json.dumps(self.application.data_container.channelBase.toDict(), default=str))
    
    
    def get(self):
        pass
        self.set_header("Content-Type", "application/x-www-form-urlencoded")
        requestHeader=self.request.headers
        print (f'GET request!!!!!!!!!!!!!')
        print (f'requestHeader:{requestHeader}')
        requestBody=self.request.body
        print (f'requestBody:{requestBody}')

class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, clbk):
        self.callback=clbk
    def __init__(self, *args, **kwargs):
        self.id = None
        super(WSHandler, self).__init__(*args, **kwargs)
    
    # def check_origin(self, origin: str) -> bool:
        #print(f'origin:{origin}')
        # сюда можно проверку хостов с которых запросы
        #return self.current_user != None  #ws запросы только если кто-то залогинился перед этим
        # return True
        #return super().check_origin(origin)

    def open(self):
            logger.info(f'Web Socket open, IP:{self.request.remote_ip} Online {len(self.application.wsClients)} clients')
            # if self.request.headers['User-Agent'] != 'UTHMBot':  #не логгируем запросы от бота и не включаем его в список ws рассылки
            #     #if tornado.escape.xhtml_escape(self.get_secure_cookie("user")) in [_ for _ in allUsers(users)]:
            if self not in self.application.wsClients:
                self.application.wsClients.append(self)
            #         user=[user for user in globals.users if user['id']==int(tornado.escape.xhtml_escape(self.get_secure_cookie("user")))][0]
            #         logger.info(f'Web Socket open, IP:{self.request.remote_ip},  user:{user.get("login")}, Online {len(globals.wss)} clients')
            #     else:
            #         logger.log ('LOGIN',f'websocket user {tornado.escape.xhtml_escape(self.get_secure_cookie("user"))} not autirized , IP:{self.request.remote_ip}')
            #         self.close()
        
    def on_message(self, message):
        try:
            jsonData = json.loads(message)
        except json.JSONDecodeError:
            logger.error ("json loads Error for message: {0}".format(message))
        else:
            if jsonData['type']=="allStateQuerry":
                logger.debug ("ws_message: allStateQuerry")
                msg = {'type':'mb_data','data': None}
                json_data = json.dumps(msg, default=str)
                self.write_message(json_data)
            elif jsonData['type']=="testMsg":
                pass
            elif jsonData['type']=="msg":
                logger.debug (f"ws_message: {jsonData['data']}")
            else:
                logger.debug('Unsupported ws message: '+message)        
 
    def on_close(self):
        # if self.request.headers['User-Agent'] != 'UTHMBot':  #не логгируем запросы от бота
        #     user=[user for user in globals.users if user['id']==int(tornado.escape.xhtml_escape(self.get_secure_cookie("user")))][0]
        #     logger.info(f' User {user.get("login")} close WebSocket. Online {len(self.application.wsClients)-1} clients')
        if self in self.application.wsClients:
            self.application.wsClients.remove(self)
        # if len(globals.wss)==0:
            # print('No online users, callback stops')
            # self.callback.stop()


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument("name", "")
        
        for user in self.application.data.users:
            if user['login']==username:
                logger.log('DEBUG',f"Try login {username}, user ok, ip:{self.request.remote_ip}")
                #self.set_secure_cookie("user", username, expires_days=180)
                self.set_secure_cookie("user", str(user.get('id') ), expires_days=180)
                self.redirect("/")
                return
        # no such user
        logger.log('DEBUG',f"Try login {username}, user wrong , ip:{self.request.remote_ip}")
        self.redirect("/login")

class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")

class Aplication(tornado.web.Application):
    def __init__(self, handlers, data_container:dict, default_host = None, transforms = None, **settings: Any) -> None:
        self.data=data_container
        self.wsClients=list()
        super().__init__(handlers, default_host, transforms, **settings)


def TornadoHTTPServerInit(params, handlers, data_container):
    # handlers=[
    #     (r"/", MainHtmlHandler),
    #     (r"/login",LoginHandler),
    #     (r"/request", RequestHtmlHandler),
    #     (r'/ws', WSHandler, dict(clbk=None)),
    #     (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": './webserver/webdata/static'}),
    #     (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': './webserver/webdata/static'}),
    #     (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': './webserver/webdata/static'}),
    #     (r'/images/(.*)', tornado.web.StaticFileHandler, {'path': './webserver/webdata/static'}),
    #     (r'/(favicon.ico)', tornado.web.StaticFileHandler, {'path': './webserver/webdata/static'})
    #     ]

    settings = {
        'static_path':  os.path.join(*params.get ('static_path','web/webdata').split('/')),
        'template_path': os.path.join(*params.get ('static_path','web/webdata').split('/')),
        'debug': params.get ('debug',True),
        'cookie_secret':params.get ('cookie_secret',"61ofdgETxcvGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="),    #TODO при необходимости вынести в envvar
        'wsParams':params.get('wsserver','ws://localhost:8888/ws')
        }
    http_server=tornado.httpserver.HTTPServer(Aplication(handlers, data_container, **settings))
    http_server.listen(params.get('port',8888))
    return http_server
        
        
        # http_server = tornado.httpserver.HTTPServer(application,ssl_options={"certfile": ".\ssl\device.crt","keyfile":".\ssl\device.key"})
        #self.server=tornado.httpserver.HTTPServer(application)
        # http_server = tornado.httpserver.HTTPServer(application,ssl_options={"certfile": "utrack_test_1.p12","keyfile":"root_cert.crt"})

# def start(self):    
#     print ('torando server starts')
#     self.main_loop = tornado.ioloop.IOLoop.current()
#     self.main_loop.make_current()
#     self.main_loop.start()


#a_loop=main_loop.asyncio_loop


# import asyncio

# loop=asyncio.get_event_loop()
# print(a_loop==loop)

# from source_pool import SourcePool
# from globals import ModuleList

# pool=SourcePool(ModuleList,a_loop)
# pool.start()

# try:
#     print('server satrt')
#     main_loop.start()
# except: #KeyboardInterrupt:
#     main_loop.stop ()
    

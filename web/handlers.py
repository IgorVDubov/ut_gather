import json
import os.path
from datetime import datetime

import tornado
import tornado.escape
import tornado.web
import tornado.websocket
from loguru import logger

from models import User
from config import CHECK_AUTORIZATION, DEFAULT_USER
from gathercore.classes import  SubscriptChannelArg
from gathercore.webserver.classes import WSClient
from gathercore.webserver.webconnector import BaseRequestHandler, BaseWSHandler

from gathercore.channels.channels import parse_attr_params
from settings import web_server_path_params as path_params
from config import http_server_params

import logics
import dataconnector as dc
import settings
import projectglobals as project_globals

RequestHandlerClass = BaseRequestHandler
StaticFileHandler = tornado.web.StaticFileHandler
WebSocketHandler = BaseWSHandler


class BaseHandler(RequestHandlerClass):
    user: User

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def getUser(self)->User | None:
        '''
        return dict with user data if user belongs to project with projectId or None
        '''
        if not self.current_user:
            return None
        try:
            userId = int(tornado.escape.xhtml_escape(self.current_user))
            # user=[user for user in self.application.data.users if user['id']==userId][0]
            if user := next(filter(lambda user: user['id'] == userId, self.application.data.users), None):
                # logger.debug('user '+user['login']+' ok')
                return user
            else:
                return None
        except TypeError or ValueError:
            return None

    def check_user(check_authorization=True):
        def decorator(handler_func):
            def wrapper(self, *args, **kwargs):
                user = {}
                if not check_authorization:
                    self.user = DEFAULT_USER
                    handler_func(self, *args, **kwargs)
                elif user := self.getUser():
                    self.user = user
                    handler_func(self, *args, **kwargs)
                else:
                    self.redirect("/login")
            return wrapper
        return decorator


class MainHtmlHandler(BaseHandler):
    # @BaseHandler.check_user(CHECK_AUTORIZATION)
    def get(self):
        # print (f'in MainHtmlHandler, project {PROJECT["name"]}, user {self.user} ')
        # try:
        # machine_id=logics.get_machine_from_user(self.user.get('login'))
        try:
            if arg := self.request.arguments.get('m'):
                machine_id = int(tornado.escape.xhtml_escape(arg[0]))
            else:
                raise KeyError(
                    f'No machine id at index request /?m=xxxx from ip {self.request.remote_ip}')
            logics.check_allowed_machine(machine_id, self.request.remote_ip)
        except (ValueError, KeyError) as ecptn:
            logger.error(ecptn)     #
            return
            # logger.log('ERROR', f'wrong machine id in client login {self.user.get("login")} do get_ch from ip:{self.request.remote_ip}.')
            # self.redirect("/login")

        self.render('index.html',
                    user=machine_id,
                    # user=self.user.get('login'),
                    machine=machine_id,
                    state_channel=str(machine_id)+'.'+settings.STATE_ARG,
                    tech_idle=logics.get_channel_arg(
                        self.application.data.channelBase, machine_id, settings.TECH_IDLE_ARG),
                    causeid_arg=logics.get_causeid_arg(
                        self.application.data.channelBase.get(machine_id)),
                    idle_couses=json.dumps(logics.convert_none_2_str(
                        logics.get_machine_causes)(machine_id), default=str),
                    default_causes=settings.DEFAULT_CAUSES,
                    current_state=logics.convert_none_2_str(logics.get_current_state)(
                        self.application.data.channelBase, machine_id),
                    wsserv=self.application.settings['wsParams'] + \
                    '?m='+str(machine_id),
                    server_time=logics.get_server_time(),
                    techidle_id=settings.TECH_IDLE_ID,
                    # operators=logics.get_machine_operators(machine_id),
                    version=settings.CLIENT_VERSION,
                    )


class WSHandler(WebSocketHandler):
    def open(self):
        try:
            machine_id = int(tornado.escape.xhtml_escape(
                self.request.arguments['m'][0]))
            logics.check_allowed_machine(machine_id, self.request.remote_ip)
        except ValueError as error:
            logger.error(error)
            return
        logger.info(f'Web Socket open, IP:{self.request.remote_ip} ')
        if self not in [client.client for client in self.application.data.ws_clients]:
            self.application.data.ws_clients.append(WSClient(self))
            logger.info(
                f'add, websocket IP:{self.request.remote_ip} Online {len(self.application.data.ws_clients)} clients')

    def on_message(self, message):
        try:
            jsonData = json.loads(message)
            print(jsonData)
        except json.JSONDecodeError:
            logger.error("json loads Error for message: {0}".format(message))
        else:
            if jsonData.get('type') == "curr_operator":
                logger.info(
                    f"ws_message: currentOperator for {jsonData.get('macine_id')} from ip:{self.request.remote_ip}")
                msg = {'type': 'curr_operator', 'data': dc.get_current_operator(
                    jsonData.get('macine_id'))}
                json_data = json.dumps(msg, default=str)
                self.write_message(json_data)
            elif jsonData.get('type') == "get_operator":
                logger.info(
                    f"ws_message: get_operator for {jsonData.get('macine_id')} from ip:{self.request.remote_ip}")
                msg = {'type': 'set_operator', 'data': dc.get_operator(
                    jsonData.get('macine_id'), jsonData.get('operator_id'))}
                json_data = json.dumps(msg, default=str)
                self.write_message(json_data)
            elif jsonData.get('type') == "set_operator":
                logger.info(
                    f"ws_message: set_operator_login for {jsonData.get('macine_id')}, operator {jsonData.get('operator_id')} from ip:{self.request.remote_ip}")
                dc.set_operator_login(jsonData.get(
                    'macine_id'), jsonData.get('operator_id'))
                self.application.data.channelBase.get(jsonData.get('macine_id')).set_arg(
                    'args.operator_id', jsonData.get('operator_id'))
            elif jsonData.get('type') == "logout_operator":
                logger.info(
                    f"ws_message: set_operator_logout for {jsonData.get('macine_id')}, operator {jsonData.get('operator_id')} from ip:{self.request.remote_ip}")
                dc.set_operator_logout(jsonData.get(
                    'macine_id'), jsonData.get('operator_id'))
                msg = {'type': 'curr_operator', 'data': dc.get_current_operator(
                    int(jsonData.get('macine_id')))}
                self.application.data.channelBase.get(jsonData.get(
                    'macine_id')).set_arg('args.operator_id', None)
                json_data = json.dumps(msg, default=str)
                self.write_message(json_data)
            elif jsonData.get('type') == "subscribe":
                logger.debug(f"subscription {jsonData.get('data')}")
                for_send = []
                for arg in jsonData.get('data'):
                    channel_id, argument = parse_attr_params(arg)
                    channel = self.application.data.channelBase.get(channel_id)
                    new_subscription = SubscriptChannelArg(channel, argument)
                    subscription = self.application.data.subscriptions.add_subscription(
                        new_subscription)
                    stored_client = self.application.data.ws_clients.get_client(self)
                    stored_client.subscriptions.append(subscription)
                    send_data = {arg: channel.get_arg(argument)}
                    send_data.update(
                        {'time': (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S')})
                    for_send.append(send_data)
                    if len(for_send):
                        logger.debug(f"echo subscription {for_send}")
                        self.write_message(json.dumps(for_send, default=str))
            elif jsonData.get('type') == "set":
                if arg := jsonData.get('arg'):
                    channel_id, argument = parse_attr_params(arg)
                    channel = self.application.data.channelBase.get(channel_id)
                    value = jsonData.get('val')
                    self.application.data.channelBase.get(
                        channel_id).set_arg(argument, value)
                    if argument == settings.CAUSEID_ARG:
                        self.application.data.channelBase.get(
                            channel_id).set_arg('args.set_cause_flag', True)
                    logger.debug(f"set arg: {jsonData.get('arg')} to {value}")

            else:
                logger.debug('Unsupported ws message: '+message)

    def on_close(self):
        if client := self.application.data.ws_clients.get_client(self):
            for subscr in client.subscriptions:
                self.application.data.subscriptions.del_subscription(subscr)
            self.application.data.ws_clients.remove(client)


class AdminHtmlHandler(BaseHandler):
    @BaseHandler.check_user(CHECK_AUTORIZATION)
    def get(self):
        # print (f'in MainHtmlHandler, project {PROJECT["name"]}, user {self.user} ')
        # try:
        #     machine_id=logics.get_machine_from_user(self.user.get('login'))
        # except ValueError:
        #     logger.log('ERROR', f'wrong machine id in client login {self.user.get("login")} do get_ch from ip:{self.request.remote_ip}.')
        #     self.redirect("/login")

        self.render('idleadm.html',
                    user=self.user.get('login'),
                    idle_couses=json.dumps(logics.get_causes(), default=str),
                    version=settings.CLIENT_VERSION,
                    )


class AdmRequestHtmlHandler(BaseHandler):
    @BaseHandler.check_user(CHECK_AUTORIZATION)
    def post(self):
        self.set_header("Content-Type", "application/json")
        request = json.loads(self.request.body)
        print(request)
        if request.get('type') == 'addCause':
            new_cause = request.get("cause")
            if new_cause and new_cause != '' and new_cause != 'underfined':
                logics.addCause(new_cause)
                logger.log(
                    'MESSAGE', f'client {self.user.get("login")} from ip:{self.request.remote_ip} add cause {new_cause}.')
                self.write(json.dumps(200, default=str))
            else:
                self.write(json.dumps(400, default=str))
        elif request.get('type') == 'resetCauses':
            logics.reset_causes()
            self.write(json.dumps(200, default=str))
        elif request.get('type') == 'cmd':
            cmd = request.get('cmd')
            if cmd and cmd != '' and cmd != 'underfined':
                logger.log(
                    'MESSAGE', f'{self.user.get("login")} send command {cmd} from ip:{self.request.remote_ip}')
                if cmd == 'resetClient':
                    for client in self.application.data.ws_clients:
                        client.write_message(json.dumps({'cmd': 'reload'}))


class MEmulHtmlHandler(BaseHandler):
    @BaseHandler.check_user(CHECK_AUTORIZATION)
    def get(self):
        print(
            f'in MainHtmlHandler, project {PROJECT["name"]}, user {self.user} ')

        self.render('memul.html',
                    user=self.user.get('login'),
                    data=json.dumps(
                        self.application.data.channelBase.toDict(), default=str),
                    wsserv=(self.application.settings['wsParams'])+'_me')


class MEmulRequestHtmlHandler(BaseHandler):
    @BaseHandler.check_user(CHECK_AUTORIZATION)
    def post(self):
        self.set_header("Content-Type", "application/json")
        request = json.loads(self.request.body)
        print(request)
        if request.get('type') == 'get_ch':
            logger.log(
                'MESSAGE', f'client {self.user.get("login")} do get_ch from ip:{self.request.remote_ip}.')
            self.write(json.dumps(self.application.data.channelBase.get(
                request.get('id')).toDict(), default=str))
        elif request.get('type') == 'get_ch_arg':
            logger.log(
                'MESSAGE', f'client {self.user.get("login")} do get_ch_arg from ip:{self.request.remote_ip}.')
            print(
                f"result: {self.application.data.channelBase.get(request.get('id')).get_arg(request.get('arg'))}")
            self.write(json.dumps(self.application.data.channelBase.get(
                request.get('id')).get_arg(request.get('arg')), default=str))
        elif request.get('type') == 'set_ch':
            logger.log(
                'MESSAGE', f'client {self.user.get("login")} do set_ch from ip:{self.request.remote_ip}.')
            print(request)
            self.application.data.channelBase.get(request.get('id')).set_arg(
                request.get('arg'), request.get('value'))
            self.write(json.dumps(200, default=str))
        elif request.get('type') == 'set_ch_arg':
            logger.log(
                'MESSAGE', f'client {self.user.get("login")} do set_ch_arg from ip:{self.request.remote_ip}.')
            id, arg = parse_attr_params(request.get('arg'))
            
            self.application.data.channelBase.get(id).set_arg(arg, [request.get('value')])
            self.write(json.dumps(200, default=str))

    def get(self):
        self.set_header("Content-Type", "application/x-www-form-urlencoded")
        requestHeader = self.request.headers
        print(f'GET request!!!!!!!!!!!!!')
        print(f'requestHeader:{requestHeader}')
        requestBody = self.request.body
        print(f'requestBody:{requestBody}')


class MEWSHandler(WebSocketHandler):
    # def initialize(self, clbk):
    #     self.callback=clbk
    # def __init__(self, *args, **kwargs):
    #     self.id = None
    #     super(WSHandler, self).__init__(*args, **kwargs)

    # def check_origin(self, origin: str) -> bool:
    # print(f'origin:{origin}')
    # сюда можно проверку хостов с которых запросы
    # return self.current_user != None  #ws запросы только если кто-то залогинился перед этим
    # return True
    # return super().check_origin(origin)

    def open(self):
        logger.info(f'Web Socket open, IP:{self.request.remote_ip} ')
        # if self.request.headers['User-Agent'] != 'UTHMBot':  #не логгируем запросы от бота и не включаем его в список ws рассылки
        #     #if tornado.escape.xhtml_escape(self.get_secure_cookie("user")) in [_ for _ in allUsers(users)]:
        if self not in [client.client for client in self.application.data.ws_clients]:
            self.application.data.ws_clients.append(WSClient(self))
            logger.info(
                f'add, websocket IP:{self.request.remote_ip} Online {len(self.application.data.ws_clients)} clients')
        #         user=[user for user in config.users if user['id']==int(tornado.escape.xhtml_escape(self.get_secure_cookie("user")))][0]
        #         logger.info(f'Web Socket open, IP:{self.request.remote_ip},  user:{user.get("login")}, Online {len(config.wss)} clients')
        #     else:
        #         logger.log ('LOGIN',f'websocket user {tornado.escape.xhtml_escape(self.get_secure_cookie("user"))} not autirized , IP:{self.request.remote_ip}')
        #         self.close()

    def on_message(self, message):
        try:
            jsonData = json.loads(message)
            print(jsonData)
        except json.JSONDecodeError:
            logger.error("json loads Error for message: {0}".format(message))
        else:
            if jsonData.get('type') == "allStateQuerry":
                logger.debug("ws_message: allStateQuerry")
                msg = {'type': 'mb_data', 'data': None}
                json_data = json.dumps(msg, default=str)
                self.write_message(json_data)
            elif jsonData.get('type') == "subscribe":
                for_send = []
                for arg in jsonData.get('data'):
                    channel_id, argument = parse_attr_params(arg)
                    channel = self.application.data.channelBase.get(channel_id)
                    new_subscription = SubscriptChannelArg(channel, argument)
                    subscription = self.application.data.subscriptions.add_subscription(
                        new_subscription)
                    self.application.data.ws_clients.get_client(
                        self).subscriptions.append(subscription)
                    send_data = {arg: channel.get_arg(argument)}
                    send_data.update(
                        {'time': (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S')})
                    for_send.append(send_data)
                    if len(for_send):
                        self.write_message(json.dumps(for_send, default=str))
                # print (f'in ws:{self.application.data.subscriptions}')
            elif jsonData.get('type') == "msg":
                logger.debug(f"ws_message: {jsonData.get('data')}")
            elif jsonData.get('cmd') == "ws_reload":
                logger.debug(f"get command: reload websocket clients")
                for client in self.application.data.ws_clients:
                    client.write_message(json.dumps({'cmd': 'reload'}))

            else:
                logger.debug('Unsupported ws message: '+message)

    def on_close(self):
        # if self.request.headers['User-Agent'] != 'UTHMBot':  #не логгируем запросы от бота
        #     user=[user for user in config.users if user['id']==int(tornado.escape.xhtml_escape(self.get_secure_cookie("user")))][0]
        #     logger.info(f' User {user.get("login")} close WebSocket. Online {len(self.application.wsC_cients)-1} clients')
        if client := self.application.data.ws_clients.get_client(self):
            for subscr in client.subscriptions:
                self.application.data.subscriptions.del_subscription(subscr)
            self.application.data.ws_clients.remove(client)


class ReportsHtmlHandler(BaseHandler):
    @BaseHandler.check_user(CHECK_AUTORIZATION)
    def get(self):
        try:
            # machine_id_list = logics.get_machine_from_user(self.user.get('id'))
            machine_id = 2000                                                          #!!!!!!!!  dev !!!!!!!!!!!!!!!!!!!!
        except ValueError:
            logger.log(
                'ERROR', f'wrong machine id in clients prequest args: {self.request.arguments}  from ip:{self.request.remote_ip}.')
            return
        self.render('reports.html',
                    user=self.user.get('login'),
                    machine=machine_id,
                    wsserv=(self.application.settings['wsParams']+'_reps'),
                    host_port=http_server_params['host'] + ':' + str(http_server_params['port']),
                    idle_couses=json.dumps(
                        logics.get_machine_causes(machine_id), default=str),
                    state_channel=str(machine_id)+'.'+settings.STATE_ARG,
                    state_input=str(machine_id)+'.result_in',
                    causeid_arg=str(machine_id)+'.'+settings.CAUSEID_ARG,
                    project=5,
                    version=0.1,
                    )


class DBHtmlHandler(BaseHandler):
    @BaseHandler.check_user(CHECK_AUTORIZATION)
    def get(self):
        try:
            # machine_id_list = logics.get_machine_from_user(self.user.get('id'))
            machine_id = 2000                                                           #!!!!!!!!  dev  !!!!!!!!!!!!!!!!!!!!!!!!
        except ValueError:
            logger.log(
                'ERROR', f'wrong machine id in clients prequest args: {self.request.arguments}  from ip:{self.request.remote_ip}.')
            return
        self.render('dbdemo.html',
                    user=self.user.get('login'),
                    machine=machine_id,
                    wsserv=(self.application.settings['wsParams']+'_reps'),
                    idle_couses=json.dumps(
                        logics.get_machine_causes(machine_id), default=str),
                    state_channel=str(machine_id)+'.'+settings.STATE_ARG,
                    state_input=str(machine_id)+'.result_in',
                    causeid_arg=str(machine_id)+'.'+settings.CAUSEID_ARG,
                    project=5,
                    version=0.1,
                    )


class ReportsWSHandler(WebSocketHandler):

    def open(self):
        logger.info(f'Web Socket open, IP:{self.request.remote_ip} ')
        if self not in [client.client for client in self.application.data.ws_clients]:
            self.application.data.ws_clients.append(WSClient(self))
            logger.info(
                f'add, websocket IP:{self.request.remote_ip} Online {len(self.application.data.ws_clients)} clients')
            project_globals.states_buffer = []
            project_globals.idles_buffer = []

    def on_message(self, message):
        try:
            jsonData = json.loads(message)
        except json.JSONDecodeError:
            logger.error("json loads Error for message: {0}".format(message))
        else:
            if jsonData.get('type') == "first_read":
                data = {'states': dc.db_get_all_states(jsonData.get('id')),
                        'idles': dc.db_get_all_idles(jsonData.get('id')),
                        'operators': dc.db_get_all_operators()
                        }
                msg = {'type': 'first_read', 'data': data}
                json_data = json.dumps(msg, default=str)
                logger.debug(f"ws_message: first_read")
                self.write_message(json_data)
            elif jsonData.get('type') == "subscribe":
                print(f'subscribe {jsonData.get("data")}')
                for_send = []
                for arg in jsonData.get('data'):
                    channel_id, argument = parse_attr_params(arg)
                    channel = self.application.data.channelBase.get(channel_id)
                    new_subscription = SubscriptChannelArg(channel, argument)
                    subscription = self.application.data.subscriptions.add_subscription(
                        new_subscription)
                    self.application.data.ws_clients.get_client(
                                    self).subscriptions.append(subscription)
                    send_data = {arg: channel.get_arg(argument)}
                    send_data.update(
                        {'time': (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S')})
                    for_send.append(send_data)
                if len(for_send):
                    self.write_message(json.dumps(for_send, default=str))
            elif jsonData.get('type') == "update_data":
                if len(project_globals.states_buffer) > 0:
                    # logger.debug(
                    #     f"update states{project_globals.states_buffer}")
                    data = project_globals.states_buffer
                    project_globals.states_buffer = []
                    msg = {'type': 'update_states_db', 'data': data}
                    json_data = json.dumps(msg, default=str)
                    self.write_message(json_data)
                if len(project_globals.idles_buffer) > 0:
                    # logger.debug(f"update idles{project_globals.idles_buffer}")
                    data = project_globals.idles_buffer
                    project_globals.idles_buffer = []
                    msg = {'type': 'update_idles_db', 'data': data}
                    json_data = json.dumps(msg, default=str)
                    self.write_message(json_data)
                if len(project_globals.operators_buffer) > 0:
                    # logger.debug(f"update operators{project_globals.idles_buffer}")
                    data = project_globals.operators_buffer
                    project_globals.operators_buffer = []
                    msg = {'type': 'update_operators_db', 'data': data}
                    json_data = json.dumps(msg, default=str)
                    self.write_message(json_data)
            elif jsonData.get('type') == 'get_ch_arg':
                logger.debug(
                    f'client do get_ch_arg from ip:{self.request.remote_ip}.')
                try:
                    result = self.application.data.channelBase.get(
                        jsonData.get('id')).get_arg(jsonData.get('arg'))
                except AttributeError:
                    result = None
                # result = result if result != None else str(None)
                msg = [{str(jsonData.get('id'))+'.' +
                        jsonData.get('arg'): result}]
                json_data = json.dumps(msg, default=str)
                self.write_message(json_data)
                print(f"result: {msg}")
                # self.write(json.dumps([], default=str))
            else:
                logger.debug('Unsupported ws message: '+message)

    def on_close(self):
        if client := self.application.data.ws_clients.get_client(self):
            self.application.data.ws_clients.remove(client)


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument("name", "")

        for user in self.application.data.users:
            if user['login'] == username:
                logger.log(
                    'DEBUG', f"Try login {username}, user ok, ip:{self.request.remote_ip}")
                # self.set_secure_cookie("user", username, expires_days=180)
                self.set_secure_cookie("user", str(
                    user.get('id')), expires_days=400)
                self.redirect("/")
                return
        # no such user
        logger.log(
            'DEBUG', f"Try login {username}, user wrong , ip:{self.request.remote_ip}")
        self.redirect("/login")


class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")


handlers = [
    (r"/", MainHtmlHandler),
    # (r"/request",RequestHtmlHandler),
    (r"/adm", AdminHtmlHandler),
    (r"/reps", ReportsHtmlHandler),
    (r"/db", DBHtmlHandler),
    (r"/arequest", AdmRequestHtmlHandler),
    (r'/ws', WSHandler),
    (r"/me", MEmulHtmlHandler),
    (r"/merequest", MEmulRequestHtmlHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r'/ws_me', MEWSHandler),
    (r'/ws_reps', ReportsWSHandler),
    (r"/static/(.*)", StaticFileHandler,
     {"path": os.path.join(*path_params.get('static', 'web/webdata').split('/'))}),
    (r'/js/(.*)', StaticFileHandler,
     {"path": os.path.join(*path_params.get('js', 'web/webdata/js').split('/'))}),
    (r'/css/(.*)', StaticFileHandler,
     {"path": os.path.join(*path_params.get('css', 'web/webdata/css').split('/'))}),
    (r'/images/(.*)', StaticFileHandler,
     {"path": os.path.join(*path_params.get('images', 'web/webdata/images').split('/'))}),
]

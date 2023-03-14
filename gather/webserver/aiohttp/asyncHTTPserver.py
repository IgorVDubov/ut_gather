from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

async def post1(request):
    print (request.query['id'])
    # name = request.match_info.get('name', "Anonymous")
    # text = "Hello, " + name
    # return web.Response(text=text)


class asyncHTTPserver(web.Application):
    def __init__(self,loop=None):
        if loop:
            _loop=loop
        else:
            import asyncio
            _loop= asyncio.get_event_loop()
        super().__init__(loop=_loop)
        # super.__init__(loop=_loop)
        self.add_routes([
                        web.get('/', handle)
                        ,web.post('/r', post1)
                        ])
    
    def start(self,_host='localhost',_port=8080):
        '''
        host = IP to run
        port = port to run
        '''
        web.run_app(self,host=_host,port=_port)

if __name__=='__main__':
    app=asyncHTTPserver()
    app.start('localhost',8081)
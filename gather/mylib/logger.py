from distutils.debug import DEBUG
from loguru import logger
import os.path

def loggerInit(loggerLevel):
    '''
    Level   Numeric value
    CRITICAL    50
    ERROR       40
    WARNING     30
    INFO        20
    DEBUG       10
    NOTSET      0
    '''
    print (os.curdir+os.sep)
    if not os.path.isdir('logs'):
        logger.info('dir .\logs not exist, creating...')
        try:
            os.mkdir('logs')
        except OSError  as e:
            logger.error(e)
            logger.error('Cant create logs files. Access denied...')
            return
    logsPath=os.curdir+os.sep+'logs'+os.sep
    
    logger.add(sink=logsPath+'server.log', format="{time:YY-MM-DD HH:mm:ss} {level} {message}", level=loggerLevel.upper(), rotation='1 MB')
    logger.level("LOGIN", no=21, color="<yellow>")
    logger.level("MESSAGE", no=41, color="<green>")


    logger.add(sink=logsPath+'logins'+'.log', format="{time:YY-MM-DD HH:mm:ss} {message}", filter=lambda record: record["level"].name == "LOGIN", rotation='1 MB')
    print(logger)


if __name__ == '__main__':
    loggerInit('error')
    logger.info('info')
    logger.debug('debug')
    logger.error('error')
    logger.warning('error')


    logger.log("LOGIN", f"Here we go!")
    logger.log("MESSAGE", f" MY MESSAGE")

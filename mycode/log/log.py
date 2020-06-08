import logging
import logging.config

logging.config.fileConfig(fname='/home/pi/Documents/Repo/Sphere_summer_project/mycode/log/log.conf', disable_existing_loggers=False)

# Get the logger specified in the file
logger = logging.getLogger('usr')

def log_this(Host_IP='',Mode='Pause',manual_rotation=False,stopped=False,duration='',status_code=000,degree=0,start_time='',finish_time=''):
    if finish_time=='' or duration=='forever' or stopped==False:
        logger.info('Host_IP:{}-Mode:{}-manual_roration:{} - stopped:{} - duration:{} - status_code:{} - degree:{}'.format(Host_IP,Mode,manual_rotation,stopped,duration,status_code,degree))
    else:
        logger.info('Host_IP:{}-Mode:{}-manual_roration:{} - stopped:{} - duration:{} - status_code:{} - degree:{} - start_time:{} - finish_time:{}'.format(Host_IP,Mode,manual_rotation,stopped,duration,status_code,degree,start_time,finish_time))

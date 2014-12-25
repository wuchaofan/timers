from datetime import datetime
import time,logging
import setting
from notify import Notify
from daemonize import Daemonize

fh = logging.FileHandler("test.log", "w")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger('jobs')
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)
def servermain():
	logger = logging.getLogger('jobs')
	try:
		while True:
			noo=Notify()
			rest=noo.bingfa()
			noo.close()
			if not rest:
				logger.debug('No data')
				logger.debug('current time-->%s',datetime.now())
				sec=setting.PERIOD-datetime.now().second
				logger.debug('sleep....%ss',sec)
				time.sleep(sec)
	except KeyboardInterrupt, e:
	 	#LOG(e)
		logger.debug(e)
	finally:
		pass
		#noo.close()
	

	
if __name__=='__main__':
	pid="timer.pid"
	
	keep_fds = [fh.stream.fileno()]
	logger.debug("Start...")
	servermain()
	# daemon = Daemonize(app="jobs", pid=pid, action=servermain,keep_fds=keep_fds)
	# daemon.start()


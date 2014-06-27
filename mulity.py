from datetime import datetime
import time,logging
import setting
from notify import Notify
from daemonize import Daemonize
#from Log import LOG
def servermain():
	try:
		while True:
			noo=Notify()
			rest=noo.sendMessage()	
			noo.close()
			if not rest:
				print '=========',datetime.now()
                		sec=setting.PERIOD-datetime.now().second
                		print 'sleep....',sec 
                		time.sleep(sec)
	except KeyboardInterrupt, e:
	 	#LOG(e)
		print e
	finally:
		pass
		#noo.close()
	

	
if __name__=='__main__':
	pid="timer.pid"
	fh = logging.FileHandler("test.log", "w")
	fh.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	fh.setFormatter(formatter)
	logger = logging.getLogger('jobs')
	logger.addHandler(fh)
	keep_fds = [fh.stream.fileno()]

#	servermain()
	daemon = Daemonize(app="test_app", pid=pid, action=servermain,keep_fds=keep_fds)
	daemon.start()


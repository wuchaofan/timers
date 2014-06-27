import time,logging
from notify import Notify
from daemonize import Daemonize
from Log import LOG
def servermain():
	noo=Notify()
	try:
		while True:
			noo.sendMessage()	
				
	# except KeyboardInterrupt, e:
	# 	LOG(e)
	except:
		pass
	finally:
		noo.close()
	

	
if __name__=='__main__':
	pid="/home/wuchaofan/test_app.pid"
	fh = logging.FileHandler("test.log", "w")
	fh.setLevel(logging.DEBUG)
	logger.addHandler(fh)
	keep_fds = [fh.stream.fileno()]

	# servermain()
	daemon = Daemonize(app="test_app", pid=pid, action=servermain,keep_fds=keep_fds)
	daemon.start()


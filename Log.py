import logging
def LOG(string):
	# logging.basicConfig()
	logger = logging.getLogger('jobs')
	stderr_log_handler = logging.StreamHandler()
	logger.addHandler(stderr_log_handler)
	logger.debug(string)
	
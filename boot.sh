#!/bin/bash
case $1
	start)
		python mulity.py
	stop)
		kill -9 `cat timer.pid`
		;;
	restart)
		kill -HUP `cat timer.pid`
	*)
		echo "stop|restart"
esac

#!/bin/bash
case "$1" in
start)
	python mulity.py
	;;
stop)
	kill -HUP `cat timer.pid`
	;;
restart)
	kill -HUP `cat timer.pid`
	echo "stop done"
	sleep 1
	python mulity.py
	echo "restart done"
	;;
*)
	echo "stop|restart"
	;;
esac

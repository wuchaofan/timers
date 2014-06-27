#!/bin/bash
case $1 in
start)
	python mulity.py
	;;
stop)
	kill -9 `cat timer.pid`
	;;
restart)
	kill -HUP `cat timer.pid`
	echo "restart done""
	;;
*)
	echo "stop|restart";;
esac

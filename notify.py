# -*- coding: utf-8 -*-
import logging
#from Log import LOG
import MySQLdb,json,time
import MySQLdb.cursors
from datetime import datetime
import setting
from baiduPush.Channel import Channel
from apns import APNs, Payload
from multiprocessing import Process
logger = logging.getLogger('jobs')
LOG=logger.debug
apn = APNs(use_sandbox=True, cert_file=setting.IOSPEM)

class Notify(object):
	"""docstring for Notify"""
	def __init__(self):
		super(Notify, self).__init__()
		self.conn=None
		try:
			self.conn=MySQLdb.connect(setting.HOST,setting.USER,\
				setting.PASSWORD,setting.DB,port=3306,cursorclass = MySQLdb.cursors.DictCursor)
			self.conn.set_character_set('utf8')
			self.cur=self.conn.cursor()
		except MySQLdb.Error,e:
			logger.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
	def query(self):
		LOG('Into query.....')
		
		s_now=datetime.now().strftime("%Y-%m-%d %H:%M:00")
		e_now=datetime.now().strftime("%Y-%m-%d %H:%M:59")
		q = "SELECT `vid`,`key_id`,`id`,`sid`,`sendtime`,`title` FROM `visit_hit` WHERE `status`=\'wait\' AND `sendtime` between \'"+s_now+"\'"
		q += " AND \'"+e_now+"\'"
		# print q
		self.cur.execute(q)
		res=self.cur.fetchall()

		return res

	def sendMessage(self):
		rest = self.query()
		iosarr=[]
		androidarr=[]
		if rest:
			for ii in rest:
				iosp=Process(target=self.iosNotify,args=(unicode(ii['title'],'utf8'),ii['vid'],ii['key_id'],ii['id'],ii['sid'],))
				# androidp=Process(target=self.androidNotify,args=(unicode(ii['title'],'utf8'),ii['vid'],u'信息'))
				iosarr.append(iosp)
				# androidarr.append(androidp)
				iosp.start()
				# androidp.start()
			for pr in range(len(rest)):
				iosarr[pr].join()
				# androidarr[pr].join()
		return  rest

	def getIOSDeviceToken(self):
		LOG('Into getIOSDeviceToken....')
		q="SELECT `devicetoken` FROM `user_device` WHERE `uid`=125676;"
		self.cur.execute(q)
		rest=self.cur.fetchall()
		tokens=[x['devicetoken'] for x in rest]
		return tokens

	def iosNotify(self,_title,vid,key,_id,sid):
		# print 'Into iosNotify....'
		Devices = self.getIOSDeviceToken()

		for token in Devices:
			payload = Payload(alert=_title, sound="ping.aiff", badge=1,custom={'vid':vid,'key':key,'id':_id,'sid':sid})
			apn.gateway_server.send_notification(token, payload)
		q="UPDATE `visit_hit` SET `status`=\'sent\' WHERE vid="+str(vid)
		self.cur.execute(q)
		# print 'OVER.....'
	def androidNotify(self,_title,_message,vid):
		bpush=Channel(setting.baidupush_apikey,setting.baidupush_secretkey)
		# for device in androidDevices:
		push_type = 1
		# optional = {}
		# optional[Channel.USER_ID] = ''
		# optional[Channel.CHANNEL_ID] =''
		#推送通知类型
		optional[Channel.MESSAGE_TYPE] = 1
		message_key = "message"
		message = json.dumps({'title':_title,'description':_message})
		ret = bpush.pushMessage(push_type, message.encode('utf8'), message_key)
		if not ret:
			logger.error("message send to android device fail")
	def close(self):
		if self.conn:
			self.cur.close()
			self.conn.commit()
			self.conn.close()





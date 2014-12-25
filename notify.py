# -*- coding: utf-8 -*-
import logging
#from Log import LOG
import MySQLdb,json,time
import MySQLdb.cursors
from datetime import datetime
import setting
from baiduPush.Channel import Channel
# from apns import APNs, Payload
from apnsclient import Session,Message,APNs

from multiprocessing import Process
logger = logging.getLogger('jobs')
LOG=logger.debug
# apn = APNs(use_sandbox=True, cert_file=setting.IOSPEM)

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
		message = Message(Devices, alert=_title, badge=10,extra={'vid':vid,'key':key,'id':_id,'sid':sid})
		srv = APNs(self.apn)
		res = srv.send(message)

		# for token in Devices:
		# 	payload = Payload(alert=_title, sound="ping.aiff", badge=1,custom={'vid':vid,'key':key,'id':_id,'sid':sid})
		# 	apn.gateway_server.send_notification(token, payload)
		q="UPDATE `visit_hit` SET `status`=\'sent\' WHERE vid="+str(vid)
		self.cur.execute(q)
		# print 'OVER.....'
	def androidNotify(self,_title,_message,vid):
		# for device in androidDevices:
		push_type = 1
		# optional = {}
		# optional[Channel.USER_ID] = ''
		# optional[Channel.CHANNEL_ID] =''
		#推送通知类型
		optional[Channel.MESSAGE_TYPE] = 1
		message_key = "message"
		message = json.dumps({'title':_title,'description':_message})
		ret = self.bpush.pushMessage(push_type, message.encode('utf8'), message_key)
		if not ret:
			logger.error("message send to android device fail")
	def close(self):
		if self.conn:
			self.cur.close()
			self.conn.commit()
			self.conn.close()
	def orderRemind(self):
		LOG("Reming start...")
		_now=datetime.now()
		q="SELECT o.`oid`,o.`beginTime`,o.`uid`,s.name as shopname,s.subname FROM `order` o,`shop` s WHERE o.status=\'confirm\' AND o.`oid` not in (SELECT `oid` FROM `remind_order`) AND o.sid=s.sid"
		self.cur.execute(q)
		remind=self.cur.fetchall()

		result = []
		for item in remind:
			otime = datetime.strptime(item['beginTime'],"%Y%m%d%H%M")
			item['beginTime']=otime
			if (otime - _now).seconds<=1860:
				if item['uid']==0:
					q="SELECT uw.uid FROM `order_weixin` ow,`user_wxaccount` uw WHERE ow.oid=%s AND ow.weixin=uw.openid"
					self.cur.execute(q,(item['oid'],))
					uid=self.cur.fetchall()
					if uid:
						item['uid']=uid[0]['uid']
						result.append(item)
				else:
					result.append(item)
				q="REPLACE INTO `remind_order`(oid,status)VALUES(%s,%s)"
				self.cur.execute(q,(item['oid'],1))

		if not result:
			return None
		msg = u'您预约的{0}[{1}]店 {2}欢唱将至，快去KTV赴约吧！'
		iosp = Process(target=self.ios_order,args=(self.cur,result,msg,'shopname','subname','beginTime'))
		andp = Process(target=self.android_order,args=(self.cur,result,msg,'shopname','subname','beginTime'))
		iosp.start()
		andp.start()

		iosp.join()
		andp.join()
	def ios_order(self,cursor,uids,mesg,a,b,c):
		for x in uids:
			mgs=mesg.format(x[a],x[b],x[c].strftime("%H:%M"))
			q="SELECT ud.devicetoken FROM `user_device` ud WHERE ud.uid="+`x`
			self.cur.execute(q)
			iostoken=self.cur.fetchall()
			if iostoken:
				message = Message([iostoken[0]['devicetoken']], alert=msg, badge=10)
				srv = APNs(self.apn)
				res = srv.send(message)
	def android_order(self,cursor,uids,mesg,a,b,c):
		for x in uids:
			q = "SELECT sad.userid,sad.channelid FROM `user_android_device` sad WHERE sad.uid="+`x`
			cursor.execute(q)
			android=cursor.fetchall()
			if android:
				mgs=mesg.format(x['shopname'],x['subname'],x['beginTime'].strftime("%H:%M"))
				push_type = 1
				# optional = {}
				optional[Channel.USER_ID] = android[0]['userid']
				optional[Channel.CHANNEL_ID] = android[0]['channelid']
				#推送通知类型
				optional[Channel.MESSAGE_TYPE] = 1
				message_key = "message"
				message = json.dumps({'title':u"消息提醒",'description':msg})
				ret = self.bpush.pushMessage(push_type, message.encode('utf8'), message_key)
				if not ret:
					logger.error("message send to android device fail")

	def bingfa(self):
		self.apn = Session().new_connection("push_sandbox", cert_file=setting.IOSPEM)
		self.bpush=Channel(setting.baidupush_apikey,setting.baidupush_secretkey)
		rest = self.sendMessage()
		self.orderRemind()
		self.remind_group
		return rest
	def remind_group(self):
		q="SELECT sg.`sgsid`,o.oid,o.uid,sg.endtime,s.name as shopname,s.subname,sgd.title FROM `order` o ,`order_detail` od,`shop_groupsaledetail` sgd,`shop_groupsale` sg,`shop` s WHERE s.sid=o.sid AND o.oid=od.oid AND od.`sgsdid` != 0 AND sgd.sgsdid=od.`sgsdid` AND sg.sgsid=sgd.sgsid AND o.status=\'confirm\'"
		self.cur.execute(q)
		group=cursor.fetchall()
		_now=datetime.now()

		result = []
		for i in group:
			gtime = datetime.strptime(i['endtime'],"%Y%m%d%H%M")
			if (gtime - _now).seconds<=24*3600:
				if i['uid']==0:
					q="SELECT uw.uid FROM `order_weixin` ow,`user_wxaccount` uw WHERE ow.oid=%s  AND ow.weixin=uw.openid"
					self.cur.execute(q,i['oid'])
					uid=cursor.fetchall()
					if uid:
						i['uid']=uid[0]['uid']
						result.append(i)
				else:
					result.append(i)
		msg = u"您购买的{0}[{1}]店{2}(团购券名)即将到期，快预约欢唱吧！"
		iosp = Process(target=self.ios_order,args=(self.cur,result,msg,'shopname','subname','title'))
		andp = Process(target=self.android_order,args=(self.cur,result,msg,'shopname','subname','title'))
		iosp.start()
		andp.start()

		iosp.join()
		andp.join()





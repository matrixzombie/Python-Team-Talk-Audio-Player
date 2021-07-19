#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os, time, threading, subprocess, psutil, keyboard, json, urllib.request, urllib.parse, re

from twisted.internet import reactor, protocol
from youtube_search import YoutubeSearch
config={}
def configure():
	print("Configuration not found. Starting configuration process.")
	config["server"]=input("Enter your server hostname/IP")
	config["port"]=input("Enter your server's port.")
	config["usertimeout"]=input("Enter the user timeout of your server. Find it in server properties.")
	config["nickname"]=input("Enter the nickname to connect with. Press enter for none.")
	if config["nickname"]=="":
		config.pop("nickname")
	config["chanid"]=input("Enter the id of the channel you'd like to join. Press enter for none.")
	if config["chanid"]=="":
		config.pop("chanid")
	config["chanpass"]=input("Enter the channel password. Press enter for none")
	if config["chanpass"]=="":
		config.pop("chanpass")
	config["username"]=input("Enter the username for your account. Press enter for none.")
	if config["username"]=="":
		config.pop("username")
	config["password"]=input("Enter the password for your account. Press enter for none.")
	if config["password"]=="":
		config.pop("password")
	config["allowpause"]=input("Would you like to allow people to pause audioplayback with the /p command? Enter allow to allow, or press enter to disallow.")
	if config["allowpause"]!="allow":
		config.pop("allowpause")
	with open("bot.ini","w") as ini:
		json.dump(config,ini)
	main()
class TeamtalkClient(protocol.Protocol):
	def connectionMade(self):
		print("Connected!")

	def send(self,data):
		self.transport.write(data.encode())
	def dataReceived(self, data):
		msg=data.decode()
		print("Server said:", msg)
		if msg.startswith("teamtalk"):
			if config.get("username")==None and config.get("password")==None:
				self.send('login nickname="'+config["nickname"]+'" username="" password=""\n')
			elif config.get("username")!=None and config.get("password")==None:
				self.send('login nickname="'+config["nickname"]+'" username="'+config["username"]+'" password=""\n')
			else:
				self.send('login nickname="'+config["nickname"]+'" username="'+config["username"]+'" password="'+config["password"]+'"\n')
		if msg.startswith("accepted"):
			if config.get("chanpass")==None and config.get("chanid")!=None:
				self.send('join chanid='+config["chanid"]+'\n')
			elif config.get("chanpass")!=None and config.get("chanid")!=None:
				self.send('join chanid='+config["chanid"]+' password='+config["chanpass"]+'\n')
			elif config.get("chanid")==None and config.get("chanpass")==None:
				self.send('join name="Audio Player Channel" parentid=1 topic="" oppassword="audioplayer001" audiocodec=[3,48000,2,2049,10,1,0,128000,1,0,1920,1] audiocfg=[0,0] type=0 userdata=0 password=""\n')
#		if msg.startswith("loggedin userid"):
#			u=user(rcv[rcv.find("userid=")+6:rcv.find("nickname=")-2],rcv[rcv.find("nickname=")+10:rcv.find("username=")-2])
#			print("added user with nickname "+u.nickname+" and userid "+u.id)
		if msg.startswith("messagedeliver type=1 "):
			msg=msg[msg.find("content=")+9:msg.find('" destuserid')]
			if msg=="/stop":
				if checkprocess("vlc.exe"):
					keyboard.send("ctrl+shift+q")
			elif msg=="/n":
				result+=1
				url=ysearch(oldmsg,result)
				if checkprocess("vlc.exe"):
					keyboard.send("ctrl+shift+q")
				subprocess.Popen("vlc/vlc.exe "+url)
			elif msg=="/p" and result>0:
				result-=1
				url=ysearch(oldmsg,result)
				if checkprocess("vlc.exe"):
					keyboard.send("ctrl+shift+q")
				subprocess.Popen("vlc/vlc.exe "+url)
			elif msg=="/pause" and config.get("allowpause")!=None:
				if checkprocess("vlc.exe"):
					keyboard.send("ctrl+shift+c")
			elif msg.find("youtube.com/watch?v=")>-1:
				if checkprocess("vlc.exe"):
					keyboard.send("ctrl+shift+q")
				subprocess.Popen("vlc/vlc.exe "+msg)
			else:
				oldmsg=msg
				result=1
				url=ysearch(msg,result)
				if checkprocess("vlc.exe"):
					keyboard.send("ctrl+shift+q")
				subprocess.Popen("vlc/vlc.exe "+url)
#		self.transport.loseConnection()

	def connectionLost(self, reason):
		print("connection lost")


class TeamtalkFactory(protocol.ClientFactory):
	protocol = TeamtalkClient

	def clientConnectionFailed(self, connector, reason):
		print("Connection failed - goodbye!")
		reactor.stop()

	def clientConnectionLost(self, connector, reason):
		print("Connection lost - goodbye!")
		reactor.stop()


def ping():
	while True:
		time.sleep(int(config["usertimeout"])-10)
		send("ping")
def ysearch(term,num):
	yt=YoutubeSearch(term,num).to_dict()
	try:
		return "https://www.youtube.com/watch?v="+yt[num-1]["id"]+""
	except:
		print("Error searching the term is "+term+" and the number is "+str(num))
def ytsearch(searchstring,num):
	query_string = urllib.parse.urlencode({"search_query" : searchstring})
	html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
	search_results = re.findall(r'href=\"\/watch\?v=()', html_content.read().decode())
	return "https://www.youtube.com/watch?v=" + search_results[num]
def checkprocess(processName):
	for proc in psutil.process_iter():
		if processName.lower() in proc.name().lower():
			return True
	return False
def main():
	print("Checking for existing config.")
	if os.path.isfile("bot.ini")==True:
		print("Configuration found. Reading config...")
		global config
		with open("bot.ini","r") as fp:
			config=json.load(fp)
		if config.get("server")==None or config.get("port")==None or config.get("usertimeout")==None:
			print("Server, port, or user timeout not entered, restarting configuration process.")
			configure()
		print("Configuration loaded!")
	else:
		configure()
	f = TeamtalkFactory()
	reactor.connectTCP(config["server"], int(config["port"]), f)
	reactor.run()
#	pingloop=threading.Thread(target=ping,args=())
#	pingloop.start()
main()

class timer():
	def __init__(self):
		self.inittime=int(round(time.time()))*1000

	def elapsed(self):
		return int(round(time.time()))*1000-self.inittime

	def restart(self):
		self.inittime=int(round(time.time()))*1000

#!/usr/bin/env python3
__author__='DGideas';
#Release:dreamspark
import os;
import sys;
try:
	os.chdir(os.path.dirname(sys.argv[0]));
except FileNotFoundError:
	pass;
except OSError:
	pass;

class DGStorage:
	def __init__(self,conf={}):
		self.DGSTORAGE_VERSION='2.0';
		self.DGSTORAGE_CHARSET='utf8';
		self.DGSTORAGE_SINGLECOLLECTIONLIMIT=1024;
		self.DGSTORAGE_SEARCHRANGE=3;
		self.DGSTORAGE_SEARCHINDEXLIMIT=256;
				
		self.Location='';
		self.CollectionCache=[];
		self.LastCollection='';
		self.SearchCache=[];
	
	def create(self,name):
		import codecs;
		import uuid;
		import urllib.parse;
		import os;
		import sys;
		
		name=urllib.parse.quote_plus(str(name));
		try:
			os.chdir(str(name));
		except FileNotFoundError:
			os.mkdir(str(name));
			self.Location=name;
			with codecs.open(self.Location+'/conf.dgb','a',self.DGSTORAGE_CHARSET) as conf:
				conf.write(str(uuid.uuid1())+'\n');
				conf.write('Version:'+self.DGSTORAGE_VERSION);
			os.mkdir(self.Location+'/index');
			with codecs.open(self.Location+'/index/index.dgi','a',self.DGSTORAGE_CHARSET) as index:
				pass;
			os.mkdir(self.Location+'/cache');
			os.mkdir(self.Location+'/cache/search');
			return True;
		else:
			return False;
	
	def select(self,name):
		import codecs;
		import uuid;
		import urllib.parse;
		import os;
		import sys;
		name=urllib.parse.quote_plus(str(name));
		try:
			os.chdir(str(name));
		except FileNotFoundError:
			return False;
		else:
			self.Location=name;
			with open('conf.dgb') as conf:
				correctVersion=False;
				for line in conf:
					if line.find('Version:2')!=-1:
						correctVersion=True;
				if correctVersion==False:
					return False;
			with open('index/index.dgi') as index:
				for line in index:
					line=line.replace('\n','');
					if line!='' and line!='\n':
						self.CollectionCache.append(line);
			return len(self.CollectionCache);
	
	def append(self,content):
		import uuid;
		return self.add(str(uuid.uuid1()),content,{"method":"append"});
	
	def add(self,key,content,prop={}):
		import codecs;
		import uuid;
		import urllib.parse;
		import os;
		import sys;
		key=str(key).replace('\n','');
		key=urllib.parse.quote_plus(str(key));
		operationCollection=''
		if key=='':
			return False;
		if len(self.CollectionCache)==0:
			if (self.createcoll(0)):
				operationCollection=0;
			else:
				return False;
		else:
			if self.LastCollection!='':
				with open(str(self.LastCollection)+'/index/index.dgi') as collIndex:
					i=0;
					for line in collIndex:
						if line!='':
							i+=1;
					if i<self.DGSTORAGE_SINGLECOLLECTIONLIMIT:
						operationCollection=self.LastCollection;
					else:
						operationCollection=self.findavailablecoll(True);
			else:
				operationCollection=self.findavailablecoll(True);
		self.LastCollection=operationCollection;
		uid='';
		with codecs.open(str(operationCollection)+'/index/index.dgi','a','utf8') as collIndex:
			collIndexR=open(str(operationCollection)+'/index/index.dgi');
			i=0;
			for line in collIndexR:
				if line!='' and line!='\n':
					i+=1;
			collIndexR.close();
			uid=uuid.uuid1();
			if i==0:
				collIndex.write(str(uid)+','+str(key));
			else:
				collIndex.write('\n'+str(uid)+','+str(key));
		with codecs.open(str(operationCollection)+'/'+str(uid)+'.dgs','a','utf8') as storage:
			storage.write(str(content));
		if len(prop)!=0:
			with codecs.open(str(operationCollection)+'/'+str(uid)+'.dgp','a','utf8') as storageProp:
				for propItem in prop:
					storageProp.write(str(propItem)+':'+str(prop[propItem])+'\n');
		return uid;
	
	def index(self,key):
		return self.get(key);
	
	def get(self,key,limit=None,skip=0):
		if limit==0:
			return False;
		if limit==None:
			return self.finditemviakey(key)[skip:];
		elif limit>0:
			return self.finditemviakey(key)[skip:int(limit)];
		else:
			return False;
	
	#Private
	def clche(self,where=''):
		if where=='':
			self.CollectionCache=[];
	
	def createcoll(self,coll):
		import codecs;
		import os;
		try:
			os.mkdir(str(coll));
		except FileExistsError:
			return False;
		else:
			os.mkdir(str(coll)+'/index');
			with codecs.open(str(coll)+'/index/index.dgi','a','utf8') as dgc:
				pass;
			self.CollectionCache.append(coll);
			with open('index/index.dgi','a') as index:
				index.write(str(coll)+'\n');
			return True;
	
	def removecoll(self,coll):
		return;
	
	def findavailablecoll(self,createNewColl=False):
		searchRange=self.DGSTORAGE_SEARCHRANGE;
		if searchRange!='' or searchRange!=None:
			searchRange=-1-int(searchRange);
		for collection in self.CollectionCache[:searchRange:-1]:
			with open(str(collection)+'/index/index.dgi') as collIndex:
				i=0;
				for line in collIndex:
					if line!='':
						i+=1;
				if i<self.DGSTORAGE_SINGLECOLLECTIONLIMIT:
					return collection;
					break;
				else:
					continue;
		if createNewColl==True:
			self.createcoll(int(self.LastCollection)+1);
			return int(self.LastCollection)+1;
		else:
			return False;
	
	def finditemviakey(self,key):
		import urllib.parse;
		key=str(urllib.parse.quote_plus(str(key)));
		res=[];
		for collection in self.CollectionCache:
			with open(str(collection)+'/index/index.dgi') as collIndex:
				for line in collIndex:
					line=line.replace('\n','');
					if line!='' or line!='\n':
						split=line.split(',');
						if split[1]==key:
							with open(str(collection)+'/'+split[0]+'.dgs') as storage:
								res.append({str(split[0]):storage.read()});
		return res;
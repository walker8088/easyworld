#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#Author: Xu jia (sanfanling)
#License:GPLv2.0

import re

class lrc:
	def __init__(self,string):
		self.string=string
		
	def format(self):
		offsetList=re.findall('\[offset:.*\]',self.string)
		if(len(offsetList)<>0):
			v=offsetList[0][8:-1]
			if(v<>''):
				self.offset=int(v)
			else:
				self.offset=0
		else:
			self.offset=0
		origin=re.findall('\[\d{2}:\d{2}.*?\n|\[\d{2}:\d{2}.*?$',self.string)
		new=[]
		for i in origin:
			part1=i.split(']')[-1]
			for j in re.findall('\[\d{2}:\d{2}.*?\]',i):
				new.append(j+part1)
		new1=[]
		for k in new:
			pp=k.split(']')[0][1:]
			qq=k.split(']')[1].strip()
			qq=re.sub('<|>','',qq)
			if(qq==''):
				qq='<br>'
			qq='<p align="center">%s</p>' %qq
			a1=int(pp[0:2])*60000
			a2=int(pp[3:5])*1000
			if(len(pp)==8):
				ms=str(a1+a2+int(pp[6:])*10-self.offset+10000000)+'$#$#'+qq
				new1.append(ms)
			elif(len(pp)==7):
				ms=str(a1+a2+int(pp[6:])*100-self.offset+10000000)+'$#$#'+qq
				new1.append(ms)
			elif(len(pp)==5):
				ms=str(a1+a2-self.offset+10000000)+'$#$#'+qq
				new1.append(ms)
		new1.sort()
		tag=[]
		context=[]
		for item in new1:
			tag.append(int(item.split('$#$#')[0])-10000000)
			context.append(item.split('$#$#')[1])
		return (tag,context)
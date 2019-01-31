# -*- coding: utf-8 -*-
# @File 	: QueryScore.py
# @Author 	: jianhuChen
# @Date 	: 2019-01-29 13:08:45
# @License 	: Copyright(C), USTC
# @Last Modified by  : jianhuChen
# @Last Modified time: 2019-02-01 00:36:57


import requests
import re
import os
import time 
from prettytable import PrettyTable  # 打印表格
from conf import *

class QueryScore:
	def __init__(self, userAccount, loginApi=1):
		'''
			作用：初始化用户信息
		'''
		self.userId = userAccount['userId']
		self.userPwd = userAccount['userPwd']
		self.userName = self.userId
		self.loginApi = loginApi
		# 构建一个Session对象，可以保存页面Cookie
		self.sess = requests.Session()
		# 构造请求报头
		self.headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}


	def getCheckcode(self, checkcodeData):
		'''
			作用：手动输入验证码
			返回：验证码
		'''
		with open('checkcode.jpg', 'wb') as f:
			f.write(checkcodeData)
		text = raw_input('请输入验证码：')
		# 返回用户输入的验证码
		return text

	def getStuInfoHtml(self):
		'''
			作用：获取个人信息页面源码，用于测试信息是否爬取成功
			返回：个人信息页面源码
		'''
		response = self.sess.get('http://yjs.ustc.edu.cn/xsxx/s_pyxx.asp', headers=self.headers)
		stuInfoHtml = response.text.encode('utf-8')
		return stuInfoHtml

	def printStuInfo(self, stuInfoHtml):
		'''
			作用：打印个人信息
			返回：是否登陆成功
		'''
		print '正在查询您的个人信息，请稍候...'
		pattern = re.compile(r'class="bt06">(.*?)</td>', re.S)
		infoList = pattern.findall(stuInfoHtml)
		if len(infoList)==0:
			print '查询您的个人信息失败...\n请检查您的账号/密码/验证码是否输入正确！'
			return False
		else:
			print '查询您的个人信息成功...'
			# 去除多余的空格
			for item in infoList:
				item = item.strip()
			# 记录名字信息
			self.userName = infoList[1]
			print '='*60
			print '学号：{}\t姓名：{}\t出生日期：{}'.format(infoList[0], infoList[1], infoList[3])
			print '院系：{}\t专业：{}\t班级：{}'.format(infoList[4], infoList[5], infoList[7])
			print '学生类型：{}\t学制：{}\t导师：{}'.format(infoList[8], infoList[9], infoList[10])
			print '='*60
			return True
			

	def yjsLogin(self):
		'''
			作用：登录科大研究生信息平台并获取学生信息页面
			返回：是否登陆成功
		'''
		if self.loginApi==1:
			# 研究生平台登录接口
			loginUrl = 'http://yjs.ustc.edu.cn/default_yjsy.asp'
			# 获取验证码的URL地址
			checkcodeUrl = 'http://yjs.ustc.edu.cn/checkcode.asp' 
			# 发送图片的请求，获取图片数据流，
			checkcodeData = self.sess.get(checkcodeUrl, headers=self.headers).content
			# 获取验证码里的文字，需要手动输入
			text = self.getCheckcode(checkcodeData)
			# 构造登录数据
			data = {
				'txt_check' : text,
				'userid' : self.userId,
				'userpwd' : self.userPwd,
				'x' : '34',
				'y' : '8'
			}
		elif self.loginApi==2:
			# 使用科大统一身份认证作为登录接口
			loginUrl = 'http://passport.ustc.edu.cn/login?service=http%3A%2F%2Fyjs%2Eustc%2Eedu%2Ecn%2Fdefault%2Easp'
			# 首先获取登录页面，找到需要POST的数据（_token)，同时会记录当前网页的Cookie值
			loginHtml = self.sess.get(loginUrl, headers=self.headers).text
			_token_pattern = re.compile(r'"_token".*?value="(.*?)"')
			_token = _token_pattern.search(loginHtml).group(1)
			# 构造登录数据
			data = {
				'_token' : _token,
				'login' : self.userId,
				'password' : self.userPwd,
				'button' : '登录'
			}			
		else:
			print '登录接口设置错误，请检查配置文件`conf.py`...'
			os._exit(0)
		
		# 发送登录需要的POST数据，获取登录后的Cookie(保存在sess里)
		print '正在进入教务系统...'
		response = self.sess.post(loginUrl, data=data, headers=self.headers)
		# 获取学生信息
		stuInfoHtml = self.getStuInfoHtml()
		# 打印学生信息，并返回是否查询成功
		loginResult = self.printStuInfo(stuInfoHtml)
		# 返回登录是否成功
		return loginResult

	def getScoreHtml(self):
		'''
			作用：获取成绩页面源码
			返回：成绩页面源码
		'''
		print '正在查询您的成绩，请稍候...'
		# 用已有登录状态的Cookie发送请求，获取目标页面源码
		response = self.sess.get('http://yjs.ustc.edu.cn/score/m_score.asp', headers=self.headers)
		scoreHtml = response.text.encode('utf-8')
		return scoreHtml

	def printScore(self, scoreHtml, isSave, savePath):
		'''
			作用：打印成绩
			score_html：包含成绩信息的html页面
			isSave：是否保存成绩信息
			savePath：成绩信息保存路径
		'''
		# 表头信息的正则
		tablebHeadPattern = re.compile(r'<TD\s.*?bgcolor="#EDEDED">(.*?)</TD>', re.S)
		tablebHead = tablebHeadPattern.findall(scoreHtml)
		# 去除多余的空格并打印表头
		for item in tablebHead:
			item = item.strip()
		# 课程成绩信息的正则
		scorePattern = re.compile(r'<td class="bt06" >(.*?)</td>', re.S)
		scoreInfo = scorePattern.findall(scoreHtml)
		# 将各门成绩被分别以列表的形式保存，方便后面打印
		scoreList = []
		for i in range(len(scoreInfo)/len(tablebHead)): # 一共有多少门课
			oneCourseScore = []
			for j in range(len(tablebHead)):
				oneCourseScore.append(scoreInfo[i*len(tablebHead)+j].strip())
			scoreList.append(oneCourseScore)
		# 开始打印成绩 
		print '{}的【成绩信息】如下：'.format(self.userName)
		# 构造成绩表格
		prettyTableHead = tablebHead[2:6]+tablebHead[8:10]
		scoreTable = PrettyTable(prettyTableHead)
		for i in range(len(scoreList)):
			prettyTableRow = scoreList[i][2:6]+scoreList[i][8:10]
			scoreTable.add_row(prettyTableRow)
		# 打印成绩表
		print scoreTable
		if isSave:
			with open(savePath, 'a') as f:
				f.write('【{}】\n'.format(time.ctime()))
				f.write('='*80+'\n{}的【成绩信息】如下：\n'.format(self.userName))
				f.write(str(scoreTable)+'\n\n\n')

	def queryScore(self, isSave, savePath):
		'''
			作用：查成绩
		'''
		# 登录并获取结果
		loginResult = self.yjsLogin()
		if loginResult:
			scoreHtml = self.getScoreHtml()
			# 打印成绩信息
			self.printScore(scoreHtml, isSave, savePath)
			print '已退出...谢谢使用！'
		else:
			print '进入教务系统失败...谢谢使用！'

def main():
	# 加载配置信息
	userAccounts = USER_ACCOUNTS
	if USTC_YJS_PLATFORMS_LOGIN_API:
		loginApi = 1
	elif USTC_UNIFIED_IDENTITY_AUTHENTICATION_LOGIN_API:
		loginApi = 2
	else:
		loginApi = 0

	# 构造一个成绩查询对象
	query = QueryScore(userAccounts, loginApi)
	# 查询并打印成绩
	query.queryScore(OUT_PUT_LOG_TO_FILE_ENABLED, OUT_PUT_LOG_TO_FILE_PATH)

if __name__ == '__main__':
	main()

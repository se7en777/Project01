#!/usr/bin/env  python3
# -*- coding: utf-8 -*-
"""
 File Name：  spider04
 Author :  seven
 Change Activity:
	 2018/11/13:
"""
# 获取多页多种类型的图片链接 多线程下载

# !/usr/bin/env  python3
# -*- coding: utf-8 -*-
"""
 File Name：  spider03
 Author :  seven
 Change Activity:
	 2018/11/13:
"""

import urllib
import urllib.request
import re
import random
import time
import threading

user_agent = ["Mozilla/5.0 (Windows NT 10.0; WOW64)", 'Mozilla/5.0 (Windows NT 6.3; WOW64)',
			  'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
			  'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
			  'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
			  'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
			  'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
			  'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
			  'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
			  'Opera/9.27 (Windows NT 5.2; U; zh-cn)', 'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
			  'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
			  'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
			  'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
			  'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
			  'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
			  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
			  'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
			  'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
			  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
			  'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
			  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11']


# 通过正则表达式获取多种格式的图片
def get_img(html):
	reg = r'data-original="(.+?\.jpg|\.jpeg|\.png|\.bmp|\.gif)"'
	imgre = re.compile(reg)
	org_url = re.findall(imgre, html)
	return org_url


img_list = []
for page in range(1, 2):
	if page == 1:  # 第一页url格式有点特殊
		url = 'https://www.haha.mx/pic/good'
	else:  # 第二页开始格式一致
		url = 'https://www.haha.mx/pic/good/' + str(page)
	request = urllib.request.Request(url=url,
									 headers={"User-Agent": random.choice(user_agent)})  # 随机从user_agent列表中抽取一个元素
	try:
		response = urllib.request.urlopen(request)
	except urllib.error.HTTPError as e:  # 异常检测
		print('page=', page, '', e.code)
	except urllib.error.URLError as e:
		print('page=', page, '', e.reason)

	content = response.read().decode('utf-8')  # 读取网页内容
	print('get page', page)  # 打印出当前获取的页数
	img_url = get_img(content)

	# 检查并修正获取到的URL格式,这里遇到的问题是获取到的url没有以http:开头
	# 直接用正确的值，替换掉img_url列表中格式不对的值，不改变index
	is_url = re.compile('^http[s]?://.+?')
	for url in img_url:
		if not is_url.match(url):
			index = img_url.index(url)
			img_url[index] = 'http:' + url
		else:
			img_list.extend(img_url)

	# img_list.extend(img_url)
	time.sleep(random.randrange(1, 3))  # 每抓一页，随机等待几秒



img_list = list(set(img_list))
print('已删除重复链接，一共抓取图片链接' + str(len(img_list)) + '个')
# for i in (img_list):
# 	print(i)
#
# print(img_list)


# 单线程下载
# x = 0
# for img_url in img_list:
# 	print(x)
# 	urllib.request.urlretrieve(img_url, 'e:\\temp\\%s.jpg' % x)
# 	x += 1
# 	time.sleep(random.randrange(1, 3))  # 每抓一页随机休眠几秒，数值可根据实际情况改动

# # 多线程下载
# 定义下载单个图片的函数
def dnld_1(dnld_url, index):
	try:
		urllib.request.urlretrieve(img_list[index], 'e:\\temp2\\%s.jpg' % (index + 1))
		# time.sleep(random.randrange(1, 3))
		print('第' + str(index + 1) + '张图片下载成功\n')
	except:
		print('图片' + str(index + 1) + '下载失败\n')


# 多线程下载
index = 0
threads = []
for img_url in range(len(img_list)):
	print('准备下载第' + str(index + 1) + '张图片')
	thread = threading.Thread(target=dnld_1, args=(img_list, index))
	threads.append(thread)
	thread.setDaemon(True)
	thread.start()
	index += 1
	# 并发50个线程的时候，在while循环里无线循环，少于50个进程，到上级for循环启动新的进程
	while True:
		if (len(threading.enumerate())) < 50:
			break
	if len(img_list) > 0:
		print('列表已经取完，下载结束。')
	else:
		for thread in threads():
			if len(img_list) > 0:
				print('列表已经取完，下载结束。')
			else:
				if not thread.is_alive():
					threads.remove(thread)
				thread.join()
print('Done.')



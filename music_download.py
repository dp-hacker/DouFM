#-*- coding: UTF-8 -*-

import urllib2,urllib,os
import re,sys,time
# deal with the error ascii out range
# 从douFM上下载歌曲，根据歌名或者歌手搜索

default_encoding = 'utf-8'  # 解决Django错误：'ascii' codec can't decode byte 0xef in position 0: ordinal not in range(128)解决方法
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def split_str(str): # 分解字符串
    s = str.decode('utf-8')
    p  = re.compile(ur'[^\u4e00-\u9fa5]')
    return len(re.findall(p,s))

def ch_format(string,n):
    str = string
    num = split_str(str)
    if len(str.decode('unicode_escape'))<n:
        str+=((2*(n-len(str.decode('unicode_escape')))-num)/3) *' '
    # str+=(n-(2/3*len(str.decode('unicode_escape'))+num/3))*' '
    return str


class mp3_download():
    def __init__(self):
        self.base_url = 'http://doufm.info/api/music/?'
        self.download_base_url = 'http://doufm.info'
        self.name_list = []
        self.url_list = []
        self.artist_list = []
        self.url = ''
        self.default_path = 'Music'

    @property
    def get_data(self):  # 根据输入信息获取web页面，使用urllib2
        print """1.歌曲
2.歌手"""
        choice = raw_input("请输入选择(Q退出)：")
        if choice not in ['1','2','Q']:
            print "请输入正确选择:"
            self.get_data
        if choice == '2':
            search = raw_input('歌手:')
            data = {'artist' : search}
            self.url =self.base_url + urllib.urlencode(data) + '&end=-1&start=0'
        elif choice =='1':
            search = raw_input('歌曲:')
            data = {'title' : search}
            self.url = self.base_url+'end=-1&start=0&' + urllib.urlencode(data)
        # print self.url
        elif choice =='Q':
            sys.exit(0)
        # print self.url
        try:
            request = urllib2.Request(self.url)
            response = urllib2.urlopen(request,timeout = 5)
            html = response.read()
        except urllib2.HTTPError , e:
            print "ERROR Retrieving data :",e
            print "error documents as follows\n"
            print e.read()
            sys.exit(1)
        except urllib2.URLError , e:
            print "Error retrieving data:",e
        finally :
            response.close()
        return html

    def get_list(self,html):  # 根据正则表达式在get_data（）的页面中选取所需的歌曲名歌手以及url
        name_pattern = re.compile(r'.*?"title": "(.*?)",.*?')  # 此处pattern添加“,”，解决音乐自带引号问题
        self.name_list = re.findall(name_pattern ,html)
        url_pattern = re.compile(r'.*?"audio": "(.*?)".*?')
        self.url_list = re.findall(url_pattern ,html)
        artist_pattern = re.compile(r'.*?"artist": "(.*?)".*?')
        self.artist_list = re.findall(artist_pattern,html)
        num_1 = len(self.name_list)
        num_2 = len(self.url_list)
        # print self.artist_list
        if num_1 == 0:
            print "搜索不到结果，返回搜索首页\n"
            self.Start()
        if num_1 == num_2 :
            i = 1
            while i <= num_1:
                # print self.name_list[i-1]
                name = eval("u\""+self.name_list[i-1]+"\"")
                artist = eval("u\""+self.artist_list[i-1]+"\"")
                # print artist
                # print ("%-5d%-30s%s"%(i,name,artist))#搜索歌手时的输出格式尚未解决
                sys.stdout.write('%-5d'%i)
                sys.stdout.write('%s'%ch_format(name,50))
                sys.stdout.write('%s'%ch_format(artist,20))
                sys.stdout.write('\n')
                # print ('%s'%artist)
                # print i
                i+=1

    def before_download(self):  # 根据输入编号,返回下载编号列表
        num = raw_input("输入需要下载歌曲的编号：(空格分开，A全部下载，R返回搜索首页)\n")
        # print type(num)
        if num == 'A' or num == 'a':
            NUM = range(len(self.name_list)+1)[1:]  # 所有编号
        elif num == 'R':
            self.Start()
        else :
            try:  # 判断编号是否在范围内以及是否为数字
                for key in [int(s) for s in num.split(' ')]:
                    if key in range(len(self.name_list)+1)[1:]:
                        continue
                    else :
                        print "请输入正确序号:"
                        self.download()
            except ValueError :
                print "请输入正确编号:"
                self.download()
            NUM = set(num.split(' '))
        return NUM

    def after_download(self):  # 下载完成之后，根据用户输入，返回相应的界面
        choice = raw_input("输入C继续下载，输入R返回首页，Q退出\n")
        if choice == 'C':
            self.download()
        elif choice == 'R':
            self.name_list = []
            self.url_list = []
            self.artist_list = []
            self.Start()
        elif choice == 'Q':
            sys.exit(0)
        else :
            print "请输入正确选择:"
            self.after_download()


    def Start_download(self,url,path,number):
        print "正在下载……"
        start_time = time.time()
        urllib.urlretrieve(url,path)
        end_time = time.time()
        use_time = end_time - start_time  # 计算花费时间 时间戳
        print "编号为%d的歌曲下载完成，花费%.2f秒"%(number+1,float(use_time))

    def download(self):
        download_list=self.before_download()
        base_path = raw_input('请输入存储位置：')
        if not len(base_path):
            base_path = self.default_path
        if not os.path.exists(base_path):
            print "请输入正确路径:"
            #base_path = raw_input('请输入存储位置：')
            self.download()
        for item in download_list:  # 下载模块
            number = int(item) - 1
            download_url = self.download_base_url + self.url_list[number]
            path = base_path + '/'+eval("u\""+self.name_list[number]+"\"")+'-'+eval("u\""+self.artist_list[number]+"\"")+'.mp3'
            while os.path.exists(path):
                choice = raw_input("编号%d歌曲已经存在，是否继续下载？(Y or N)\n"%int(item))
                if choice == 'Y':
                    self.Start_download(download_url,path,number)
                    break
                elif choice == 'N':
                    break
                else:
                    print "请输入正确的选择:"
                    continue
            else :
                self.Start_download(download_url,path,number)
            # print "error"
        self.after_download()


    def Start(self):
        html = self.get_data
        self.get_list(html)
        self.download()

if __name__ == '__main__':
    print"""程序：豆瓣音乐下载
作者：DHS
时间：2015.9.18
问题：搜索歌手输出格式
    """
    R = mp3_download()
    R.Start()






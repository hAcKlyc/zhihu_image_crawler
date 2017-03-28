import urllib.request
import requests
import urllib.parse
import json
from bs4 import BeautifulSoup
import os
from proxy_IP import getProxy

class getZhihuQPic():
    def __init__(self):
        abc = getProxy()
        self.post_url = 'https://www.zhihu.com/node/QuestionAnswerListV2'

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Referer": "https://www.zhihu.com/question/39284255",
            "Cookie": 'q_c1=eb9b5724184749389bd5692871292a42|1484058457000|1484058457000; cap_id="ZjU4NDVkMjdhNGJiNDRjZGExNjM3NzFmZTA1MDJkMzA=|1484742533|b234827a487d0c79232ed5f5fce3724c1042d10b"; l_cap_id="NDdmZDk3OTQ3NTU1NGYyZWIxMWZkYzc2ZmMzMmEzZDA=|1484742533|6f5d6c9e04058baf0767adfa15544469fffe9a7f"; d_c0="ACAC5WlFIguPTtvqxhONV41UqsSzg6nmETc=|1484058458"; r_cap_id="OTFiNWFkZDkyNDhjNGY4MmI0ZjM3YTllNDhkYjNjMGY=|1484742534|8dae6a084f749b941d205bc1b94fc488efb86aab"; _zap=9ca787f7-2945-46cb-a4dd-214012f5e007; login="NjE2NWQ3YzE4YjNhNDliMGEyODQzYmM5MTFiYTM1YTk=|1484742546|35161d458278d486e8c3d75026991b5941502d9f"; _xsrf=0019a34eccfe90165a44cdff664fb51f; z_c0=Mi4wQUFCQWZNc1pBQUFBSUFMbGFVVWlDeGNBQUFCaEFsVk5rdXltV0FCN1BGbF9mRFZoOGo3X3R1UkZpRzNtX0hUMDZR|1484811412|c754a3149aef9e528c48a048888393886085cb5d; aliyungf_tc=AQAAAEw0dGYiAAQAtWa13Oo0zZbRpZIU; s-q=%E6%8A%93%E5%8F%96%20%E7%9F%A5%E4%B9%8E%20%E6%9B%B4%E5%A4%9A; s-i=14; sid=qf31de8g; s-t=autocomplete'
        }
        self.headers_post = {
            "Host": "www.zhihu.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.zhihu.com/question/39284255",
            "Cookie": 'q_c1=eb9b5724184749389bd5692871292a42|1484058457000|1484058457000; cap_id="ZjU4NDVkMjdhNGJiNDRjZGExNjM3NzFmZTA1MDJkMzA=|1484742533|b234827a487d0c79232ed5f5fce3724c1042d10b"; l_cap_id="NDdmZDk3OTQ3NTU1NGYyZWIxMWZkYzc2ZmMzMmEzZDA=|1484742533|6f5d6c9e04058baf0767adfa15544469fffe9a7f"; d_c0="ACAC5WlFIguPTtvqxhONV41UqsSzg6nmETc=|1484058458"; r_cap_id="OTFiNWFkZDkyNDhjNGY4MmI0ZjM3YTllNDhkYjNjMGY=|1484742534|8dae6a084f749b941d205bc1b94fc488efb86aab"; _zap=9ca787f7-2945-46cb-a4dd-214012f5e007; login="NjE2NWQ3YzE4YjNhNDliMGEyODQzYmM5MTFiYTM1YTk=|1484742546|35161d458278d486e8c3d75026991b5941502d9f"; _xsrf=0019a34eccfe90165a44cdff664fb51f; z_c0=Mi4wQUFCQWZNc1pBQUFBSUFMbGFVVWlDeGNBQUFCaEFsVk5rdXltV0FCN1BGbF9mRFZoOGo3X3R1UkZpRzNtX0hUMDZR|1484811412|c754a3149aef9e528c48a048888393886085cb5d; aliyungf_tc=AQAAAEw0dGYiAAQAtWa13Oo0zZbRpZIU; s-q=%E6%8A%93%E5%8F%96%20%E7%9F%A5%E4%B9%8E%20%E6%9B%B4%E5%A4%9A; s-i=14; sid=qf31de8g; s-t=autocomplete',
            "Connection": "keep-alive"
        }
        self.contents = []
        self.image_urls=set()
        self.proxies = abc.getOneUrl()

    def getMaxnum(self,url_token):
        full_url = 'https://www.zhihu.com/question/' + str(url_token)
        request = urllib.request.Request(full_url, headers=self.headers)
        response = urllib.request.urlopen(request)
        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        # 整个答案数量
        data_num = soup.find('h3', id="zh-question-answer-num").get('data-num')
        return int(data_num)

    def getTitle(self,url_token):
        full_url = 'https://www.zhihu.com/question/' + str(url_token)
        request = urllib.request.Request(full_url, headers=self.headers)
        response = urllib.request.urlopen(request)
        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        file_title = soup.find('h2',class_="zm-item-title").get_text()
        return file_title

    def getPicUrl(self):
        content = "".join(self.contents)
        soup = BeautifulSoup(content, 'html.parser')
        image_url_tem = soup.find_all('img', class_="origin_image zh-lightbox-thumb lazy")
        for url_tem in image_url_tem:
            self.image_urls.add(url_tem.get('data-original'))

    def getContent(self,url_token,page_num):
        post_url2 = 'https://www.zhihu.com/api/v4/questions/%s/answers?sort_by=default&include=data[*].is_normal,is_sticky,collapsed_by,suggest_edit,comment_count,collapsed_counts,reviewing_comments_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,mark_infos,created_time,updated_time,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].author.is_blocking,is_blocked,is_followed,voteup_count,message_thread_token,badge[?(type=best_answerer)].topics&limit=20&offset=23'%url_token
        data = {
            "method": "next",
            "params": '{"url_token":%d,"pagesize":10,"offset":%d}' % (url_token, page_num)
        }
        session = requests.session()
        session.headers = self.headers_post
        postdata = urllib.parse.urlencode(data)
        #page = session.post(self.post_url, data=postdata)
        page = session.get(post_url2)
        try:
            dic = json.loads(page.content.decode('utf-8'))
            # li = dic['msg'][0]
            #print(len(dic['msg']))
            self.contents.extend(dic['msg'])
        except:
            print('返回值失效')
        return

    def downloadPic(self,url_token):
        count = 1
        #title = self.getTitle(url_token)
        #path = os.getcwd()
        path = 'D:\\py_data'
        os.makedirs(str(path)+'\\image_%s'%url_token)
        url_img = len(self.image_urls)
        for url in self.image_urls :
            try:
                urllib.request.urlretrieve(url,str(path)+'\\image_%s\\%s.png'%(url_token,count))
            except:
                print("链接失效")
            print("正在下载第%d/%d张图片"%(count,url_img))
            count = count +1
        print("已经下载完毕,共下载%d张图片"%count)
        print("Enjoy it!")

    def start(self,url_token):
        page_num = 0
        #if url_token is None:
        #    url_token = input("请输入要抓取的问题ID")
        max_num = self.getMaxnum(url_token)
        zushu = int(max_num)/10
        count = 1
        while True:
            print("开始抓取第%d/%d组答案内容"%(count,zushu))
            self.getContent(url_token,page_num)
            if page_num > max_num:
                break
            page_num += 10
            count += 1
        print("抓取内容成功，准备开始抓取图片链接")
        self.getPicUrl()
        print("图片链接抓取完毕，准备开始下载")
        self.downloadPic(url_token)

if __name__ == '__main__':
    code = int(input("请输入要抓取问题ID:"))
    if code == '':
        code = 39284255
        print("未输入数字，默认抓取问题ID=39284255")
    abc = getZhihuQPic()
    abc.start(code)

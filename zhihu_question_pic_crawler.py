import os
import time
import random
import re
import socket
import urllib.request
import threading
import logging

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    # 日志级别
    level=logging.INFO,
    # 日志格式
    # 时间、代码所在文件名、代码行号、日志级别名字、日志信息
    format=
    '%(asctime)s-%(levelname)s:\033[1;36m %(message)s \033[0m| %(funcName)s - %(threadName)s - %(filename)s [line:%(lineno)d]',
    # 打印日志的时间
    datefmt='%H:%M:%S',
    # # 日志文件存放的目录（目录必须存在）及日志文件名
    # filename = 'd:/report.log',
    # # 打开日志文件的方式
    # filemode = 'w'
)

socket.setdefaulttimeout(10)

STORAGE_PATH = './storage/'
URL_CACHE_TXT_PATH = 'img_url.txt'
USE_PROXY = False
REQ_NUM_MAX = 99999
NULL_TIMES = 5  # 判断抓取结束的标志
WAIT_TIME = 8  # 初始等待启动下载器时间
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.910.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.49",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.2631.169 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_26) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.5975.128 Safari/537.36"
]


class zhihuQuestionPicCrawler():
    def __init__(self, use_proxy=False, question_id=None):
        # self.use_proxy = USE_PROXY # 代理功能未做实现，实测小批量抓取还不需要
        self.headers = {"User-Agent": random.choice(UA_LIST)}

        if question_id is not None:
            self.question_id = question_id
        else:
            self.question_id = self._get_question_id()
        self.downloaded_url = []
        self.is_crawling = True
        self.url_cache_file = str(self.question_id) + '_' + URL_CACHE_TXT_PATH

    def _get_question_id(self):
        question_id = input('请输入待抓取的问题ID：')
        return str(question_id)

    def crawl_answer_image(self,
                           question_id='366062253',
                           req_num_max=REQ_NUM_MAX):
        offset = 5
        all_answer_info = []
        req_num = 1
        null_times = 0
        while True:
            logging.info('开始第{req_num}次请求'.format(req_num=req_num))
            resp_json = self._get_answer_content(
                question_id=question_id, offset=offset)
            req_num += 1
            offset += 5

            if resp_json is not None:
                cache = self._parse_answer_content(resp_json)
                if isinstance(cache, list):
                    if len(cache[0].get('imgs')) == 0:
                        null_times += 1
                all_answer_info.extend(cache)
                self._save_download_url_to_txtfile(cache)
            else:
                logging.info('请求数据为空，结束本轮抓取')
                self.is_crawling = False
                break

            # 抓取结束后sleep
            time.sleep(3.14)

            # 结束判定
            if req_num > req_num_max:  # for debuging
                self.is_crawling = False
                break  # for debuging

            if null_times > NULL_TIMES:  # 多次获取失败，则判定抓取结束
                self.is_crawling = False
                break

        return all_answer_info

    def _get_answer_content(self, question_id, limit=5, offset=5):
        include = "data%5b*%5d.is_normal%2cadmin_closed_comment%2creward_info%2cis_collapsed%2cannotation_action%2cannotation_detail%2ccollapse_reason%2cis_sticky%2ccollapsed_by%2csuggest_edit%2ccomment_count%2ccan_comment%2ccontent%2ceditable_content%2cvoteup_count%2creshipment_settings%2ccomment_permission%2ccreated_time%2cupdated_time%2creview_info%2crelevant_info%2cquestion%2cexcerpt%2crelationship.is_authorized%2cis_author%2cvoting%2cis_thanked%2cis_nothelp%2cis_labeled%2cis_recognized%2cpaid_info%2cpaid_info_content%3bdata%5b*%5d.mark_infos%5b*%5d.url%3bdata%5b*%5d.author.follower_count%2cbadge%5b*%5d.topics"
        post_url = 'https://www.zhihu.com/api/v4/questions/{question_id}/answers?include={include}&limit={limit}&offset={offset}&platform=desktop&sort_by=default'
        url = post_url.format(
            question_id=question_id,
            include=include,
            limit=limit,
            offset=offset)
        resp = requests.get(url, headers=self.headers)
        if resp:
            # logging.info(resp.json())
            if resp.status_code == 200:
                logging.info('请求成功：{0}'.format(resp.status_code))
                return resp.json()
            else:
                logging.warning('请求异常：{0}'.format(resp.status_code))
                logging.warning(resp.text)
        else:
            logging.warning('请求失败，无结果')

    def _parse_answer_content(self, resp_json):
        # 从中取出所有image数据
        # answer_id
        answer_content_info = []
        answer_content = resp_json['data']
        tem_dict = {}
        for answer in answer_content:
            tem_dict['answer_id'] = answer.get('id')
            try:
                tem_dict['imgs'] = self._parse_img_from_content(
                    content=answer.get('content'))
            except Exception as e:
                logging.info(e)
            answer_content_info.append(tem_dict)
            tem_dict = {}
        return answer_content_info

    def _parse_img_from_content(self, content):
        soup = BeautifulSoup(content, 'lxml')
        imgs = []
        img_ = soup.findAll('img',
                            {'class': 'origin_image zh-lightbox-thumb lazy'})
        for i in img_:
            imgs.append(i['data-original'])
        img_num = len(imgs)
        logging.info('图片解析成功，获得图片：{0}张'.format(img_num))
        return imgs

    def _save_download_url_to_txtfile(self, data):
        logging.info('开始写入请求数据')
        write_cache = []
        for i in data:
            img_url = i.get('imgs')
            if img_url is not None:
                write_cache.extend(img_url)
        write_num = len(write_cache)
        logging.info('共获取{0}条数据，准备写入'.format(write_num))
        if write_num != 0:
            with open(self.url_cache_file, 'a') as f:
                for i in write_cache:
                    f.write(str(i))
                    f.write('\r\n')
        else:
            logging.warning('待写入数据为空，停止写入')

    def download_answer_imgs(self):
        # 读取待抓取数据
        imgs = []
        with open(self.url_cache_file, 'r') as f:
            img_urls = f.readlines()
        if isinstance(imgs, list):
            logging.info('待抓取数据读取成功')
            logging.info('共{0}张图片待下载'.format(len(imgs)))
        else:
            logging.warning('未获取到有效数据')

        vaild_urls = self._get_vaild_download_url(all_urls=img_urls)
        if len(vaild_urls) == 0:
            logging.info('暂无有效可下载数据,等待10s后重试')
            time.sleep(10)
            return None
        # 本次读取txt中url将作已下载的url列表，下一次查重时会被抛弃
        self.downloaded_url = img_urls
        # 使用查重后的url 进行下载
        self._download_files(urls=vaild_urls)

    def _get_vaild_download_url(self, all_urls):
        vaild_urls = []
        for url in all_urls:
            if url not in self.downloaded_url:
                vaild_urls.append(url)
        return vaild_urls

    def _download_files(self, urls):
        path = STORAGE_PATH + str(self.question_id) + os.sep
        if not os.path.isdir(path):
            os.mkdir(path)
        count = 1
        total_num = len(urls)
        for url in urls:
            try:
                file_name = re.search(r'\.com\/(.*?_r\.jpg)', url).group(1)
            except Exception as e:
                logging.error(e)
                file_name = str(int(time.time()))
            try:
                file_path = path + file_name
                # logging.info(file_path)
                urllib.request.urlretrieve(url, file_path)
            except Exception as e:
                logging.error(e)
                logging.error("链接失效")
            logging.info("正在下载第%d/%d张图片" % (count, total_num))
            count = count + 1
        logging.info("已经下载完毕,共下载%d张图片" % count)
        logging.info("Enjoy it!")

    def start_downloading(self):
        # 方法封装，用于多线程调用
        while self.is_crawling == True:
            self.download_answer_imgs()
        logging.info('检测到抓取结束，执行最后一轮下载')
        self.download_answer_imgs()
        logging.info('图片全部下载完成！')

    def start_crawling(self):
        # 方法封装，用于多线程调用
        cache = self.crawl_answer_image(question_id=self.question_id)
        logging.info(
            '本次数据抓取完毕，共抓取到{answer_num}条答案下的数据'.format(answer_num=len(cache)))

    def start(self):
        # 单线程运行 - 可运行
        try:
            cache = self.crawl_answer_image(question_id=self.question_id)
            logging.info('本次数据抓取完毕，共抓取到{answer_num}条答案下的数据'.format(
                answer_num=len(cache)))
        except Exception as e:
            logging.error(e)
            self.download_answer_imgs()

    def multi_thread_start(self):
        # 多线程运行 - 推荐使用
        logging.info('启动多线程爬虫模式')
        crawlThread = threading.Thread(target=self.start_crawling)
        downloadThread = threading.Thread(target=self.start_downloading)
        logging.info('启动抓取线程')
        crawlThread.start()
        logging.info('等待%d后，开启下载线程' % WAIT_TIME)
        time.sleep(WAIT_TIME)
        logging.info('启动下载线程')
        downloadThread.start()


if __name__ == '__main__':
    zhihuPic = zhihuQuestionPicCrawler()
    zhihuPic.multi_thread_start()
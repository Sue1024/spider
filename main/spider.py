# 爬虫分析
from bs4 import BeautifulSoup
import lxml.html
etree = lxml.html.etree
from selenium import webdriver
import time
from pymongo import MongoClient
import requests
import re
import hashlib

session = requests.session()

HEADERS = {
    'Referer': 'https://passport.lagou.com/login/login.html',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:51.0) Gecko/20100101 Firefox/51.0',
}

class WorkSpider:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.zfdb = self.client.spider
        self.zfdb.authenticate("sue", "123456")

    # 要爬取的城市列表
    def getCity(self):
        return [
            "全国",
            "北京",
            "上海",
            "深圳",
            "广州",
        ]

    # 要爬取的语言列表
    def getLanguage(self):
        return [
            "Java",
            "Python",
            "C",
            "机器学习",
            "图像识别",
            "自然语言处理",
            "区块链",
            "精准推荐",
            "Node.js",
            "Go",
            "Hadoop",
            "Php",
            ".NET",
            "Android",
            "iOS",
            "web前端",
        ]

    def get_token(self):
        Forge_Token = ""
        Forge_Code = ""
        login_page = 'https://passport.lagou.com/login/login.html'
        data = session.get(login_page, headers=HEADERS)
        match_obj = re.match(r'.*X_Anti_Forge_Token = \'(.*?)\';.*X_Anti_Forge_Code = \'(\d+?)\'', data.text, re.DOTALL)
        if match_obj:
            Forge_Token = match_obj.group(1)
            Forge_Code = match_obj.group(2)
        return Forge_Token, Forge_Code

    def login(self, username, passwd):
        X_Anti_Forge_Token, X_Anti_Forge_Code = get_token()
        login_headers = HEADERS.copy()
        login_headers.update({'X-Requested-With': 'XMLHttpRequest', 'X-Anit-Forge-Token': X_Anti_Forge_Token,
                              'X-Anit-Forge-Code': X_Anti_Forge_Code})
        postData = {
            'isValidate': 'true',
            'username': username,
            'password': get_password(passwd),
            'request_form_verifyCode': '',
            'submit': '',
        }
        response = session.post('https://passport.lagou.com/login/login.json', data=postData, headers=login_headers)
        print(response.text)

    def get_cookies(self):
        return requests.utils.dict_from_cookiejar(session.cookies)

    # 经过观察发现，拉钩的 url 随语言和城市的变化如下
    def getUrl(self, language, city):
        url = "https://www.lagou.com/jobs/list_" + language + "?px=default&city=" + city
        return url

    # 获取一个城市，列表中所有语言的 url 列表
    def getCityUrl(self, city):
        urlList = []
        for language in self.getLanguage():
            urlList.append(self.getUrl(language, city))
        return urlList

    # 获取一门语言，不同城市的 url 列表
    def getLanguageUrl(self, language):
        urlList = []
        for city in self.getCity():
            urlList.append(self.getUrl(language, city))
        return urlList

    def getOnePageData(self):

        pass

    # MongoDB 存储数据结构
    def getRentMsg(self, name, company, welfare, salaryMin, salaryMid, salaryMax, experience, education, companyType,
                   companyLevel, companySize):
        return {
            "name": name,  # 职位名称(python工程师)
            "company": company,  # 公司名称（xxx有限公司）
            "welfare": welfare,  # 福利（餐补、下午茶、带薪年假）
            "salaryMin": salaryMin,  # 工资下限（9k）
            "salaryMid": salaryMid,  # 工资下限（9k+15k）/2
            "salaryMax": salaryMax,  # 工资上限（15k）
            "experience": experience,  # 工作经验（经验3-5年）
            "education": education,  # 教育程度（本科）
            "companyType": companyType,  # 公司类型（移动互联网/信息安全）
            "companyLevel": companyLevel,  # 公司级别（上市公司）
            "companySize": companySize,  # 公司人数规模（150-500人）

        }


    # 获取网页源码数据
    # language => 编程语言
    # city => 城市
    # collectionType => 值：True/False  True => 数据库表以编程语言命名   False => 以城市命名
    def get_password(self, passwd):
        '''这里对密码进行了md5双重加密 veennike 这个值是在main.html_aio_f95e644.js文件找到的 '''
        passwd = hashlib.md5(passwd.encode('utf-8')).hexdigest()
        passwd = 'veenike' + passwd + 'veenike'
        passwd = hashlib.md5(passwd.encode('utf-8')).hexdigest()
        return passwd
    def main(self, language, city, collectionType):

        # r1 = session.get('https://passport.lagou.com/login/login.html',
        #                  headers={
        #                      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        #                  },
        #                  )
        #
        # X_Anti_Forge_Token = re.findall("X_Anti_Forge_Token = '(.*?)'", r1.text, re.S)[0]
        # X_Anti_Forge_Code = re.findall("X_Anti_Forge_Code = '(.*?)'", r1.text, re.S)[0]
        # print(X_Anti_Forge_Code, X_Anti_Forge_Token)

        # r2 = session.post('https://passport.lagou.com/login/login.json',
        #                   headers={
        #                       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        #                       'Referer': 'https://passport.lagou.com/login/login.html',
        #                       'X-Anit-Forge-Code': X_Anti_Forge_Code,
        #                       'X-Anit-Forge-Token': X_Anti_Forge_Token,
        #                       'X-Requested-With': 'XMLHttpRequest'
        #                   },
        #                   data={
        #                       "isValidate": True,
        #                       'username': '17521662140',
        #                       'password': self.get_password('091001jane'),
        #                       'request_form_verifyCode': '',
        #                       'submit': ''
        #                   }
        #                   )
        # r3 = session.get('https://passport.lagou.com/grantServiceTicket/grant.html',
        #                  headers={
        #                      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        #                      'Referer': 'https://passport.lagou.com/login/login.html',
        #                  }
        #
        username = '1371XXXXXXX'
        passwd = 'xxxxxxxxxx'
        login(username, passwd)
        print(get_cookies())
        print(" 当前爬取的语言为 => " + language + "  当前爬取的城市为 => " + city)
        print(" 当前爬取的语言为 => " + language + "  当前爬取的城市为 => " + city)
        print(" 当前爬取的语言为 => " + language + "  当前爬取的城市为 => " + city)
        url = self.getUrl(language, city)
        browser = webdriver.Chrome("./chromedriver")
        browser.get(url)
        browser.implicitly_wait(10)
        for i in range(30):
            selector = etree.HTML(browser.page_source)  # 获取源码
            soup = BeautifulSoup(browser.page_source, "html.parser")
            span = soup.find("div", attrs={"class": "pager_container"}).find("span", attrs={"action": "next"})
            print(
                span)  # <span action="next" class="pager_next pager_next_disabled" hidefocus="hidefocus">下一页<strong class="pager_lgthen pager_lgthen_dis"></strong></span>
            classArr = span['class']
            print(classArr)  # 输出内容为 -> ['pager_next', 'pager_next_disabled']
            classArrList = list(classArr);
            classArrListLen = len(classArrList)
            if classArrListLen == 2 and classArrList[1] == "pager_next_disabled":
                print("已经爬到最后一页，爬虫结束")
                break
            else:
                print("还有下一页，爬虫继续")
                browser.find_element_by_xpath('//*[@id="order"]/li/div[4]/div[2]').click()  # 点击下一页
            time.sleep(5)
            print('第{}页抓取完毕'.format(i + 1))
            self.getItemData(selector, language, city, collectionType)
        browser.close()

    # 解析一条 item 数据，并存进数据库
    def getItemData(self, selector, language, city, collectionType):
        items = selector.xpath('//*[@id="s_position_list"]/ul/li')
        for item in items:
            try:
                name = item.xpath('div[1]/div[1]/div[1]/a/h3/text()')[0]
                company = item.xpath('div[1]/div[2]/div[1]/a/text()')[0]
                welfare = item.xpath('div[2]/div[2]/text()')[0]
                salaryArray = item.xpath('div[1]/div[1]/div[2]/div/span/text()')[0].strip().split("-")
                salaryMin = salaryArray[0][:len(salaryArray[0]) - 1]
                salaryMax = salaryArray[1][:len(salaryArray[1]) - 1]
                salaryMid = (int(salaryMin) + int(salaryMax)) / 2
                educationArray = item.xpath('div[1]/div[1]/div[2]/div//text()')[3].strip().split("/")
                education = educationArray[0].strip()
                experience = educationArray[1].strip()
                conmpanyMsgArray = item.xpath('div[1]/div[2]/div[2]/text()')[0].strip().split("/")
                companyType = conmpanyMsgArray[0].strip()
                companyLevel = conmpanyMsgArray[1].strip()
                companySize = conmpanyMsgArray[2].strip()

                data = self.getRentMsg(
                    name,
                    company,
                    welfare,
                    int(salaryMin),
                    salaryMid,
                    int(salaryMax),
                    experience,
                    education,
                    companyType,
                    companyLevel,
                    companySize
                )
                if collectionType:
                    self.zfdb["z_" + language].insert(data)
                else:
                    self.zfdb["z_" + city].insert(data)

                print(data)
            except:
                print("=======  exception  =======")
                continue




spider = WorkSpider()# 职业爬虫
for language in spider.getLanguage():
    spider.main(language, "深圳", True)
    time.sleep(5)

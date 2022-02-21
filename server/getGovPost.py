import json
from multiprocessing.context import Process
import os
from pyjsparser import parse
from urllib.parse import urlparse, parse_qs
import re
import requests
import asyncio
from bs4 import BeautifulSoup

class GetGovPost:
    def __init__(self) -> None:
        self.FILENAME = "./gov.txt"
        self.baseUrl = 'https://www.moe.go.kr'
        self.firstPageUrl = 'https://www.moe.go.kr/boardCnts/listRenew.do?boardID=312'
        self.response = requests.get(self.firstPageUrl)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def goView(self, reqBoardID, reqBoardSeq, reqLev, reqStatusYN, reqCurrPage, reqWriterYN):
        _url = "/boardCnts/viewRenew.do?boardID="+reqBoardID+"&boardSeq="+reqBoardSeq+"&lev="+reqLev+"&searchType=null&statusYN="+reqStatusYN+"&page="+reqCurrPage+"&s=moe&m="+"0301"+"&opType=N"
        return _url

    def refine(self, _str):
        return _str.replace('"', r'\"').replace("'", r'\"').replace(u'\xa0', u'')

    def refine2(self, _str):
        return _str.replace(u'\xa0', u'').replace("'", '"').replace('\\\\', '\\')

    def getData(self):
        ret = []
        
        pagination = self.soup.select_one('#txt > section > div:nth-child(3) > div > a.end')
        fullUrl = self.baseUrl + parse(pagination['onclick'])['body'][0]['expression']['right']['value']
        parsed_url = urlparse(fullUrl)
        pageLen = parse_qs(parsed_url.query)['page'][0]
        for page in range(int(pageLen)):
            print('Page: {0}'.format(page + 1))
            # pass value to parent
        #     pass
        # for page in range(1):
            url = 'https://www.moe.go.kr/boardCnts/listRenew.do?type=default&page={0}&m=0301&prntBoardID=0&searchType=S&s=moe&prntBoardSeq=0&prntLev=0&boardID=312'.format(page + 1)
            _soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            if requests.get(url).status_code == 200:
                tbody = _soup.select_one('#txt > section > div:nth-child(2) > div > table > tbody')
                if tbody is None:
                    titles = []
                else:
                    titles = tbody.select('tr > td > a')
                for title in titles:
                    try:
                        dct = {}
                        k = title['onclick']
                        p = re.findall("'(\w+)'",k)
                        _response = requests.get(self.baseUrl + self.goView(p[0], p[1], p[2], p[3], p[4], p[5]))
                        if _response.status_code == 200:
                            _soup = BeautifulSoup(_response.text, 'html.parser')
                            _metaData = _soup.select_one('#txt > section:nth-child(1) > div:nth-child(1) > div > table > tbody > tr:nth-child(2)').find_all('td')
                            _content = _soup.select_one('#txt > section:nth-child(1) > div:nth-child(1) > div > table > tbody > tr:nth-child(4) > td > div')
                            _fileSection = _soup.select_one('#txt > section:nth-child(1) > div:nth-child(1) > div > table > tbody > tr:nth-child(3) > td > ul')
                            dct['제목'] = self.refine(title.get_text().strip())
                            dct['등록일'] = self.refine(_metaData[0].get_text().strip())
                            dct['업로더'] = self.refine(_metaData[1].get_text().strip())
                            dct['조회수'] = self.refine(_metaData[2].get_text().strip())
                            dct['본문내용'] = self.refine(_content.get_text().strip())
                            if not(_fileSection is None or len(_fileSection.find_all('li')) == 0):
                                files = _fileSection.find_all('li')
                                idx = 1
                                for file in files:
                                    fileName = file.contents[0].strip()
                                    _downloadTag = _soup.select_one('#txt > section:nth-child(1) > div:nth-child(1) > div > table > tbody > tr:nth-child(3) > td > ul > li > a:nth-child(1)')
                                    _downloadUrl = self.baseUrl + _downloadTag['href']
                                    dct['파일이름-{0}'.format(idx)] = self.refine(fileName)
                                    dct['link-{0}'.format(idx)] = self.refine(_downloadUrl)
                                    idx = idx + 1
                        else:
                            print(_response.status_code)
                        ret.append(dct)
                    except AttributeError:
                        continue
            else : 
                print(self.response.status_code)
        return ret

    def get(self):
        with open(self.FILENAME, 'w') as f:
            results = self.getData()
            f.write("[\n")
            for idx, row in enumerate(results):
                if idx < len(results) - 1:
                    f.write("%s,\n" % self.refine2(str(row)))
                else:
                    f.write("%s" % self.refine2(str(row)))
            f.write("\n]")
            

    async def run(self):
        try:
            totalPostCount = self.soup.select_one('#txt > section > div:nth-child(1) > strong > span')
            try:
                if not(os.stat(self.FILENAME).st_size == 0):
                    with open(self.FILENAME, 'r') as f:
                        json_data = json.load(f)
                        if len(json_data) == int(totalPostCount.get_text()):
                            print('리프레시 필요 없음.')
                            quit()
                        else:
                            print('리프레시 필요.')
                            self.get()
                            print('done refreshing!')
                else:
                    print('파일 비어 있음.')
                    self.get()
                    print('done refreshing!')
            except FileNotFoundError:
                self.get()
                print('done refreshing!')
        except AttributeError:
            print('error!')

    def process(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.run())
        print(result)
        loop.stop()

if __name__ == '__main__':
    pass
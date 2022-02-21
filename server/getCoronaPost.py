import json
from pyjsparser import parse
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

class GetCoronaPost:
    def __init__(self) -> None:
        self.url = 'http://ncov.mohw.go.kr/tcmBoardList.do?brdId=&brdGubun=&dataGubun=&ncvContSeq=&contSeq=&board_id=140&gubun='
        self.baseUrl = 'http://ncov.mohw.go.kr/'
        self.response = requests.get(self.url)
        self.FILENAME = "./corona.txt"
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def view(self, _values):
        return 'http://ncov.mohw.go.kr/tcmBoardView.do?brdId={0}&brdGubun={1}&dataGubun=&ncvContSeq={2}&contSeq={3}&board_id={4}&gubun={5}'.format(_values[1], _values[2], _values[3], _values[3], _values[4], _values[5])

    def getData(self):
        ret = []
        pagination = self.soup.select_one('#content > div > div.paging > a.p_last')
        pageLen = int(parse(pagination['onclick'].split('; ')[0])['body'][0]['expression']['arguments'][0]['value'])
        # for page in range(int(pageLen)):
        #     # pass value to parent
        #     with self.lock:
        #         self.q.put(page + 1)
        #     pass
        for page in [1]:
            fullUrl = 'http://ncov.mohw.go.kr/tcmBoardList.do?pageIndex={0}&brdId=&brdGubun=&board_id=140&search_item=1&search_content='.format(page)
            _soup = BeautifulSoup(requests.get(fullUrl).text, 'html.parser')
            tbody = _soup.select_one('#content > div > div.board_list > table > tbody')
            for tag in tbody.find_all('tr'):
                dct = {}
                _t = tag.find_all('td')
                _index = _t[0].get_text().strip()
                _onclick = _t[1].find('a')['onclick']
                _title = _t[1].find('a').get_text().strip()
                _uploader = _t[2].get_text().strip()
                _date = _t[3].get_text().strip()
                dct['인덱스'] = _index
                dct['제목'] = _title
                dct['업로더'] = _uploader
                dct['작성일'] = _date
                _args = parse(_onclick)['body'][0]['expression']['arguments']
                _values = []
                for _arg in _args:
                    _values.append(_arg['value'])
                _bs = BeautifulSoup(requests.get(self.view(_values)).text, 'html.parser')
                contentHtml = str(_bs.select_one('#content > div > div.board_view > div.bv_content > div')).replace(u'\xa0', u'')
                dct['본문내용'] = contentHtml
                _attachments = _bs.select('#content > div > div.board_view > div.bv_file > div.bvf_lst > ul')
                for _attach in _attachments:
                    for idx, _li in enumerate(_attach.find_all('li')):
                        _file_url = self.baseUrl + _li.find('a')['href']
                        parsed = urlparse(_file_url).query
                        _file_name = parse_qs(parsed)['file_name']
                        dct['파일이름-{0}'.format(idx + 1)] = _file_name[0]
                        dct['link-{0}'.format(idx + 1)] = _file_url
                ret.append(dct)
        return ret

    def get(self):
        with open(self.FILENAME, 'w') as f:
            results = self.getData()
            f.write(json.dumps(results, ensure_ascii=False))

if __name__ == '__main__':
    gcp = GetCoronaPost()
    gcp.get()
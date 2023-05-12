from database import getdb
import requests
from bs4 import BeautifulSoup
import time
import traceback

head = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Cookie": "yunsuo_session_verify=c36b1e82f4969a52767d7b3763380253",
"Host": "www.ccgp-hebei.gov.cn",
"If-Modified-Since": "Mon, 14 Nov 2022 07:46:44 GMT",
"If-None-Match": "e58b-5ed6970e4235d",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"
}

urllib = {
    "张家口old": "http://search.hebcz.cn:8080/was5/web/search?channelid=240117&lanmu=zbggAAASAAAS&admindivcode=130700000&province=130700000",
    "张家口": "http://search.hebcz.cn:8080/was5/web/search?channelid=240117&perpage=50&outlinepage=10&lanmu=zbgg&admindivcode=1307"

}


def get_page_number(url):
    # result = requests.request("get", url)
    # soup = BeautifulSoup(result.content, 'html.parser')
    # result = soup.find_all("a", class_="last-page")[0]['href']
    # page_start = result.find('page')
    # result = result[page_start+5:]
    # page_end = result.find("&")
    # result = int(result[:page_end])
    return 3


def get_all(city, ac=""):
    base_url = urllib[city]
    # 获取有多少页
    page_num = get_page_number(base_url)
    # db
    db = getdb()
    newlist = []
    # 逐页爬取
    for i in range(page_num):
        chongfu = False
        trycount = 0
        maxtry = 5
        while True:
            try:
                print("采购网:尝试获取第%s页的数据"%(i+1))
                url = base_url + "&page=%s"%(i+1)
                result = requests.request("get", url)
                soup = BeautifulSoup(result.content, 'html.parser')
                a = soup.find_all("a", class_="a3")
                b = soup.find_all("td", class_="txt1")
                assert len(a)==len(b)
                for i in range(len(a)):
                    href = a[i]['href']
                    name = a[i].text.strip()
                    blist = b[i].find_all("span")
                    time_all = blist[0].text.strip().split("-")
                    time_year = int(time_all[0].strip())
                    time_month = int(time_all[1].strip())
                    time_day = int(time_all[2].strip())
                    area = blist[1].text.strip()
                    people = blist[2].text.strip()

                    dbresult = db.count_documents({"source": "hbcg", "href":href})
                    if dbresult==0:
                        d = {
                            "name": name,
                            "href": href,
                            "date_y": time_year,
                            "date_m": time_month,
                            "date_d": time_day,
                            "area": area,
                            "people": people,
                            "source": "hbcg",
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        print("采购网:遇到重复数据")
                        chongfu = True
                        break
                time.sleep(10)
                break
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                trycount += 1
                if trycount > maxtry:
                    db.db.close()
                    return "ERROR!"
                time.sleep(100)
        if chongfu:
            break
    db.db.close()
    return newlist


if __name__ == "__main__":
    get_all("张家口")






















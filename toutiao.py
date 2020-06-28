import requests
import os
from hashlib import md5
import re
from selenium import webdriver 
from multiprocessing.pool import Pool
max_page=30
base_url='https://www.toutiao.com/api/search/content/?'
params = {
        'aid': '24',
        'app_name': 'web_search',
        'offset': '0',
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
    }
#自动化测试模拟获得cookies
def get_cookies(url):
    options=webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser=webdriver.Chrome(options=options)
    browser.get(url)
    str=''
    for item in browser.get_cookies():      #字典转化为cookies格式
        try:
            str=str+item.get('name')+'='+item.get('value')+';'
        except ValueError as e:
            print(e)
    return str
def get_one_ajax(offset):
    params['offset']=offset
    try:
        response=requests.get(base_url,params=params,headers=headers)
        if response.status_code==200:
            return response.json()
        return None
    except Exception:
        return None
#生成器，每次循环调用一次就解析一张照片
def parse_one_ajax(text):
    if text:
        items=text.get('data')
        if items:
            for item in items:
                title=item.get('title')
                urls=item.get('image_list')
                if urls:
                    for url in urls:
                        image_url=url.get('url')
                        print(image_url)
                        yield{
                            'title':title,
                            'image_url':image_url
                        }
def save_one_image(item):
    title=re.sub('[\|,\s]*','',item.get('title'))
    if not os.path.exists('C:\\Users\\19233\Desktop\\Python3网络爬虫开发实战书籍项目\\%s' % title ):
        os.mkdir('C:\\Users\\19233\\Desktop\\Python3网络爬虫开发实战书籍项目\\%s' % title )
    try:
        response=requests.get(item.get('image_url'),timeout=10,headers=headers)
        print(response.status_code)
        if response.status_code==200:
            file_path='C:\\Users\\19233\Desktop\\Python3网络爬虫开发实战书籍项目\\{0}\\{1}.{2}'.format(title,md5(response.content).hexdigest(),'jpeg')
            if not os.path.exists(file_path):
                with open(file_path,'wb') as f:
                    f.write(response.content)
    except requests.ConnectionError:
        print('ERROR')
headers={
    'cookie':get_cookies('https://www.toutiao.com'),
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    'x-requested-with': 'XMLHttpRequest'
}
def main(offset):
    text=get_one_ajax(offset)
    for item in parse_one_ajax(text):
        save_one_image(item)

if __name__=='__main__':
    pool=Pool()
    pool.map(main,[x*20 for x in range(max_page+1)])    #map函数把第一个参数函数作用于第二个可迭代的参数
    pool.close()    #调用join前必须先关闭进程，不再添加新的进程
    pool.join()     #等待进程结束
    print('OK!!')
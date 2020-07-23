import os
from lxml import etree
import requests
import queue  # 保证pyinstaller能正确打包requests库
import re


class TBSpider:
    def __init__(self, url, root):
        self.url = url

        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/73.0.3683.103 Safari/537.36'}
        self.root = root
        self.src = 'http://imgsrc.baidu.com/forum/pic/item/'
        self.piclis = []

    def get_source(self):
        # 实现类似do-while的效果
        nx = 1
        while nx:
            # 获取网页
            try:
                r = requests.get(self.url, headers=self.header)
            except:
                return 0
            html = etree.HTML(str(r.text))
            # 获取图片url，并过滤广告图片
            templis = html.xpath('//img[@class="BDE_Image" and not(@ad-dom-img="true")]/@src')
            for href in templis:
                self.piclis.append(href.split('/')[-1])

            # 如果有“下一页”，继续爬取
            nx = re.search(r'<a href="(/p/\d+\?pn=\d+)">下一页</a>', str(r.text))
            if nx:
                self.url = 'https://tieba.baidu.com/' + nx.group(1)

        return self.piclis

    # 独立下载模块
    def download_isolated(self):
        try:
            length = len(self.piclis)
            count = 0
            # 下载图片
            for pic in self.piclis:
                itemsrc = self.src + pic
                # pic是图片名称
                path = self.root + '/' + pic
                if not os.path.exists(self.root):
                    os.mkdir(self.root)
                if not os.path.exists(path):
                    # 写入文件
                    item = requests.get(itemsrc, headers=self.header)
                    with open(path, 'wb') as f:
                        f.write(item.content)
                count += 1
                print(f'\r下载进度：{count}/{length}')

        except IOError:
            return '--- 下载失败 ---'
        else:
            return '--- 下载成功 ---'

    def download(self, pic, name):
        try:
            # 下载图片
            itemsrc = self.src + pic
            # name是图片名称
            path = self.root + '/' + name
            # 不存在指定文件夹则创建
            if not os.path.exists(self.root):
                os.mkdir(self.root)
            # 若当前路径唯一则写入文件
            if not os.path.exists(path):
                # 写入文件
                item = requests.get(itemsrc, headers=self.header)
                with open(path, 'wb') as f:
                    f.write(item.content)

            return 1
        # 处理IO异常
        except IOError:
            return 0

    def test(self):
        print(self.url)
        print(self.root)


if __name__ == '__main__':
    url = 'https://tieba.baidu.com/p/6203103182'
    root = 'F:\\test'
    tb = TBSpider(url, root)
    tb.get_source()
    tb.download_isolated()

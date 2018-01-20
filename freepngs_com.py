#coding:utf8
'''
freepngs.com网站的爬虫
这个网站比较特殊，数据都是各种json,没有直接在html中显示，使用了jsonpath来解析json文件。
get_all_json是获取到所有页面的json，执行一次就可以。
get_document_data是从页面的json文件中获取2个关键的参数，组成获取iframe(页面内的内嵌html)的URL
get_all_data是从iframe的json文件中获取这个网站的所有数据的，图片的URL，title，subcat，description，并存入数据库
fail_process 处理请求失败的URL，去数据库中取数据，重新发起请求
get_html 发起http请求，返回数据
get_cat_from_mysql 根据子类，获取数据库中的主类
get_proxy 去数据库中提取代理
'''
import re,requests,json,jsonpath,MySQLdb
from data_queue import data_queue
class freepng():
    myqueue = data_queue()
    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', '123456', 'freepngs_201801')
        self.cursor = self.db.cursor()
    def get_all_json(self):
        url = 'https://www.freepngs.com'
        html = self.get_html(url,'get_all_json')
        if html is not None:
            re_compile = re.compile(r'"pageJsonFileName":"(\w{44}.json)?"')
            jsons = re.findall(re_compile,html)
            for i in jsons:
                url = 'https://static.wixstatic.com/sites/%s.z?v=3' % i
                self.myqueue.push(url=url,def_name='get_ducument_data')
    def get_document_data(self):
        data = self.myqueue.pop(def_name='get_document_data')
        print data
        if data:
            url = data[1]
            html = self.get_html(url,'get_document_data')
            if html is not None:
                html = json.loads(html)
                exterid = jsonpath.jsonpath(html,'$..referenceId')
                if exterid:
                    exterid = exterid[0]
                    print exterid
                    compid = jsonpath.jsonpath(html,"$..items")
                    if compid:
                        text = compid[0]
                        print compid
                        re_compid = re.compile(r'"sourceId":"([\w-]{13})?"')
                        compid = re.findall(re_compid,text)
                        if compid:
                            compid = compid[0]
                            url = 'https://progallery.wix.com/gallery.html?compId=%s&deviceType=desktop&externalId=%s&instance=heS7iIBsS_OaGarU5Vei4JhXCFVWu-S83cSquoNdMo8.eyJpbnN0YW5jZUlkIjoiZmQ3MjdkOTQtNDZkNy00ZDYyLWJkOWEtNDVlMmQ4MDE5MWM3IiwiYXBwRGVmSWQiOiIxNDI3MWQ2Zi1iYTYyLWQwNDUtNTQ5Yi1hYjk3MmFlMWY3MGUiLCJzaWduRGF0ZSI6IjIwMTgtMDEtMDlUMDY6MDI6NDkuMTYzWiIsInVpZCI6bnVsbCwiaXBBbmRQb3J0IjoiNDUuMzMuNy4zMi8zODMyOCIsInZlbmRvclByb2R1Y3RJZCI6bnVsbCwiZGVtb01vZGUiOmZhbHNlLCJvcmlnaW5JbnN0YW5jZUlkIjoiY2YzYTk1ZjctODc0Yy00NWRkLWE0YzktN2JhMTFkN2FmODFiIiwiYWlkIjoiOThiNDdmNDgtMmJjZC00Mjg3LTllYzUtYWRmNmU0Y2JlYmY3IiwiYmlUb2tlbiI6IjE1ZmJmYzg2LTQ0YmItMGRlZi0zOTg0LTMwZjRiOGUzZTc2NiIsInNpdGVPd25lcklkIjoiMmNkNDNiMDUtMTY5Yi00NGVjLWE5MWUtY2I0MDJlNWQ2MWI5In0' % (compid, exterid)
                            print url
                            return url
            else:
                print '这个是主类页面,不用爬取'
        else:
            print '数据库没有数据了；'
    def get_iframe(self,url):
        html = self.get_html(url,'get_iframe')
        if html is not None:
            re_baseurl = re.compile(r'window.infiniteScrollUrl = "(.*)?";')
            base_url = re.findall(re_baseurl,html)
            if base_url:
                print base_url
                base_url = base_url[0]+'from/0/to/1000?instance='
                re_instance = re.compile(r'window.instance = "(.*)?";')
                instance = re.findall(re_instance,html)
                if instance:
                    print instance
                    url = base_url + instance[0]
                    return url
    def get_all_data(self,url):
        html = self.get_html(url,'get_all_data')
        if html is not None:
            html= json.loads(html)
            titles = jsonpath.jsonpath(html,"$..title")
            print 'titles      ',titles
            url = jsonpath.jsonpath(html,"$..mediaUrl")
            descs = jsonpath.jsonpath(html,"$..description")
            if url:
                print url
                i = 0
                for i in range(0,len(url)):
                    download_url = 'https://static.wixstatic.com/media/' + url[i]
                    print download_url
                    if titles:
                        title = titles[0]
                        subcat = re.sub(r'-png-\d+','',title)
                        if 'pngs' in subcat:
                            subcat = subcat.replace('pngs','')
                        if 'icon' in subcat:
                            subcat = subcat.replace('icon','')
                        if 'PNGs' in subcat:
                            subcat = subcat.replace('PNGs','')
                        if 'PNG' in subcat:
                            subcat = subcat.replace('PNG','')
                        if 'images' in subcat:
                            subcat = subcat.replace('images','')
                        if 'image' in subcat:
                            subcat = subcat.replace('image','')
                        if 'free' in subcat:
                            subcat = subcat.replace('free','')
                        if 'Free' in subcat:
                            subcat = subcat.replace('Free','')
                        if 'cutouts' in subcat:
                            subcat = subcat.replace('cutouts','')
                        if 'cutout' in subcat:
                            subcat = subcat.replace('cutout','')
                        if 'holiday' in subcat:
                            subcat = subcat.replace('holiday','')
                        if 'collection' in subcat:
                            subcat = subcat.replace('collection','')
                        if 'Letter' in subcat:
                            subcat = subcat.replace('Letter','')
                        if 'Number' in subcat:
                            subcat = subcat.replace('Number','')
                        if ',' in subcat:
                            subcat = subcat.replace(',',' ')
                        if ':' in subcat:
                            subcat = subcat.replace(':',' ')
                        if 'transparent' in subcat:
                            subcat = subcat.replace('transparent',' ')
                        if 'ex' in subcat:
                            subcat = subcat.replace('ex',' ')
                        subcat = subcat.strip()
                        cat = self.get_cat_from_mysql(subcat)
                        if descs:
                            desc = descs[0].strip('- ')
                            if '\\' in desc:
                                desc = desc.replace('\\','`')

                            if cat:
                                sql = 'insert into freepngs_pdts (cat,subcat,title,download_url,description) VALUES ("%s","%s","%s","%s","%s")' % (cat,subcat,title,download_url,desc)
                            else:
                                sql = 'insert into freepngs_pdts (subcat,title,download_url,description) VALUES ("%s","%s","%s","%s")' % (subcat, title, download_url, desc)
                        else:
                            if cat:
                                sql = 'insert into freepngs_pdts (cat,subcat,title,download_url) VALUES ("%s","%s","%s","%s")' % (cat,subcat,title,download_url)
                            else:
                                sql = 'insert into freepngs_pdts (subcat,title,download_url) VALUES ("%s","%s","%s")' % (subcat, title, download_url)
                    else:
                        sql = 'insert into freepngs_pdts (download_url) VALUES ("%s")' % download_url
                    i += 1
                    try:
                        self.cursor.execute(sql)
                        self.db.commit()
                        print '插入成功'
                    except Exception, e:
                        self.db.rollback()
                        print sql
                        print str(e)
    def get_cat_from_mysql(self,subcat):
        sql = 'select cat from freepngs_cat_dict where subcat="%s"' % subcat.title()
        try:
            self.cursor.execute(sql)
            record = self.cursor.fetchone()
            self.db.commit()
            if record:
                cat = record[0]
                return cat
            else:
                return 0
        except Exception,e:
            self.db.rollback()
            print str(e)
    def get_proxy(self):
        # 从数据库中取出代理，给session会话加代理，返回代理信息，给phantomjs也加上代理
        sql = "select * from pngtree_proxy order by status asc limit 1"
        try:
            self.cursor.execute(sql)
            proxies = self.cursor.fetchone()
            # 更新代理时间戳
            sql = "update pngtree_proxy set status=%d where id=%d" % (int(time.time()), proxies[0])
            self.cursor.execute(sql)
            proxy = {
                'http': 'http://%s' % proxie,
                'https': 'https://%s' % proxie,
            }
            self.db.commit()
            return proxy
        except Exception, e:
            print sql
            print str(e)
            self.db.rollback()
    def get_html(self,url,def_name):
        try:
            '''添加代理版'''
            # proxy = self.get_proxy()
            # if proxy:
            #     res = requests.get(url,proxies=proxy)
            # else:
            #     res = requests.get(url)
            '''普通版'''
            res = requests.get(url)
            html = res.text
            return html
        except:
            self.myqueue.push_fail(url=url,def_name=def_name)
            return None
    def fail_process(self):
        data = self.myqueue.pop_fail()
        if data:
            url = data[1]
            def_name = data[2]
            if def_name == 'get_document_data':
                data = self.get_document_data()
                url = self.get_iframe(data)
                self.get_all_data(url)
            elif def_name == 'get_iframe':
                url = self.get_iframe(url)
                self.get_all_data(url)
            elif def_name == 'get_all_data':
                self.get_all_data(url)
        else:
            print '数据库没有失败的数据'










if __name__ == '__main__':
    free = freepng()
    # free.get_all_json()
    data = free.get_document_data()
    if data is not None:
        url = free.get_iframe(data)
        if url is not None:
            free.get_all_data(url)
    # for i in range(20):
    #     url = free.get_document_data()
    #     # url = 'https://static.wixstatic.com/sites/2cd43b_d7587ff16268ea65b182fb8f82e856cf_2884.json.z?v=3'
    #     if url:
    #         free.get_iframe(url)
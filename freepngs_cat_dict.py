#coding:utf8
'''获取freepngs。com网站的主类子类，及其对应关系，存入数据库中'''
import re,json,jsonpath,requests,MySQLdb
db = MySQLdb.connect('localhost', 'root', '123456', 'freepngs_201801')
cursor = db.cursor()

def repalce_amp(strs):
    return strs.repalce('amp;','')
def insert_sql(cat,subcat):
    sql = 'insert into freepngs_cat_dict (cat,subcat) value ("%s","%s")' % (cat,subcat)
    try:
        cursor.execute(sql)
        db.commit()
        print '插入成功'
    except Exception, e:
        db.rollback()
        print str(e)
        print '数据已存在'
def get_subcat(text,cat):
    # 匹配出子类，格式很多，所以正则也比较多
    re_subcat = re.compile(r'underline"><a dataquery="#[\w-]+?">([\w -;&]+)?</a>')
    subcats = re.findall(re_subcat,text)
    for subcat in subcats:
        print '子类是',subcat
        insert_sql(cat,subcat)
    re_subcat1 = re.compile(r'underline">([\w &-;]+)?</span>')
    subcatss = re.findall(re_subcat1, text)
    for subcat1 in subcatss:
        print '子类是', subcat1
        insert_sql(cat, subcat1)
    re_subcat2 = re.compile(r'underline;"><a dataquery="#[\w-]+?">([\w -;&]+)?</a>')
    subcats = re.findall(re_subcat2, text)
    for subcat in subcats:
        print '子类是', subcat
        insert_sql(cat, subcat)
    re_subcat3 = re.compile(r'underline;">([\w &;]+)?</span>')
    subcatss = re.findall(re_subcat3, text)
    for subcat in subcatss:
        print '子类是', subcat
        insert_sql(cat, subcat)
'''爬取分类查看的那个页面，把他们的主类子类抓下来'''
def spider():
    url = 'https://static.wixstatic.com/sites/2cd43b_2b4b6f3b7b93c3d7534fb6d6fc845efc_2857.json.z?v=3'
    res = requests.get(url)
    html = json.loads(res.text)
    texts = jsonpath.jsonpath(html,'$..text')
    re_h1 = re.compile(r'<h1')
    for text in texts:
        match = re.findall(re_h1,text)
        if match:
            re_cat = re.compile(r'>(\w+)? </span></span></a></span></h1>')
            cat = re.findall(re_cat,text)
            if cat:
                # print text
                for i in cat:
                    print i
                    get_subcat(text,i)
            else:
                re_cat1 = re.compile(r'>(\w+)?</span>&nbsp;PNG images.')
                cat = re.findall(re_cat1,text)
                if cat:
                    # print text
                    for i in cat:
                        get_subcat(text,i)
                else:
                    re_cat2 = re.compile(r'>(\w+)?&nbsp;PNG images.')
                    cat = re.findall(re_cat2,text)
                    if cat:
                        for i in cat:
                            print i
                            get_subcat(text,i)
                    else:
                        re_cat3 = re.compile(r'>(\w+)?&nbsp;</a></span></span></span></h1>')
                        cat = re.findall(re_cat3, text)
                        if cat:
                            # print text
                            for i in cat:
                                print i
                                get_subcat(text,i)
                        else:
                            re_cat4 = re.compile(r'>(\w+)? PNG&nbsp;images.')
                            cat = re.findall(re_cat4, text)
                            if cat:
                                for i in cat:
                                    print i
                                    get_subcat(text,i)
                            else:
                                re_cat5 = re.compile(r'>(\w+)?</span></span></a></span></h1>')
                                cat = re.findall(re_cat5, text)
                                if cat:

                                    for i in cat:
                                        if i == 'images.':
                                            print text
                                        else:
                                            print i
                                            get_subcat(text,i)
                                else:
                                    re_cat6 = re.compile(r'(\w+ &amp; \w+)')
                                    cat = re.findall(re_cat6,text)
                                    if cat:

                                        # print text
                                        for i in cat:
                                            i = i.replace('amp;','')
                                            get_subcat(text,i)
                                    else:
                                        re_cat7 = re.compile(r'(\w+)? PNG images.</span></span></a></span></h1>')
                                        cat = re.findall(re_cat7, text)
                                        if cat:

                                            # print text
                                            for i in cat:
                                                print i
                                                get_subcat(text,i)
                                        else:
                                            re_cat8 = re.compile(r'>(\w+)? </a></span></span></span></h1>')
                                            cat = re.findall(re_cat8, text)
                                            if cat:
                                                # print text
                                                for i in cat:
                                                    print i
                                                    get_subcat(text,i)
                                            else:
                                                print text
'''处理数据，把nbsp  还有& 这种替换'''
def data_process():
    sql = 'select id,subcat from freepngs_cat_dict where status=0 limit 1'
    try:
        cursor.execute(sql)
        record = cursor.fetchone()
        db.commit()
        if record:
            id = record[0]
            update_sql = 'UPDATE freepngs_cat_dict set status=1 where id = %d' % id
            try:
                cursor.execute(update_sql)
                db.commit()
                print '状态更新成功'
                subcat = record[1]
                if 'amp;' in subcat:
                    subcat = subcat.replace('amp;','')
                    update_sql = 'UPDATE freepngs_cat_dict set subcat="%s" where id = %d' % (subcat,id)
                    try:
                        cursor.execute(update_sql)
                        db.commit()
                        print 'subcat更新成功'
                    except Exception, e:
                        db.rollback()
                        print str(e)
                elif '&nbsp;' in subcat:
                    subcat = subcat.replace('&nbsp;', ' ')
                    update_sql = 'UPDATE freepngs_cat_dict set subcat="%s" where id = %d' % (subcat, id)
                    try:
                        cursor.execute(update_sql)
                        db.commit()
                        print 'subcat更新成功'
                    except Exception, e:
                        db.rollback()
                elif '&#39;' in subcat:
                    subcat = subcat.replace("&#39;", "'")
                    update_sql = 'UPDATE freepngs_cat_dict set subcat="%s" where id = %d' % (subcat, id)
                    try:
                        cursor.execute(update_sql)
                        db.commit()
                        print 'subcat更新成功'
                    except Exception, e:
                        db.rollback()
            except Exception, e:
                db.rollback()
                print str(e)
    except Exception, e:
        db.rollback()
        print str(e)
        print '数据已存在'
'''统计数据库的数据数量，循环处理数据'''
def count():
    sql = 'SELECT count(id) from freepngs_cat_dict '
    try:
        cursor.execute(sql)
        record = cursor.fetchone()
        db.commit()
        if record:
            max = record[0]
            i = 0
            for i in range(0,int(max)):
                i += 1
                data_process()
    except Exception, e:
        db.rollback()
        print str(e)
        print '没有数据了'


if __name__ == '__main__':
    # spider()
    # data_process()
    count()
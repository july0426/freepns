#coding:utf8
'''
用来管理数据爬取的队列
push  添加一条数据
pop  提取一条数据
push_fail 添加一条处理失败的数据
pop_fail  提取一条处理失败的数据

'''
import MySQLdb


class data_queue():
    # 起始状态，url刚入列的状态
    init_status = 1
    # URL被提取，开始请求的状态
    processing = 2
    # URL请求成功，并处理完成的状态
    completed = 3
    # URL请求失败的状态
    faild = 4
    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', '123456', 'freepngs_201801')
        self.cursor = self.db.cursor()
    def push(self,url,def_name):
        # 将一个URL加入到队列中，subcat是子类，要进行函数间的传递，所以也保存起来
        sql = 'insert into freepngs_data_queue (url,def_name,status) values ("%s","%s","%s")' % (url,def_name,self.init_status)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            print '插入成功'
        except Exception,e:
            self.db.rollback()
            print str(e)
            print 'url已经在队列中'
    def pop(self,def_name):
        #取出一个URL
        # record记录，查询出想要的URL
        # 默认按照插入顺序查找，显示一条，并把状态更改成为正在处理
        select_sql = 'select id,url from freepngs_data_queue where status=1 and def_name="%s" limit 1' % def_name
        try:
            self.cursor.execute(select_sql)
            record = self.cursor.fetchone()
            self.db.commit()
            if record:
                id = record[0]
                update_sql = 'UPDATE freepngs_data_queue set status=2 where id = %d' % id
                try:
                    self.cursor.execute(update_sql)
                    self.db.commit()
                    print '更新成功'
                    return record
                except Exception, e:
                    self.db.rollback()
                    print str(e)
        except Exception,e:
            self.db.rollback()
            print str(e)
            print 'url已经在队列中'

    def push_fail(self,url,def_name):
        # 插入一条失败的URL
        insert_sql = 'insert into freepngs_data_queue (url,status,def_name)  values ("%s","%s","%s")' % (url,4,def_name)
        try:
            self.cursor.execute(insert_sql)
            self.db.commit()
            print '更新成功'
        except Exception, e:
            self.db.rollback()
            print str(e)
    def pop_fail(self):
        # 取出一个爬取失败的URL
        # record记录，查询出想要的URL
        # 默认按照插入顺序查找，显示一条
        select_sql = 'select id,url,def_name from freepngs_data_queue where status=4 limit 1'
        try:
            self.cursor.execute(select_sql)
            record = self.cursor.fetchone()
            self.db.commit()
            if record:
                id = record[0]
                update_sql = 'UPDATE freepngs_data_queue set status=1 where id = %d' % id
                try:
                    self.cursor.execute(update_sql)
                    self.db.commit()
                    print '更新成功'
                    return record
                except Exception, e:
                    self.db.rollback()
                    print str(e)
        except Exception, e:
            self.db.rollback()
            print str(e)
            print 'url已经在队列中'
    # def complete(self,url):
    #     # 把已经完成的URL状态改成已完成
    #     update_sql = 'UPDATE freepngs_data_queue set status=3 where url = "%s"' % url
    #     try:
    #         self.cursor.execute(update_sql)
    #         self.db.commit()
    #         print '更新成功'
    #     except Exception, e:
    #         self.db.rollback()
    #         print str(e)
    # def pop_process(self):
    #     # 取出一个爬取中断的URL
    #     # record记录，查询出想要的URL
    #     # 默认按照插入顺序查找，显示一条
    #     select_sql = 'select id,url from freepngs_data_queue where status=2 limit 1'
    #     try:
    #         self.cursor.execute(select_sql)
    #         record = self.cursor.fetchone()
    #         self.db.commit()
    #         if record:
    #             return record
    #     except Exception, e:
    #         self.db.rollback()
    #         print str(e)
    #         print 'url已经在队列中'
if __name__ == "__main__":
    myqueue = data_queue()
    # myqueue.push('www.duu2.com','deatil','a')
    # myqueue.push('www.duu3.com', 'deatil','b')
    # myqueue.push('www.duuqq.com', 'deatil','b')
    print myqueue.pop()
    myqueue.db.close()

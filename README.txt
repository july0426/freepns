目标网站：www.freepngs.com
数据量：30000-40000
特点：HTML全部基于json数据生成，网页源代码获取不到想要的数据。
对策：根据网站各个页面跳转是请求的数据，依次找到关键的json，通过解析json，来获取想要的数据。

依赖的拓展：
        requests  模拟http请求
        jsonpath  json文件解析
        MySQLdb   mysql数据库连接

数据库：mysql
数据库名字:freepngs_201801
数据表：
    freepngs_pdts:图片的相关数据，本地的存储路径等
    freepngs_data_queue:URL的数据库，主要是URL，函数名字，状态
    freepngs_cat_dict:主类子类的对应关系

data_queue.py: 连接mysql数据库，管理http请求的URL，进行标记。
freepngs_com.py: 爬虫文件，爬取该网站的数据
freepngs_cat_dict.py: 爬取该网站的主类、子类、对应关系，保存在数据库中，爬取数据后，根据子类找到主类进行保存。

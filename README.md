## COVID_19

### 功能：将各国确诊数，死亡数和治愈数存入数据库

### 数据源：Johns Hopkins University 约翰斯·霍普金斯大学

网址：https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series

下的三个global.csv文件。

### 服务器建表

```mysql
CREATE TABLE Covid_19 (
  `ID` int NOT NULL primary key AUTO_INCREMENT,
  `Country` varchar(25) ,
  `Date` date ,
  `Confirm` int ,
  `Deaths` int ,
  `Recovered` int
) 
```


### 修改covid_19.py代码46行和66行

##### 改成自己的数据库地址

```python
conn = pymysql.connect(host='服务器ip', port=3306, user='数据库用户', password='数据库密码', db='库名')
```



### 服务器设置定时任务，每日更新数据库

linux执行：

```python
cd 路径
touch log.txt	#创建日志文件
crontab -e		#编辑定时任务
#每天 n时 m分 执行covid_19.py 输出追加到日志
m n * * * python covid_19.py的绝对路径 >> log.txt日志文件的绝对路径	#加到最后一行
```









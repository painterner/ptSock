## issue
### crypto
只推导了

的形式

但是没有考虑到e|2^n不成立的情况。
ref: https://www.cnblogs.com/idreamo/p/9411265.html
暂时没有去仔细分析其算法, 可能结合有限域等思想来理解会比较容易理解。

大数存储以及运算. 好像有点麻烦, 先用python库来处理吧.


#os 
## centos
### port
https://www.linuxidc.com/Linux/2019-06/159104.htm

[root@centos7 ~]# firewall-cmd --zone=public --add-port=80/tcp --permanent

查询端口号80 是否开启：

[root@centos7 ~]# firewall-cmd --query-port=80/tcp

重启防火墙：

[root@centos7 ~]# firewall-cmd --reload

查询有哪些端口是开启的:

[root@centos7 ~]# firewall-cmd --list-port
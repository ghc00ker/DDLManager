# DDLManager

该项目通过Caldav进行日程管理，通过本地的聊天记录和LLM进行分析

## 使用方法：

1. 根据requirements.txt安装依赖
2. 将.env.example的.example去掉，即改名为.env文件
3. 在.env文件中填入自己的信息
4. 在data中创建自己的聊天记录（具体见后文）
5. 运行根目录下的run.py

## QQ聊天记录获取方法

详见https://github.com/shuakami/qq-chat-exporter ，选择json导出形式

## 关于QQ邮箱的选择

主要是采用了邮箱的**CalDav**服务，经测试QQ邮箱可以使用。其它邮箱请自行搜索使用方法

### QQ邮箱的使用说明

网页版QQ邮箱 -> 个人信息 -> 账号安全 -> 安全设置 -> 开启*POP3/IMAP/SMTP/Exchange/CardDAV 服务* -> 生成授权码

# 最后

个人能力有限，有问题请及时反馈！也欢迎交流想法。联系方式 QQ: 2663469147

感谢使用！可以的话点一下小星星
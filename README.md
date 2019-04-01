# Dead By Unicode

![Demo](https://github.com/k9yyy/dead_by_unicode/blob/master/resources/dbu_demo.jpg?raw=true)

**此项目已被[Dead By Unicode GUI](https://github.com/k9yyy/dead_by_unicode_gui)替代。**

## 介绍
这是一个开发中的用于黎明杀机中文聊天的辅助工具。原理是通过HTTP请求接收文本，然后发送按键事件模拟键盘按下Alt{+Unicode}来输入每个字符。

## 运行环境
* 服务端支持在Windows下运行；
* 直接运行Python脚本需要有Python 3环境，运行exe版需要有VC++2010（x86）运行库；
* 用于发送文本的设备（如手机）需要和运行服务端的电脑在同一局域网内。

## 下载
* Python脚本版：使用`git clone`或直接下载zip包；
* exe版：访问 [release页面](https://github.com/k9yyy/dead_by_unicode/releases)
* Python3下载：访问 [Python官网](https://www.python.org/downloads/)
* VC++运行库：访问微软下载页面 [64位](https://www.microsoft.com/zh-cn/download/details.aspx?id=14632) [32位](https://www.microsoft.com/zh-CN/download/details.aspx?id=5555)

## 使用方法
1. 在运行DbD的电脑上，执行`enable_hex_numpad.reg`来导入`EnableHexNumpad`的注册表项，然后注销并重新登录Windows；
2. * 使用Python脚本：在运行DbD的电脑上，用`py -3 dead_by_unicode.py`或者直接执行`dead_by_unicode.py`来启动Dead By Unicode服务端；
   * 使用exe版：在运行DbD的电脑上，直接执行`dead_by_unicode.exe`来启动Dead By Unicode服务端；
3. 出现防火墙提示时，选择允许；如果没有出现提示，需要到Windows防火墙设置中手动放通；
4. 用于发送文本的设备（如手机）上，用浏览器访问`http://<电脑的IP>:<监听端口号>`，监听端口号默认是8081；
5. 在DbD中，将光标定位至聊天框，然后通过上一步中浏览器打开的页面即可发送文本。

## 注意事项
* 传输内容未经过加密和鉴权，模拟按键有被攻击者利用的风险；
* 建议只在可信任的局域网中使用此工具，并且使用完后尽快关闭。

## 命令行参数
* `-a <地址>`或`--listen-address <地址>`：指定监听地址；
* `-p <端口号>`或`--listen-port <端口号>`：指定监听端口号；
* `-d <延时时间>`或`--key-delay <延时时间>`：指定每次按键事件后加入的延时（毫秒）；
* `-v`或`--verbose`：打印调试信息。

## 用py2exe构建exe
https://pypi.org/project/py2exe/

注意不支持最新版本的Python，需要用3.3或3.4。

```
py -3.4 -m pip install py2exe
py -3.4 -m py2exe dead_by_unicode.py -b 0
```

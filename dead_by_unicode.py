#!python3

import socket
import ctypes
import time
import struct
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import argparse, sys

LISTEN_ADDR = "0.0.0.0"		# 监听地址
LISTEN_PORT = 8081			# 监听端口号

KEY_DELAY = 5			# 按键延迟
DEBUG = False			# 打印调试信息

def debug(msg):
	if DEBUG: print(msg)

def vkey_to_scan_code(key_code):
	return ctypes.windll.user32.MapVirtualKeyA(key_code, 0)

def key_down(key_code, ext=False):
	ext_flg = 1 if ext else 0
	scan_code = vkey_to_scan_code(key_code)
	ctypes.windll.user32.keybd_event(key_code, scan_code, ext_flg, 0)
	debug('Key Down: %02x' % key_code)
	time.sleep(KEY_DELAY / 1000)
	
def key_up(key_code, ext=False):
	ext_flg = 1 if ext else 0
	scan_code = vkey_to_scan_code(key_code)
	ctypes.windll.user32.keybd_event(key_code, scan_code, 2 | ext_flg, 0)
	debug('Key Up: %02x' % key_code)
	time.sleep(KEY_DELAY / 1000)
	
def num_key_press(digit): # 输入0x0到0xf的整型，'+'是加号
	key_code = 0
	ext = False
	if digit == '+':
		key_code = 0x6B
		#ext = True
	elif digit >= 0 and digit < 10:
		key_code = digit | 0x60 # 小键盘数字范围 0x60到0x69
	elif digit >= 10 and digit < 16:
		key_code = (digit - 9) | 0x40 # A到F键：0x41到0x46
	key_down(key_code, ext)
	key_up(key_code, ext)
	
def do_hex_input(value):
	debug('Hex value: %04x' % value)
	# l_alt: 0xa4
	key_down(0xa4)
	debug('Pressing +')
	num_key_press('+')
	found_non_zero = False
	for i in range(0, 4): 	# alt+unicode 最高支持16位
		digit = (value >> 4 * (4 - 1 - i)) & 0xf
		if found_non_zero == False:
			if digit == 0: continue
			else: found_non_zero = True
		debug('Pressing digit %1x' % digit)
		num_key_press(digit)
	key_up(0xa4)
	
def enter_string(str):
	debug("Received: " + str)
	for c in str:
		if c == "\n":
			debug("pressing enter")
			key_down(0x0d)
			key_up(0x0d)
		else:
			debug("entering: " + c)
			c_bytes = c.encode('utf-32-le')
			c_value = struct.unpack("<I", c_bytes)[0]
			do_hex_input(c_value)
		
class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		query = self.path.split("?")
		path = query[0]
		params = query[1] if len(query) > 1 else ""
		params = parse_qs(params)
		if path == "/":
			global html_content
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(html_content.encode("utf-8"))
		elif path == "/send":
			if "msg" in params.keys() and params["msg"] != "":
				enter_string(params["msg"][0])
				self.send_response(200)
				self.end_headers()
				self.wfile.write(b"Sent: " + params["msg"][0].replace("\n", "⏎").encode("utf-8"))
			else:
				self.send_response(400)
				self.end_headers()
				self.wfile.write(b"Error: Empty Message")
		else:
			self.send_response(404)
			self.end_headers()
			self.wfile.write(b"Error: Not Found")
	def do_POST(self):
		self.send_response(501)
		self.end_headers()
		self.wfile.write(b"Error: Not Implemented")
		
def main():
	global LISTEN_ADDR, LISTEN_PORT, KEY_DELAY, DEBUG
	parser = argparse.ArgumentParser(description="Dead By Unicode: 黎明杀机中文输入辅助工具")
	parser.add_argument('-a', '--listen-address', metavar='ADDRESS', help="指定监听地址（默认值：%s）" % LISTEN_ADDR)
	parser.add_argument('-p', '--listen-port', type=int, metavar='PORT', help="指定监听端口号（默认值：%d）" % LISTEN_PORT)	
	parser.add_argument('-d', '--key-delay', type=int, metavar='DELAY', help="指定每次发送按键事件后加入的延时（毫秒，默认值：%d）" % KEY_DELAY)
	parser.add_argument('-v', '--verbose', action='store_true', help='打印调试信息')
	parsed_args = vars(parser.parse_args(sys.argv[1:]))
	
	listen_addr = parsed_args["listen_address"]
	listen_port = parsed_args["listen_port"]
	key_delay = parsed_args["key_delay"]
	
	if listen_addr is not None: LISTEN_ADDR = listen_addr
	if listen_port is not None: LISTEN_PORT = listen_port
	if key_delay is not None: KEY_DELAY = key_delay
	
	if parsed_args["verbose"] == True: DEBUG = True
	
	print("Starting HTTP server at: %s:%s" % (LISTEN_ADDR, LISTEN_PORT))
	httpd = HTTPServer((LISTEN_ADDR, LISTEN_PORT), RequestHandler)
	httpd.serve_forever()

html_content = r"""
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dead by Unicode</title>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
</head>
<body style="font-family: 微软雅黑, sans-serif">
<div class="container">
<h1>发送文本</h1>
<form onsubmit="submitForm(); return false">
	<div class="form-group">
		<label for="msg">文本内容</label>
		<input id="msg" placeholder="内容" size="40" autocomplete="off">
	</div>
	<div class="form-check">
		<input class="form-check-input" type="checkbox" value="" id="followByEnter">
		<label class="form-check-label" for="followByEnter">
			自动发送回车
		</label>
	</div>
	<button id="sendButton" type="submit" class="btn btn-default">发送</button>
	<button type="button" onclick="clearMsg()" class="btn btn-default">清除待发消息</button>
	<button id="sendEnterButton" type="button" onclick="sendEnter()" class="btn btn-default">发送回车</button>
</form>
<div id="status"></div>
</div>
<script>
var isSending = false;

function updateStatus(text) {
	$("#status").text(text);
}

function xhrTimeout() {
	updateStatus("连接超时。");
	setIsSending(false);
}

function xhrCallback(status, responseText) {
	console.log("Callback: " + status + ", " + responseText);
	updateStatus(status == 200 ? responseText : responseText + "(" + status + ")");
	setIsSending(false);
}

function setIsSending(flag) {
	$("#sendButton").prop("disabled", flag);
	$("#sendEnterButton").prop("disabled", flag);
	isSending = flag;
}

function setFocus() {
	$("#msg").focus();
	$("#msg").delay(1).select();
}

var timePerChar = %%%TIME_PER_CHAR%%%
function sendMsg(msg) {
	if (isSending) {
		updateStatus("有消息正在发送。");
		return;
	}
	if (msg == "")
	{
		updateStatus("待发消息为空。");
		return;
	}
	console.log("Sending: " + msg);
	var url = "/send?msg=" + msg;
    var xhr = new XMLHttpRequest();
    xhr.onload = function(){ xhrCallback(xhr.status, xhr.responseText) };
    xhr.onerror = function(){ updateStatus("发生了错误。") };
	xhr.ontimeout = xhrTimeout;
	xhr.timeout = timePerChar * msg.length + 10000;
    xhr.open("GET", encodeURI(url), true);
	xhr.send(null);
	setIsSending(true);
	updateStatus("发送中…");
	setFocus();
}

function submitForm() {
	var msg = $("#msg").val();
	if ($('#followByEnter').prop('checked')) msg +=	"\n";
	sendMsg(msg);
}

function clearMsg() {
	$("#msg").val("");
	setFocus();
}

function sendEnter() {
	sendMsg("\n");
}
</script>
</body>
</html>
""".replace("%%%TIME_PER_CHAR%%%", str(KEY_DELAY * 12))

if __name__ == "__main__":
	main()

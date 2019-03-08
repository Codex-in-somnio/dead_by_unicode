#!python3

import socket
import ctypes
import time
import struct
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

LISTEN_IP = "0.0.0.0"		# 监听地址
LISTEN_PORT = 8081			# 监听端口号

KEY_DELAY = 0.0002			# 按键延迟

def vkey_to_scan_code(key_code):
	return ctypes.windll.user32.MapVirtualKeyA(key_code, 0)

def key_down(key_code, ext=False):
	ext_flg = 1 if ext else 0
	scan_code = vkey_to_scan_code(key_code)
	ctypes.windll.user32.keybd_event(key_code, scan_code, ext_flg, 0)
	print('Key Down: %02x' % key_code)
	time.sleep(KEY_DELAY)
	
def key_up(key_code, ext=False):
	ext_flg = 1 if ext else 0
	scan_code = vkey_to_scan_code(key_code)
	ctypes.windll.user32.keybd_event(key_code, scan_code, 2 | ext_flg, 0)
	print('Key Up: %02x' % key_code)
	time.sleep(KEY_DELAY)
	
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
	print('Hex value: %04x' % value)
	# l_alt: 0xa4
	key_down(0xa4)
	print('Pressing +')
	num_key_press('+')
	found_non_zero = False
	for i in range(0, 4): 	# alt+unicode 最高支持16位
		digit = (value >> 4 * (4 - 1 - i)) & 0xf
		if found_non_zero == False:
			if digit == 0: continue
			else: found_non_zero = True
		print('Pressing digit %1x' % digit)
		num_key_press(digit)
	key_up(0xa4)
	
def enter_string(str):
	print("Received: " + str)
	for c in str:
		print("entering: " + c)
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
				self.wfile.write(b"Sent: " + params["msg"][0].encode("utf-8"))
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
	print("Starting HTTP server at: %s:%s" % (LISTEN_IP, LISTEN_PORT))
	httpd = HTTPServer((LISTEN_IP, LISTEN_PORT), RequestHandler)
	httpd.serve_forever()

html_content = """
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
<form onsubmit="sendMsg(); return false">
	<div class="form-group">
		<label for="msg">文本内容</label>
		<input id="msg" placeholder="内容" size="40" autocomplete="off">
	</div>
	<button id="sendButton" type="submit" class="btn btn-default">发送</button>
	<button type="button" onclick="clearMsg()" class="btn btn-default">清除待发消息</button>
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
	isSending = flag;
}

function setFocus() {
	$("#msg").focus();
	$("#msg").delay(1).select();
}

function sendMsg() {
	if (isSending) {
		updateStatus("有消息正在发送。");
		return;
	}
	var msg = $("#msg").val();
	console.log("Sending: " + msg);
	var url = "/send?msg=" + msg;
    var xhr = new XMLHttpRequest();
    xhr.onload = function(){ xhrCallback(xhr.status, xhr.responseText) };
    xhr.onerror = function(){ updateStatus("发生了错误。") };
	xhr.ontimeout = xhrTimeout;
	xhr.timeout = 20000;
    xhr.open("GET", encodeURI(url), true);
	xhr.send(null);
	setIsSending(true);
	updateStatus("发送中…");
	setFocus();
}

function clearMsg() {
	$("#msg").val("");
	setFocus();
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
	main()

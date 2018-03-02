import requests
import re
import random
import configparser
import json
import datetime
import time
import threading
from bs4 import BeautifulSoup
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])

def ptt_Tainan():
    # session為會話對象, verify設置為False,rs能忽略對SSL的驗證
    # http://docs.python-requests.org/zh_CN/latest/user/advanced.html
    #rs = request.session()
    #res = rs.get('https://www.ptt.cc/bbs/Tainan/index.html', verify=False)
    try :
        res = requests.get('https://www.ptt.cc/bbs/Gamesale/index.html')
    except requests.exceptions.ConnectionError as e :
        print (e)
        return ""

    soup = BeautifulSoup(res.text, 'html.parser')
    match = []
    for info in soup.find_all( text=re.compile('PS4|ps4|1207|slim')):
        idRecompile = re.compile('/bbs/Gamesale/M.(.*).html')

        match.append( {'title': info.parent.text,
                       'link': 'http://www.ptt.cc' + info.parent.get( 'href'),
                       'id': idRecompile.match(info.parent.get('href')).group(0) })
    return match


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'

# def getUserId(str_parse):
#     print(str_parse)
#     pattern = re.compile(r'\"userId\": \"(\w+)\"\}')
#     match = pattern.match(str_parse)
#     return match.group(1)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	#pattern = re.compile(r'\{\"type\"\: \"user\", \"userId\": \"(\w+)\"\}')
    #str1 = str(event.source)
    #print(str1)
    #if 'U9f98c03bb3753a859673e68da9568cae' in str1:
    #print(type(str1))
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        message)
    global MyJobControl
    #print(type(event.message.text))
    #print(event.message.text)
    print("JobControl1 is " + MyJobControl.__str__())
    if event.message.text == "on" :
        MyJobControl = True
        print("JobControl1 is " + MyJobControl.__str__())

    if event.message.text == "off" :
        MyJobControl = False
        print("JobControl1 is " + MyJobControl.__str__())

MyJobControl = False

def replyjob():

    #global MyJobControl
     while True :
        while MyJobControl:
            #print('replyjob turn on')
            TainanMatch = ptt_Tainan()
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if len(TainanMatch) > 0 :
                with open('data/history/gamesale.json', 'r+') as file:
                    history = json.load(file)

                    new_flag = False
                    match_flag = False

                    for article in TainanMatch:
                        # 找有沒有符合此文章id的,若有就跳過
                        for matchArticle in history:
                            if matchArticle == article['id']:
                                match_flag = True
                                break
                        if match_flag == False:
                            new_flag = True
                            history.append(article['id'])
                            content = "{}\n{}".format(article['title'], article['link'])
                            # U29f923ae7851a833b43583f35cd9dff1
                            #line_bot_api.push_message('U9f98c03bb3753a859673e68da9568cae', TextSendMessage(text=content))
                            line_bot_api.push_message('U75401acbb67a72481667ad55f10affc2', TextSendMessage(text=content))
                            #line_bot_api.push_message('Udcc166b83b56d970317fbd99f098f967', TextSendMessage(text=content))
                        match_flag = False

                    if new_flag == True :#or new_flag1 == True:
                        file.seek(0)
                        file.truncate()
                        file.write(json.dumps(history))
                    else:

                        print("{}: Nothing".format(now))
            else:
                # line_bot_api.push_message('U9f98c03bb3753a859673e68da9568cae', TextSendMessage(text='很抱歉,現在搜尋不到你要的文章'))
                print("{}: Nothing".format(now))
            time.sleep(30)
        time.sleep( 10 )




    # 下面是會跟著回一樣的訊息,但是前面會附加line id vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    #print("Handle: reply_token: " + event.reply_token + ", message: " + event.message.text)
    # content = "{}: {}".format(event.source.user_id, event.message.text)
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=content))
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(event.message.text)))
    # if event.message.text == '123':
    #     event.message.text = 'honghen123123123123'
    # print("Handle: reply_token: " + event.reply_token + ", user_id: " + event.source.user_id + ", message: " + event.message.text)
    # # 上面是會跟著回一樣的訊息,但是前面會附加line id ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
if __name__ == '__main__':
    CrawlerJob = threading.Thread(target=replyjob,args=[])
    print(1)
    CrawlerJob.start()
    print(2)
    app.run()

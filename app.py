#-*- coding: utf-8 -*-　　 
#-*- coding: cp950 -*-　

import sys
import random
import telegram
import json
import urllib2
from html.parser import HTMLParser  
import urllib
from flask import Flask, request, send_file
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from io import BytesIO
from fsm import TocMachine

app = Flask(__name__)
bot = telegram.Bot(token='398228664:AAEEQqqAx8ssgOObZrvLgAwt83lCN42ZVfg')

f = urllib.urlopen("http://www.vscinemas.com.tw/visPrintShowTimes.aspx?cid=NF&visLang=2")
html = f.read().decode('utf-8')
sss = 0 
total = ""
update = ""

machine = TocMachine(
    states=[
        'user',
        'state_init',
        'state_ask_poem',
        'Laugh',
        'Angry',
        'reply(poem_website)',
        'state_ask_num',
        'list_not_full',
        'check_repeat',
        'ignore_this_num',
        'add_num_into_list',
        'list_full',
        'reply(list)'

    ],
    transitions=[
        {
            'trigger': 'start_bot',
            'source': 'user',
            'dest': 'state_init',
        },
        {
            'trigger': 'advance',
            'source': 'state_init',
            'dest': 'state_ask_poem',
            'conditions': 'is_going_to_state_ask_poem'
        },
        {
            'trigger': 'rand',
            'source': 'state_ask_poem',
            'dest': 'reply(poem_website)',
            'conditions': '==1(Positive)'
        },
        {
            'trigger': 'rand',
            'source': 'state_ask_poem',
            'dest': 'Laugh',
            'conditions': '==2'
        },
        {
            'trigger': 'rand',
            'source': 'state_ask_poem',
            'dest': 'Angry',
            'conditions': '==3'
        },
        {
            'trigger': 'go_back',
            'source': [
                'reply(poem_website)',
                'Laugh',
                'Angry',
                'reply(list)',
                'reply(secret)',
                'reply(message_last)',
                'reply(other)',
                'reply(help_msg)'
            ],
            'dest': 'state_init'
        },
        
        {
            'trigger': 'advance',
            'source': 'state_init',
            'dest': 'state_ask_num',
            'conditions': 'is_going_to_state_ask_num'
        },
        {
            'trigger': 'check_list',
            'source': 'state_ask_num',
            'dest': 'list_not_full',
            'conditions': '=not_full'
        },
        {
            'trigger': 'rand',
            'source': 'list_not_full',
            'dest': 'check_repeat',
            'conditions': '1-49'
        },
        {
            'trigger': 'yes',
            'source': 'check_repeat',
            'dest': 'ignore_this_num'
        },
        {
            'trigger': 'no',
            'source': 'check_repeat',
            'dest': 'add_num_into_list'
        },
        {
            'trigger': 'again',
            'source': 'ignore_this_num',
            'dest': 'state_ask_num'
        },
        {
            'trigger': 'move_on',
            'source': 'add_num_into_list',
            'dest': 'state_ask_num'
        },
        {
            'trigger': 'check_list',
            'source': 'state_ask_num',
            'dest': 'list_full',
            'conditions': '=full'
        },
        {
            'trigger': 'sort',
            'source': 'list_full',
            'dest': 'reply(list)'
        },
       
        {
            'trigger': 'advance',
            'source': 'state_init',
            'dest': 'reply(secret)',
            'conditions': 'is_going_to_secret'
        },

        {
            'trigger': 'advance',
            'source': 'state_init',
            'dest': 'state_parse',
            'conditions': 'is_going_to_state_parse'
        },
        {
            'trigger': 'starttag',
            'source': 'state_parse',
            'dest': 'check_position',
            'conditions': 'Film'
        },
        {
            'trigger': 'beginning',
            'source': 'check_position',
            'dest': 'message+=Film_name',
        },
        {
            'trigger': 'middle',
            'source': 'check_position',
            'dest': 'reply(message)',
        },
        {
            'trigger': 'message_initialize',
            'source': 'reply(message)',
            'dest': 'message+=Film_name',
        },
        {
            'trigger': 'starttag',
            'source': 'state_parse',
            'dest': 'message+=Day',
            'conditions': 'Day'
        },
        {
            'trigger': 'starttag',
            'source': 'state_parse',
            'dest': 'message+=Session',
            'conditions': 'Session'
        },
        {
            'trigger': 'endtag',
            'source': 'state_parse',
            'dest': 'reply(message_last)',
            'conditions': 'html'
        },
        {
            'trigger': 'continue_parse',
            'source': [
                'message+=Film_name',
                'message+=Day',
                'message+=Session'
            ],
            'dest': 'state_parse'
        },
        {
            'trigger': 'advance',
            'source': 'state_init',
            'dest': 'reply(other)',
            'conditions': 'is_going_to_other'
        },
        {
            'trigger': 'advance',
            'source': 'state_init',
            'dest': 'reply(help_msg)',
            'conditions': 'is_going_to_help'
        }

    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global sss
        if tag == "td":
            for name, value in attrs:
                if value == "PrintShowTimesFilm":
                    sss = 1
                if value == "PrintShowTimesDay":
                    sss = 2
                if value == "PrintShowTimesSession":
                    sss = 3

    def handle_data(self, data):
        global sss
        global total
        if sss == 1:
            if total != "":
                update.message.reply_text(total)
                total = ""
            total = total +  "\n\n" + data.encode('utf-8') + "\n"
            sss = 0
        if sss == 2:
            total = total + data.encode('utf-8') + "\n"
            sss = 0
        if sss == 3:
            total = total + "時間 " + data.encode('utf-8') + "\n"
            sss = 0


    def handle_endtag(self, tag):
        global sss
        global total
        if tag == "form":
            update.message.reply_text(total)

def _set_webhook():
    status = bot.set_webhook('https://cd6acfbd.ngrok.io/hook')
    if not status:
        print('Webhook setup failed')
        sys.exit(1)

@app.route('/hook', methods=['POST'])
def webhook_handler():
    test = 0
    t1 = "求籤"
    t2 = "大樂透"
    t3 = "威秀"
    if request.method == "POST":
        global update
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        if update.message.text == "/start":
            start_reply = "歡迎來到廟公bot\n想求籤詩請輸入 求籤\n大樂透電腦選號請輸入 大樂透\n南紡夢時代威秀影片上映時刻表請輸入 威秀";
            data_text = "start"
            update.message.reply_text(start_reply)
        elif update.message.text == t1.decode('utf-8'):
            reply_1 = random.randint(1,60);
            update.message.reply_text(reply_1)
            text = "幫你擲筊的結果為"
            update.message.reply_text(text)
            answer = random.randint(1,3);
            if answer == 1:
                update.message.reply_text("聖筊")
                text1 = "http://www.chance.org.tw/籤詩集/六十甲子籤/台北新莊地藏庵六十甲子籤/籤詩網%20-%20台北新莊地藏庵六十甲子籤_第"
                text2 = "籤.jpg"
                text = text1 + str(reply_1) + text2
                update.message.reply_text(text)
            elif answer == 2:
                update.message.reply_text("笑筊")
                update.message.reply_text("請在心中重新問問題並輸入 求籤") 
            elif answer == 3:
                update.message.reply_text("怒筊")
                update.message.reply_text("請在心中重新問問題並輸入 求籤")
        elif update.message.text == t2.decode('utf-8'):
            reply = ""
            my_list = []
            for i in range(0, 6, 1):
                reply_2 = random.randint(1, 49)
                if (reply_2 in my_list) == True:
                    T = 0
                    while T == 0:
                        reply_2 = random.randint(1, 49)
                        if (reply_2 in my_list) == False:
                            T = 1
                    my_list.append(reply_2)
                else: 
                    my_list.append(reply_2)
            my_list.sort()
            msg = ' '.join(str(e) for e in my_list)
            update.message.reply_text("本廟公幫你選的幸運號碼為: \n" + msg)
#            update.message.reply_text(my_list)
            
        elif update.message.text == "Hi":
            update.message.reply_text("http://cdn.koreaboo.com/wp-content/uploads/2016/12/nayeon-6.jpg")
            reply = "photo"
        elif update.message.text == t3.decode('utf-8'):
            parser = MyHTMLParser()
            parser.feed(html) 
            update.message.reply_text("End")
            parser.close()
            parser.reset()
            update.message.text = ""
        elif update.message.text == "/help":
            update.message.reply_text("求籤詩請輸入 求籤\n大樂透電腦選號請輸入 大樂透\n南紡夢時代威秀影片上映時刻表請輸入 威秀")
        else:
            update.message.reply_text("我還沒有這個功能\n輸入 /help 查看指令")

    return 'ok'

@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')

if __name__ == "__main__":
    _set_webhook()
    app.run()

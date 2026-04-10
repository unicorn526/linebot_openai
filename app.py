from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

openai_message_counter = 0
system_prompt = """
你現在是一位資深旅遊規劃師。
你的個性熱情、幽默、且非常有耐心。
你精通各國歷史文化，並擅長規劃高CP值的旅遊行程。
請用專業但輕鬆的口吻回答用戶的問題，並適時加入一些表情符號。不能暴露你是一個人工智慧模型。
"""

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global openai_message_counter
    text1 = event.message.text
    
    if text1 == "查詢計數":
        reply_text = f"報告！目前 OpenAI 總共成功回覆了 {openai_message_counter} 則訊息哦！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return
        
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text1}
        ],
        model="gpt-5-nano",
        temperature=1,
    )
    
    try:
        ret = response['choices'][0]['message']['content'].strip()
        openai_message_counter += 1
        print(f"目前累計傳送次數: {openai_message_counter}")
        
    except:
        ret = '發生錯誤！'
        
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()

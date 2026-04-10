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

# 【新增】在這裡定義機器人的個性、職業與能力 (System Prompt)
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
    text1 = event.message.text
    
    # 【修改】在 messages 陣列最前方加入 role: system
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
    except:
        ret = '發生錯誤！'
        
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
import linebot

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, MessageAction,
    QuickReplyButton, QuickReply, 
    RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize, PostbackEvent,
)
from linebot.models.actions import PostbackAction
from linebot.models.events import FollowEvent

from sql_command import SQLConnector

app = Flask(__name__)

line_bot_api = LineBotApi('t2lSa2EaUzdKASHT2YAhLINkSDXtSv8VWtM9H0i9dqxVAAdWyJz+RqqqbGSvSILkmTBwW6hwzYDqvd9lI4BlLqjjVblzfSlINlmuFNZKJApLTFAwY+cz4jUPNPbo4kPPzuUJ7izLxNLOemi0NT6kFQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c637057e90cd9866323f4cf509bb06da')

sqlconnector = SQLConnector()

#リッチメニューを作成する関数
def create_richmenu():
    #リッチメニュー定義、作成
    rich_menu_to_create = RichMenu(
        size = RichMenuSize(width=1200, height=405),
        selected = True,
        name = 'richmenu for kakeibo',
        chat_bar_text = 'メインメニュー',
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=600, height=405),
                action=PostbackAction(label="金額登録",data="金額登録")
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=600, y=0, width=600, height=405),
                action=PostbackAction(label="履歴照会",data="履歴照会")
            )
        ]
    )
    richMenuId = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    #画像をupload(未定)

    #リッチメニューをデフォルトに設定
    #line_bot_api.set_default_rich_menu(richMenuId)
    
    return richMenuId


richmenu_id = create_richmenu()

@app.route("/")
def hello_world():
    return "Hello_World!"


@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: "+ body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

#テキストメッセージが来た時のイベント
#おそらく金額の登録時のみ利用
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_id = event.source.user_id
    #userテーブルからセッション番号、現在の登録金額を取得
    session_num = sqlconnector.get_session(user_id=user_id)
    total_money = sqlconnector.get_total_money(user_id=user_id)
    
    
    #セッションが0
    if session_num == 0:
        try:
            money = int(event.message.text)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="入力内容が正しくありません。\n再度入力し直すか、リッチメニューからやり直して下さい。"))
            return

        # ①プラスならそのまま「かしこまりました、現在の所持金はXXX円です」と返す
        if money >= 0:
            
            #家計簿テーブルに登録
            sqlconnector.register_kakeibo(user_id, money,category=None)
            #userテーブルの所持金更新
            sqlconnector.update_total_money(user_id, total_money=total_money+money)

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="承りました。現在の所持金は{}円です。".format(total_money+money)))

            return

        
        # ②マイナスなら用途をクイックリプライで選択してもらい、増減履歴テーブルを更新してセッションを1に更新
        else:
            category_list = ["飲食","娯楽", "洋服", "交通費", "公共料金","その他"]
            items = [QuickReplyButton(action=MessageAction(label=f"{category}", text=f"{category}")) for category in category_list]

            messages = TextSendMessage(text="カテゴリーを選択してください。",
                               quick_reply=QuickReply(items=items))

            #増減履歴テーブルに登録
            sqlconnector.register_money_difference(user_id=user_id, money=money)
            #セッション番号の更新
            sqlconnector.update_session(user_id=user_id, sess_num=1)

            line_bot_api.reply_message(event.reply_token, messages=messages)


            return

    #
    #セッション=1なら、「かしこまりました。現在の所持金はXXX円です」と返し、セッションを0に更新
    elif session_num == 1:

        category = event.message.text
        #増減一時テーブルから増減額を取得
        money_difference = sqlconnector.get_money_difference(user_id)
        
        #現在の所持金を通知
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="承りました。現在の所持金は{}円です。".format(total_money+money_difference)))

        #家計簿テーブルに登録
        sqlconnector.register_kakeibo(user_id, money_difference,category=category)

        #セッション番号、所持金を更新
        sqlconnector.update_total_money(user_id, total_money=total_money+money_difference)
        sqlconnector.update_session(user_id=user_id,sess_num=0)

    #履歴照会用のブロック
    #指定月の履歴を表示し、セッションを0に更新
    elif session_num == 2:
        month = int(event.message.text)

        history_dic = sqlconnector.get_kakeibo_history(month=month, user_id=user_id)
        total_money = sqlconnector.get_total_money(user_id=user_id)

        sqlconnector.update_session(user_id=user_id,sess_num=0)

        message1 = "{}月の履歴\nカテゴリー別\n飲食:{0}円\n娯楽:{1}円\n洋服:{2}円\n交通費:{3}円\n公共料金:{4}円\nその他:{5}円".format(
            history_dic['飲食'],history_dic['娯楽'], history_dic['洋服'], history_dic['交通費'],history_dic['公共料金'], history_dic['その他'])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message1))
        
        message2 = "現在の所持金は{}円です。".format(total_money)
        line_bot_api.push_message(to=user_id, messages=TextSendMessage(text=message2))


        line_bot_api.link_rich_menu_to_user(user_id=user_id, rich_menu_id=richmenu_id)



#ボタンの入力が来た時のイベント、リッチメニューから送信はここで受け取る(予定)
#登録なら金額を記入するように言う
#履歴表示ならテーブルから履歴を取ってきて表示する
@handler.add(PostbackEvent)
def on_postback(event):

    reply_token = event.reply_token
    user_id = event.source.user_id
    postback_msg = event.postback.data

    if postback_msg == "金額登録":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="金額を+1000や-2000のように入力してください。"))
        #リッチメニューを解除
        line_bot_api.unlink_rich_menu_from_user(user_id=user_id)

    elif postback_msg == "履歴照会":

        #何月の履歴を参照したいかをクイックリプライで聞く
        month_list = [i for i in range(1, 13)]
        items = [QuickReplyButton(action=MessageAction(label=f"{month}月", text=f"{month}")) for month in month_list]
        messages = TextSendMessage(text="カテゴリーを選択してください。",
                               quick_reply=QuickReply(items=items))
        
        #セッションを更新(0→2)
        sqlconnector.update_session(user_id=user_id,sess_num=2)

        line_bot_api.reply_message(event.reply_token, messages=messages)
        
        #リッチメニューを解除
        line_bot_api.unlink_rich_menu_from_user(user_id=user_id)
        



#フォローが来た時のイベント
@handler.add(FollowEvent)
def on_follow(event):

    user_id = event.source.user_id
    profiles = line_bot_api.get_profile(user_id=user_id)
    display_name = profiles.display_name

    #ユーザーID、表示名をuserテーブルに登録する

    line_bot_api.reply_message(event.reply_token, 
    messages=TextSendMessage(text="{}さん、\nこちらのアカウントでは家計簿を管理できます。".format(display_name)))

    #リッチメニューをユーザーと紐付ける
    line_bot_api.link_rich_menu_to_user(user_id=user_id, rich_menu_id=richmenu_id)
    



if __name__ == "__main__":
    app.run()
# -*- coding: utf-8 -*-

import os
import psycopg2


#SQLに関するクラス
class SQLConnector:
    def __init__(self):
        #初期操作としてもしデータベースが無ければ、テーブルその他作成はここで行う
        #テスト環境はdockerで立てる
        self.dsn = os.environ("postgresql://localhost:5432/sample_db?user=postgres")
        #テーブル作成
        with self.get_connection as cnn:
            with cnn.cursor() as cur:
                cur.execute()
    
    #接続
    def get_connection(self):
        return psycopg2.connect(self.dsn)

    #↓ここから登録メソッド
    #ユーザー登録(フォローされた際に呼び出す)
    #最初は残金0円にしておく
    def register_user(self, user_id, display_name):
        with self.get_connection as conn:
            with conn.cursor() as cur:
                cur.execute("INCERT INTO user (user_id, display_name, money, session) VALUES ('%s', '%s');" % (user_id, display_name, 0, 0))
    
    #増減履歴テーブルに登録
    def register_money_difference(self, user_id, money):
        with self.get_connection as conn:
            with conn.cursor() as cur:
                cur.execute("INCERT INTO money_history (user_id, money) VALUES ('%s', '%s');" % (user_id, money))

    #家計簿テーブルに登録
    def register_kakeibo(self, user_id, money ,category):
        with self.get_connection() as conn:
            with conn.cursur() as cur:
                cur.excecute("INCERT INTO kakeibo (user_id, money, category) VALUES ('%s', '%s', '%s')" % (user_id, money, category))

        
    #↓ここから取得メソッド
    #1ヶ月の履歴を表示する用にDBに接続
    #カテゴリ毎の合算値+残金を算出
    def get_kakeibo_history(self, month, user_id):
        #指定月のカテゴリ毎の合算値をkakeiboテーブルから引っ張ってくる

        return "カテゴリ毎の合算値を辞書型にまとめる"

    def get_session(self, user_id):
        with self.get_connection() as conn:
            with conn.cursur() as cur:
                cur.excecute("userテーブルのセッションを取得するクエリ")
        
        return 0
    
    def get_total_money(self, user_id):
        with self.get_connection() as conn:
            with conn.cursur() as cur:
                cur.excecute("合計金額を引っ張ってくるクエリ")
        
        return 1000

    def get_money_difference(self, user_id):
        with self.get_connection() as conn:
            with conn.cursur() as cur:
                cur.excecute("増減履歴テーブルから該当userの現セッションでの差額を取得するクエリ")
        
        return 1000
    
    #↓ここから更新メソッド
    #セッション更新する関数
    def update_session(self, user_id, sess_num):
        #指定されたuserのセッションIDを更新する

        with self.get_connection() as conn:
            with conn.cursur() as cur:
                cur.excecute("userテーブルのセッションをsess_numに更新するクエリ")
    
    def update_total_money(self, user_id, total_money):
        with self.get_connection() as conn:
            with conn.cursur() as cur:
                cur.excecute("userテーブルの現在の所持金を更新するクエリ")
    
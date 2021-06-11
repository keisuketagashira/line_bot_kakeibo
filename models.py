import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from setting import Base
from setting import ENGINE

from datetime import datetime

#家計簿テーブル
class Kakeibo(Base):
    __tablename__ = 'kakeibo'
    id = Column('id', Integer, autoincrement=True, primary_key=True)
    user_id = Column('name', String(255), unique=True)
    money_history = Column('money_history',Integer)
    category_id = Column('category_id', Integer)
    register = Column('register_at', DateTime, default=datetime.now, nullable=False)

    #登録
    def __init__(self, user_id, money_history, category_id):
        self.user_id = user_id
        self.money_history = money_history
        self.category_id = category_id
        now = datetime.now()
        self.register = now
        
#ユーザーテーブル
class User(Base):
    __tablename__ = 'user'
    id = Column('id', Integer,autoincrement=True)
    user_id = Column('user_id', String(255), unique=True, primary_key=True)
    display_name = Column('display_name', String(255))
    total_money = Column('total_money', Integer)
    session_num = Column('session_num', Integer)
    register = Column('register_at', DateTime, default=datetime.now, nullable=False)
    modified = Column('modified_at', DateTime, default=datetime.now, nullable=False)

    #登録
    def __init__(self, user_id, display_name):
        self.user_id = user_id
        self.display_name = display_name
        self.total_money = 0
        self.session_num = 0
        now = datetime.now()
        self.register = now
        self.modified = now

#カテゴリーテーブル
class Category(Base):
    __tablename__ = 'category'
    category_id = Column('category_id', Integer)
    category_name = Column('category_name', String(255), primary_key=True)

    #登録
    def __init__(self, category_id, category_name) -> None:
        self.category_id = category_id
        self.category_name = category_name


def create_database(args):
    Base.metadata.create_all(bind=ENGINE)

if __name__ == "__main__":
    create_database(sys.argv)
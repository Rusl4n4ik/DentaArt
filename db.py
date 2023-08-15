from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from main import bot

DATABASE_NAME = 'DentArt.sqlite'

engine = create_engine(f"sqlite:///{DATABASE_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Users(Base):
    __tablename__ = 'Clients'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    first_name = Column(String(100), nullable=True)
    username = Column(String(50), nullable=True)
    name = Column(String(50), nullable=False)
    phnum = Column(String(50), nullable=False)


class Admins(Base):
    __tablename__ = 'Admins'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    first_name = Column(String(100), nullable=True)
    username = Column(String(50), nullable=True)


def send_broadcast(bot, message: str):
    session = Session()
    users = session.query(Users).all()
    for user in users:
        bot.send_message(user.chat_id, message)
    session.close()


def get_all_users():
    users = session.query(Users).all()
    user_list = []
    for user in users:
        user_info = {
            'chat_id': user.chat_id,
            'first_name': user.first_name,
            'username': user.username,
            'name': user.name,
            'phnum': user.phnum
        }
        user_list.append(user_info)
    return user_list


def add_admin(chat_id, first_name, username):
    session = Session()
    exist = session.query(Admins).filter_by(chat_id=chat_id).first()
    if not exist:
        admin = Admins(chat_id=chat_id,
                       first_name=first_name,
                       username=username)
        session.add(admin)
        session.commit()
    session.close()


def remove_admin(chat_id):
    admin = session.query(Admins).filter_by(chat_id=chat_id).first()
    if admin:
        session.delete(admin)
        session.commit()


def get_all_admins():
    admins = session.query(Admins).all()
    return admins


def is_admin(chat_id):
    admins = [1373285788]
    return chat_id in admins


def add_user(id, first_name, username, name, phnum):
    session = Session()
    exist = check_existing(id)
    if not exist:
        user = Users(chat_id=id,
                       first_name=first_name,
                       username=username,
                       name=name,
                       phnum=phnum)
        session.add(user)
        session.commit()
    session.close()


def get_user_info(chat_id):
    session = Session()
    user = session.query(Users).filter_by(chat_id=chat_id).first()
    if user:
        user_info = {
            'name': user.name,
            'phnum': user.phnum
        }
        return user_info
    return None


def update_user(chat_id, name=None, phnum=None):
    session = Session()
    user = session.query(Users).filter_by(chat_id=chat_id).first()
    if user:
        if name is not None:
            user.name = name
        if phnum is not None:
            user.phnum = phnum
        session.commit()
    session.close()


def check_existing(id):
    session = Session()
    result = session.query(Users.chat_id).filter(Users.chat_id == id).all()
    return result


def create_db():
    Base.metadata.create_all(engine)
    session = Session()
    session.commit()


if __name__ == '__main__':
    create_db()
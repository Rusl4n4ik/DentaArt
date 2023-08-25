from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, func, extract, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound


DATABASE_NAME = 'DentArt.sqlite'

engine = create_engine(f"sqlite:///{DATABASE_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

###############################################################
class Users(Base):
    __tablename__ = 'Clients'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    first_name = Column(String(100), nullable=True)
    username = Column(String(50), nullable=True)
    name = Column(String(50), nullable=False)
    phnum = Column(String(50), nullable=False)
    language = Column(String(10))  # Add this column for user's language preference



class Admins(Base):
    __tablename__ = 'Admins'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    first_name = Column(String(100), nullable=True)
    username = Column(String(50), nullable=True)


class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, index=True, unique=True)
    price = Column(String)


class AppointmentStatus(Enum):
    BOOKED = "Booked"
    CANCELED = "Canceled"


class Appointment(Base):
    __tablename__ = "appointment"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    username = Column(String)
    name = Column(String(50), nullable=False)
    number = Column(String(50), nullable=False)
    reason = Column(String(100))
    time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Booked")


class Appointment_Cancel(Base):
    __tablename__ = "canceled"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    username = Column(String)
    name = Column(String(50), nullable=False)
    number = Column(String(50), nullable=False)
    reason = Column(String(100))
    time = Column(DateTime, default=datetime.utcnow)



class Offline(Base):
    __tablename__ = "offline"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    number = Column(String(50), nullable=False)
    reason = Column(String(100))
    time = Column(DateTime, default=datetime.utcnow)


def get_user_info_offline(session: Session):
    offline_record = session.query(Offline).first()
    if offline_record:
        user_info = {
            'name': offline_record.name,
            'phnum': offline_record.number
        }
        return user_info
    return None


def get_appointments_in_time_range(db: Session, start_time: datetime, end_time: datetime):
    return db.query(Appointment).filter(Appointment.time >= start_time, Appointment.time <= end_time).all()


def get_appointments_on_day(db: Session, year: int, month: int, day: int):
    return db.query(Appointment).filter(
        extract('year', Appointment.time) == year,
        extract('month', Appointment.time) == month,
        extract('day', Appointment.time) == day
    ).all()


def get_user_language(session, id: int):
    user = session.query(Users).filter(Users.chat_id == id).first()
    if user:
        return user.language


def update_user_language(session, chat_id: int, new_language: str):
    user = session.query(Users).filter(Users.chat_id == chat_id).first()
    if user:
        user.language = new_language
        session.commit()



def get_available_hours(appointments_on_day):
    all_hours = set([f"{hour:02d}:{minute:02d}" for hour in range(8, 19) for minute in (0, 30) if not (hour == 18 and minute > 0)])
    booked_hours = set([appointment.time.strftime("%H:%M") for appointment in appointments_on_day])
    available_hours = all_hours - booked_hours
    return available_hours

################################################################################3


def send_broadcast(bot, message: str):
    session = Session()
    users = session.query(Users).all()
    for user in users:
        bot.send_message(user.chat_id, message)
    session.close()


def get_users_with_appointments(session: Session):
    users_with_appointments = (
        session.query(Users)
            .filter(Users.chat_id.in_(session.query(Appointment.chat_id)))
            .all()
    )
    return users_with_appointments


def get_user_appointments(session: Session, chat_id: int):
    user = session.query(Users).filter_by(chat_id=chat_id).first()
    if user:
        return user.appointments
    return []



#########################################################################################


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
##########################################################


def add_user(id, first_name, username, name, phnum, language='ru'):
    session = Session()
    exist = check_existing(id)
    if not exist:
        user = Users(chat_id=id,
                     first_name=first_name,
                     username=username,
                     name=name,
                     phnum=phnum,
                     language=language)  # Set the language for the user
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
########################################################################################


def get_all_prices(session: Session):
    return session.query(Price).all()


def add_price_and_service(service: str, price: str):
    session = Session()
    new_price = Price(service=service, price=price)
    session.add(new_price)
    session.commit()
    session.close()


def get_price_by_index(session: Session, index):
    return session.query(Price).filter_by(id=index + 1).first()


def get_price(session: Session, service):
    return session.query(Price).filter_by(service=service).first()


def update_service_price(session: Session, service, new_price):
    price = get_price(session, service)
    if price:
        price.price = new_price
        session.commit()
        print(f"Цена для {service} обновлена на {new_price}")
        return True
    else:
        print(f"Сервис {service} не найден")
        return False


def update_service_name(session: Session, index, new_name):
    try:
        price = session.query(Price).filter_by(id=index + 1).first()
        if price:
            price.service = new_name
            session.commit()
    except Exception as e:
        session.rollback()
        raise e


# def get_users_with_appointments(session: Session):
#     users_with_appointments = session.query(Users).filter(Users.appointments.any()).all()
#     return users_with_appointments

#######################################################################################


def create_appointment(chat_id, username, name, number, reason, time):
    with Session() as session:
        appointment = Appointment(chat_id=chat_id, username=username, name=name, number=number, reason=reason, time=time)
        session.add(appointment)
        session.commit()


def create_appointment_offline(name, number, reason, time):
    session = Session()  # Создаем экземпляр сессии
    try:
        appointment = Offline(name=name, number=number, reason=reason, time=time)
        session.add(appointment)
        session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        # Обработка ошибки, если необходимо
    finally:
        session.close()


def get_appointments_view(session: Session, chat_id: int):
    return session.query(Appointment).filter_by(chat_id=chat_id, status="Booked").all()


def get_appointment_info(session: Session, year: int, month: int, day: int, hour: str):
    appointment = session.query(Appointment).filter(Appointment.time).first()

    if appointment:
        appointment_info = {
            'reason': appointment.reason,
        }
        return appointment_info
    else:
        return None


def get_appointments(session: Session, chat_id: int, view_mode: str):
    if view_mode == "booked":
        return session.query(Appointment).filter_by(chat_id=chat_id, status="Booked").all()
    elif view_mode == "canceled":
        return session.query(Appointment).filter_by(chat_id=chat_id, status="Canceled").all()
    else:
        raise ValueError("Invalid view mode")


def get_appointment_by_datetime(session, year, month, day, time):
    appointment = session.query(Appointment).filter_by(year=year, month=month, day=day, time=time).first()
    return appointment



def get_all_appointments(session: Session):
    return session.query(Appointment).filter(Appointment.status == "Booked").all()


def get_all_offline_appointments(session: Session):
    return session.query(Offline).all()


def delete_appointment(session: Session, appointment_id: int):
    appointment = session.query(Appointment).get(appointment_id)
    if appointment:
        appointment.status = "Canceled"
        session.commit()
        return True
    return False


########################################################################################
def create_db():
    Base.metadata.create_all(engine)
    session = Session()
    session.commit()


if __name__ == '__main__':
    create_db()
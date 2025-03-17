from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import datetime

# Создаем базовый класс для моделей
Base = declarative_base()


# Определяем модели данных
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    level = Column(String(10))
    source = Column(String(255))
    message = Column(Text)

    def __repr__(self):
        return f"<Log(id={self.id}, timestamp={self.timestamp}, level={self.level})>"


class TerminatedProcess(Base):
    __tablename__ = "terminated_processes"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    process_name = Column(String(255))
    pid = Column(String(50))
    memory_usage = Column(Float)
    cpu_usage = Column(Float)
    status = Column(String(50))
    terminated_by = Column(String(255))  # Имя пользователя или системы

    def __repr__(self):
        return f"<TerminatedProcess(id={self.id}, process_name={self.process_name}, pid={self.pid})>"


# Функция для инициализации базы данных
def init_db():
    # Создаем директорию для базы данных, если её нет
    db_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database"
    )
    os.makedirs(db_dir, exist_ok=True)

    # Путь к файлу базы данных
    db_path = os.path.join(db_dir, "system_monitor.db")

    # Создаем движок SQLAlchemy
    engine = create_engine(f"sqlite:///{db_path}")

    # Создаем таблицы
    Base.metadata.create_all(engine)

    # Создаем фабрику сессий
    Session = sessionmaker(bind=engine)

    return engine, Session

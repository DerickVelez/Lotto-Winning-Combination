from sqlalchemy import create_engine, Integer, DECIMAL,Date, String, UUID , Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import PrimaryKeyConstraint, UniqueConstraint
import uuid

engine = create_engine('postgresql+psycopg2://postgres:Workeye29@localhost/PCSO_LOTTODB', echo=True)

Base = declarative_base()

class LottoTable(Base):
    __tablename__= 'lotto_table'
    id = Column(UUID(as_uuid=True),  default=uuid.uuid4 , primary_key=True)
    game = Column(String)
    jackpot_amount = Column(DECIMAL,nullable=False)
    draw_date = Column(Date)
    number_of_winners = Column(Integer,  nullable = True)
    
    __table_args__ = (
        UniqueConstraint(game, draw_date, name = "unique_draw_date"),
        {})

class WinningNumbers(Base):
    __tablename__= 'winning_numbers'
    lotto_id = Column(UUID ,ForeignKey('lotto_table.id'))
    draw_number = Column(Integer)
    
    __table_args__ = (
        PrimaryKeyConstraint(lotto_id,draw_number),
        {})

class RawDrawResults(Base):
    __tablename__='raw_draw_result'
    id = Column(UUID(as_uuid=True),  default=uuid.uuid4 , primary_key=True)
    raw_lotto_game = Column(String)
    raw_combinations = Column(String)
    raw_draw_date = Column(Date)
    raw_jackpot = Column(DECIMAL)
    raw_winners = Column(Integer)
    
    __table_args__ = (
        UniqueConstraint(raw_lotto_game,raw_draw_date),
        {})


class UploadRecordTable(Base):
    __tablename__='upload_record_table'
    upload_date = Column(String, primary_key=True)
    
        
    
Base.metadata.create_all(engine)



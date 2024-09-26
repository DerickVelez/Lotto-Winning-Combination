
from sqlalchemy import create_engine, Integer, DECIMAL,Date, String, UUID , Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint, UniqueConstraint
import uuid

engine = create_engine('postgresql+psycopg2://postgres:Workeye29@localhost/PCSO_LOTTODB', echo=True)

Base = declarative_base()

class DrawResults(Base):
    __tablename__='draw_results'
    id = Column(UUID(as_uuid=True),  default=uuid.uuid4 , primary_key=True)
    raw_lotto_game = Column(String)
    raw_draw_date = Column(Date)
    raw_jackpot = Column(DECIMAL)
    raw_winners = Column(Integer)
    
    __table_args__ = (
        UniqueConstraint(raw_lotto_game,raw_draw_date),
        {})


class WinningCombinations(Base):
    __tablename__='winning_combination'
    id = Column(UUID(as_uuid=True),  default=uuid.uuid4 , primary_key=True)
    lotto_id = Column(UUID(as_uuid=True) ,ForeignKey('draw_results.id'))
    draw_number = Column(Integer)
        
    
Base.metadata.create_all(engine)



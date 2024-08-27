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
    winning_numbers = Column(Integer)
    
    __table_args__ = (
        PrimaryKeyConstraint(lotto_id,winning_numbers),
        {})
    
Base.metadata.create_all(engine)



# Session = sessionmaker(bind=engine)

# with Session(engine) as session:

# new_result = LottoTable(game = 'dsf',jackpot_amount = 342523,draw_date = '01-03-',number_of_winners = result[3], winning_numbers = result[4])
# session.add(new_result)
# session.commit()
   
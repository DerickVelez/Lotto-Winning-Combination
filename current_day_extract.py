from bs4 import BeautifulSoup
import requests

from datetime import datetime
import os
import decimal

from pathlib import Path

from sqlalchemy.orm import Session
from lotto_project.models.databasemanager import DrawResults, WinningCombinations, engine

file_name = rf"D:\development\python\PCSO_LOTTO_NUMBERS\data\html\pcso_{datetime.strftime(datetime.now(),'%Y%m%d')}.html"
if not os.path.exists(file_name):
 
    url = "https://www.pcso.gov.ph"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }#fake agent
    
    response = requests.get(url, headers=headers)
    f = open(file_name, 'w', encoding='utf-8')
    f.write(response.text)
    f.close()
    
data = Path(file_name).read_text()

soup = BeautifulSoup(data, 'html.parser')
results = soup.find_all('div', class_='draw-game') 



lotto_results = [] 
for result in results:
    numbers = result.find_all_next('span', class_='draw-number',limit = 6)
    game_type = result.find_next('span', class_='draw-number')['id'].split("_")[-1].replace("1","")
    jackpot_amount = result.find_next('span', class_='jackpot-amount').text
    number_of_winners = result.find_next('span', class_='jackpot-winner').text
    draw_date = result.find_next('span', class_='jackpot-date').text
    print(game_type)
    winning_numbers = []
    for number in numbers:
        winning_numbers.append(int(number.text))
    
    
    # formatted
    amount = decimal.Decimal(jackpot_amount[1:].replace(",",""))
    winners = int(number_of_winners.replace(" Jackpot Winner/s",""))
    date = datetime.strptime(draw_date, '%B %d, %Y').date()

        
    with Session(engine) as session:
        lotto_result = DrawResults(raw_lotto_game=game_type, raw_jackpot=amount, raw_draw_date=date, raw_winners=winners)
        existing_result = session.query(DrawResults).filter_by(raw_lotto_game=lotto_result.raw_lotto_game,
                                                                raw_draw_date=lotto_result.raw_draw_date).one_or_none()
        if existing_result is None:
            session.add(lotto_result)
            session.flush()
            session.refresh(lotto_result)
            for number in numbers:
                winning_number = WinningCombinations(lotto_id= lotto_result.id, draw_number=int(number.text))
                session.add(winning_number)
        session.commit()
        
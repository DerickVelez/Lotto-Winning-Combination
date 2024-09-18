import requests
import os.path

from bs4 import BeautifulSoup
from datetime import datetime
import decimal


file_name = rf"D:\development\python\PCSO_LOTTO_NUMBERS\html\pcso_{datetime.strftime(datetime.now(),'%Y%m%d')}.html"
if not os.path.exists(file_name):
    
    headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
    url = 'https://www.pcso.gov.ph/'
    r = requests.get(url, headers = headers)

    f = open(file_name, "w", encoding ='utf-8')
    f.write(r.text)
    f.close()

html =  open(file_name, "r")
index = html.read()

soup = BeautifulSoup(index, 'html.parser')
results = soup.find_all('div', class_='draw-game')
lotto_result= []

for result in results:
    numbers = result.find_all_next('span', class_='draw-number').text
    draw_amount = result.find_next('span', class_='jackpot-amount').text
    draw_winner = result.find_next('span', class_='jackpot-winner').text.replace(" Jackpot Winner/s","")
    draw_date = result.find_next('span', class_='jackpot-date').text
    game_type = result.find_next('span', class_='draw-number')['id'].split("_")[-1].replace("1","")
    
    
    new_date = datetime.strptime(draw_date, "%B %d, %Y").date()
    new_amount = decimal.Decimal(draw_amount[1:].replace(",",""))
    lotto_result.append(numbers)

print(lotto_result)
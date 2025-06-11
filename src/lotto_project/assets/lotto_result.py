from dagster import AssetExecutionContext, asset

import requests
import os
import decimal
import calendar

from bs4 import BeautifulSoup
from pathlib import Path
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session
from src.lotto_project.models.databasemanager import DrawResults, WinningCombinations, engine

@asset(
  deps=["table_initialization"]
)
def get_current_lotto_result(context: AssetExecutionContext):
    try:
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
                context.log.info('Successfully inserted data to wrist band')
                
    except Exception as e:
        context.log.exception("An error occurred during asset execution")
        raise
        
@asset(
  deps=["table_initialization"]
)
def get_monthly_lotto_result(context: AssetExecutionContext):
    
    today = datetime.today()
    prev_month_date = today - relativedelta(months=1)
    date_from = prev_month_date.replace(day=1)
    last_day = calendar.monthrange(prev_month_date.year, prev_month_date.month)[1]
    date_to = prev_month_date.replace(day=last_day)

    month_from = date_from.strftime("%B")
    year_from = date_from.strftime("%Y")
    day_from = date_from.strftime("%#d")

    month_to = date_to.strftime("%B")
    year_to = date_to.strftime("%Y")
    day_to = date_to.strftime("%#d")

    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # page = context.new_page()
        
        page.goto("https://www.pcso.gov.ph/SearchLottoResult.aspx")
        
        page.wait_for_selector("id=cphContainer_cpContent_ddlStartMonth").select_option(value=month_from)
        page.wait_for_selector("id=cphContainer_cpContent_ddlStartDate").select_option(value=day_from)
        page.wait_for_selector("id=cphContainer_cpContent_ddlStartYear").select_option(value=year_from)

        page.wait_for_selector("id=cphContainer_cpContent_ddlEndMonth").select_option(value=month_to)
        page.wait_for_selector("id=cphContainer_cpContent_ddlEndDay").select_option(value=day_to)
        page.wait_for_selector("id=cphContainer_cpContent_ddlEndYear").select_option(value=year_to)

        page.get_by_role("button", name="Search Lotto").click()
        page.screenshot(path="screenshot.png")
        
        table = []
        table_rows = page.locator("table > tbody > tr")
        print(table_rows.count())

        for row_index in range(1,table_rows.count()):
            row = table_rows.nth(row_index)
            columns = row.locator("td")
            
            row_data = [columns.nth(col_index).text_content() for col_index in range(columns.count())]
            table.append(row_data)
            # print(table)
        page.wait_for_timeout(2000)
        browser.close() 
    
    with Session(engine) as session:
        for sublist in table:
            game, combinations, draw_date, jackpot, winners = sublist
            formatted_combination = combinations.split('-')
              
            existing_result = session.query(DrawResults).filter(
                DrawResults.raw_lotto_game == game,
                DrawResults.raw_draw_date == datetime.strptime(draw_date, '%m/%d/%Y')
            ).first()

            if existing_result:
                print(f"Duplicate entry found for {game} on {draw_date}. Skipping insertion.")
                continue

            # Create a new DrawResults entry
            lotto_result = DrawResults(
                raw_lotto_game=game,
                raw_draw_date=datetime.strptime(draw_date, '%m/%d/%Y'),
                raw_jackpot=decimal.Decimal(jackpot.replace(',', '')),
                raw_winners=int(winners)
            )
            session.add(lotto_result)
            session.flush()  

            for number in formatted_combination:
                winning_result = WinningCombinations(
                    lotto_id=lotto_result.id,
                    draw_number=int(number.rstrip())
                )
                session.add(winning_result)

        session.commit()
    
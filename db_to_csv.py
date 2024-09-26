import csv
import uuid
from sqlalchemy.orm import Session
from datetime import date
from databasemanager import engine
from sqlalchemy import text


def db_to_csv(date_from: date, date_to: date): 

    with Session(engine) as session:
        
        
        query = text(f"""SELECT * FROM draw_results WHERE raw_draw_date BETWEEN '{date_from}' AND '{date_to}'""") 
        
        result = session.execute(query)
            
        file_path = rf'D:\development\python\PCSO_LOTTO_NUMBERS\csv\{str(uuid.uuid4())}.csv'


        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            writer.writerow(result.keys())

            for row in result:
                writer.writerow(row)
        print('finished')



db_to_csv(date_from=date(2024, 3, 1), date_to=date(2024, 3, 31))


import pandas as pd
import uuid
from datetime import date
from databasemanager import engine
from sqlalchemy import text
from playwright.sync_api import sync_playwright



def db_to_pdf(date_from: date, date_to: date): 
    
    query = text(f"""SELECT * FROM draw_results WHERE raw_draw_date BETWEEN '{date_from}' AND '{date_to}'""") 
    
    with engine.connect() as conn:
        
        
        data =pd.read_sql(query, conn)
        df = pd.DataFrame(data)
        html_file = str(uuid.uuid4())+'.html'
        df.to_html(html_file,float_format='{:,.2f}'.format)

        
        with sync_playwright() as p:
                 
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()            
            
            with open(html_file, 'r', encoding= 'utf-8',) as file:
                html_content = file.read()
                
            page.set_content(html_content)
        
            page.pdf(path= rf'D:\development\python\PCSO_LOTTO_NUMBERS\{str(uuid.uuid4())}.pdf' )
        

 
db_to_pdf(date_from=date(2024, 3, 1), date_to=date(2024, 3, 31))

    


    



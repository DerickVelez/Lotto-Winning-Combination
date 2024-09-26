from datetime import datetime 
from extract_previous import get_result_by_date ,upload_to_db
from datetime import datetime
from dateutil.relativedelta import relativedelta

start_date = datetime(2014, 1, 1)
end_date = datetime(2014, 5, 31)

current_date = start_date

while current_date <= end_date:

    month_start_date = start_date
    current_date += relativedelta(months=1)
    month_end_date = current_date - relativedelta(days=1) 
    
    
    if month_end_date > current_date:
        print(start_date.strftime("%Y-%m-%d"))    
        print(month_end_date.strftime("%Y-%m-%d"))
        table = get_result_by_date(start_date,month_end_date)
        upload_to_db(table= table)
        
    else:
        print(current_date.strftime("%Y-%m-%d"))
        print(month_end_date.strftime("%Y-%m-%d"))
        table = get_result_by_date(current_date - relativedelta(months=1),month_end_date)
        upload_to_db(table= table)
        
    
    
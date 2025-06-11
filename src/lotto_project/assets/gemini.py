from dagster import AssetExecutionContext, asset

import requests
import os
import decimal
import calendar
import logging

from bs4 import BeautifulSoup
from pathlib import Path
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session
from src.lotto_project.models.databasemanager import DrawResults, WinningCombinations, engine
from sqlalchemy.exc import SQLAlchemyError
       
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
        
@asset(

)
def get_monthly_lotto_result_gemini(context: AssetExecutionContext):
    """
        Dagster asset to scrape monthly lotto results from PCSO website and store them in a database.
        Includes comprehensive error handling and logging.
        """
    logger.info("Starting get_monthly_lotto_result asset execution.")
        
    # Calculate the date range for the previous month
    today = datetime.today()
    prev_month_date = today - relativedelta(months=1)
    date_from = prev_month_date.replace(day=1) # First day of previous month
    last_day = calendar.monthrange(prev_month_date.year, prev_month_date.month)[1]
    date_to = prev_month_date.replace(day=last_day) # Last day of previous month

    # Format dates for Playwright's dropdown selection
    month_from = date_from.strftime("%B")
    year_from = date_from.strftime("%Y")
    # Use %#d for Windows (no leading zero) and %-d for Linux (no leading zero).
    # Since Docker typically runs Linux, %-d is safer, but %#d often works cross-platform for simple digits.
    # For robust cross-platform date formatting, consider explicit handling or a different approach if issues arise.
    day_from = date_from.strftime("%#d") 

    month_to = date_to.strftime("%B")
    year_to = date_to.strftime("%Y")
    day_to = date_to.strftime("%#d")

    browser = None # Initialize browser to None for proper cleanup in finally block
    table_data = [] # Initialize table_data to ensure it's always defined

    try:
        # --- Playwright Automation Section ---
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) # Launch browser in headless mode
            page = browser.new_page() # Create a new page

            page.goto("https://www.pcso.gov.ph/SearchLottoResult.aspx")
            logger.info("Navigated to PCSO Search Lotto Result page.")
            
            # Select the start date in the form
            logger.info(f"Selecting start date: {month_from} {day_from}, {year_from}")
            page.wait_for_selector("id=cphContainer_cpContent_ddlStartMonth").select_option(value=month_from)
            page.wait_for_selector("id=cphContainer_cpContent_ddlStartDate").select_option(value=day_from)
            page.wait_for_selector("id=cphContainer_cpContent_ddlStartYear").select_option(value=year_from)

            # Select the end date in the form
            logger.info(f"Selecting end date: {month_to} {day_to}, {year_to}")
            page.wait_for_selector("id=cphContainer_cpContent_ddlEndMonth").select_option(value=month_to)
            page.wait_for_selector("id=cphContainer_cpContent_ddlEndDay").select_option(value=day_to)
            page.wait_for_selector("id=cphContainer_cpContent_ddlEndYear").select_option(value=year_to)

            # Click the search button to submit the form
            page.get_by_role("button", name="Search Lotto").click()
            logger.info("Clicked 'Search Lotto' button. Waiting for results to load.")
            
            # Wait for the network to be idle, indicating that results are likely loaded.
            # For more robustness, consider waiting for a specific element on the results table.
            page.wait_for_load_state('networkidle') 
            
            # Take a screenshot for debugging purposes (useful if `headless=True`)
            page.screenshot(path="screenshot_after_search.png")
            logger.info("Screenshot 'screenshot_after_search.png' taken.")
            
            # Extract data from the results table
            try:
                # Target the specific table containing the lotto results. Adjust selector if necessary.
                # Common pattern: `table#someId tbody > tr` or `div#someId table tbody > tr`
                table_rows = page.locator("table > tbody > tr") # This is a general selector; make it more specific if possible.
                row_count = table_rows.count()
                logger.info(f"Found {row_count} table rows in the results.")

                if row_count == 0:
                    logger.warning("No results found for the specified date range. The results table appears empty.")
                else:
                    # Iterate through table rows, skipping the header row (assuming it's the first `tr`)
                    for row_index in range(1, row_count):
                        row = table_rows.nth(row_index)
                        columns = row.locator("td")
                        
                        # Extract text content from each column, stripping whitespace
                        row_data = [columns.nth(col_index).text_content().strip() for col_index in range(columns.count())]
                        table_data.append(row_data)
                        logger.debug(f"Extracted row: {row_data}")
            except Exception as e:
                logger.error(f"Error extracting data from the Playwright table: {e}", exc_info=True)
                # If extraction fails, table_data might be incomplete or empty, but we'll proceed
                # to allow the database section to handle empty data gracefully.

    except Exception as e:
        logger.error(f"An unexpected error occurred during Playwright operations: {e}", exc_info=True)
        # If Playwright fails catastrophically, exit the asset.
        return 
    finally:
        # Ensure the browser is closed even if errors occur
        if browser:
            logger.info("Closing browser.")
            browser.close()

    if not table_data:
        logger.info("No data was successfully extracted from the website. Skipping database insertion.")
        return # Exit if no data was scraped

    # --- Database Insertion Section ---
    try:
        with Session(engine) as session:
            logger.info(f"Attempting to insert {len(table_data)} rows into the database.")
            for sublist in table_data:
                # Validate row length to prevent IndexError
                if len(sublist) != 5:
                    logger.warning(f"Skipping malformed row: {sublist}. Expected 5 elements (game, combinations, date, jackpot, winners), but got {len(sublist)}.")
                    continue

                game, combinations_str, draw_date_str, jackpot_str, winners_str = sublist
                
                # Data cleaning and type conversion with robust error handling for each field
                try:
                    formatted_combination = combinations_str.split('-')
                    # Convert to date object for better database storage
                    draw_date = datetime.strptime(draw_date_str, '%m/%d/%Y').date() 
                    # Clean and convert jackpot string to Decimal
                    jackpot = decimal.Decimal(jackpot_str.replace(',', '').replace('Php', '').strip())
                    # Convert winners string to integer
                    winners = int(winners_str)
                except ValueError as ve:
                    logger.warning(f"Data conversion error for row '{sublist}': {ve}. Skipping this row.", exc_info=True)
                    continue # Skip to the next row if conversion fails
                except Exception as e:
                    logger.error(f"Unexpected data parsing error for row '{sublist}': {e}. Skipping this row.", exc_info=True)
                    continue # Skip to the next row for any other parsing errors

                try:
                    # Check for duplicate entries before inserting
                    existing_result = session.query(DrawResults).filter(
                        DrawResults.raw_lotto_game == game,
                        DrawResults.raw_draw_date == draw_date
                    ).first()

                    if existing_result:
                        logger.info(f"Duplicate entry found for game '{game}' on '{draw_date}'. Skipping insertion.")
                        continue # Skip to the next row if a duplicate exists

                    # Create a new DrawResults entry
                    lotto_result = DrawResults(
                        raw_lotto_game=game,
                        raw_draw_date=draw_date,
                        raw_jackpot=jackpot,
                        raw_winners=winners
                    )
                    session.add(lotto_result)
                    session.flush()  # Flush to get the `id` for the new `lotto_result` before adding combinations

                    # Add winning combinations linked to the new draw result
                    for number_str in formatted_combination:
                        try:
                            # Clean and convert each combination number to integer
                            winning_result = WinningCombinations(
                                lotto_id=lotto_result.id,
                                draw_number=int(number_str.strip()) 
                            )
                            session.add(winning_result)
                        except ValueError as ve_num:
                            logger.warning(f"Invalid winning combination number '{number_str}' for game '{game}' on '{draw_date_str}': {ve_num}. Skipping this number.", exc_info=True)
                            # Continue to the next number, don't stop the whole row insertion
                        except Exception as e_num:
                            logger.error(f"Error adding winning combination '{number_str}' for game '{game}' on '{draw_date_str}': {e_num}", exc_info=True)
                            # Continue to the next number

                except SQLAlchemyError as sa_e:
                    session.rollback() # Rollback the session on any SQLAlchemy error to prevent partial commits
                    logger.error(f"Database error during processing row '{sublist}': {sa_e}", exc_info=True)
                except Exception as e:
                    session.rollback() # Rollback for any other unexpected errors during loop iteration
                    logger.error(f"Unexpected error processing row '{sublist}': {e}", exc_info=True)
                    
            session.commit() # Commit all changes to the database at the end of the session block
            logger.info("Successfully committed all new lotto results and combinations to the database.")

    except SQLAlchemyError as e:
        # Catch critical SQLAlchemy errors outside the loop (e.g., connection issues)
        logger.critical(f"A critical SQLAlchemy error occurred during the overall database session: {e}", exc_info=True)
        # Depending on criticality, you might want to re-raise or trigger alerts here.
    except Exception as e:
        # Catch any other unexpected critical errors during database operations
        logger.critical(f"An unexpected critical error occurred during overall database operations: {e}", exc_info=True)
        # Consider re-raising or notification for critical errors.

    logger.info("Finished get_monthly_lotto_result asset execution.")


from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime
import requests
import praw
import time

def get_activity_data(subreddit):
    reddit = praw.Reddit(client_id='?', client_secret='?', user_agent='?')
    
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    subreddit = reddit.subreddit(subreddit)
    post_count = 0
    comment_count = 0
    for submission in subreddit.new(limit=None):
        if submission.created_utc > yesterday.timestamp():
            post_count += 1
            comment_count += submission.num_comments

    activity_score = post_count * 32 + comment_count
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    worksheet = client.open('Stock and Subreddit Data').worksheet('Subreddit Data')  


    data = [yesterday.strftime('%m/%d/%y'), subreddit.display_name, post_count, comment_count, activity_score]
    worksheet.append_row(data)

def get_stock_data(symbol):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('Stock and Subreddit Data').worksheet('Stock Data')
    
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    date = yesterday.strftime('%Y-%m-%d')

    api_key = '?'

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&datatype=json"

    response = requests.get(url).json()
    if date in response['Time Series (Daily)']:
        close_price = response['Time Series (Daily)'][date]['4. close']
        data = [yesterday.strftime('%m/%d/%y'), symbol, close_price]
        sheet.append_row(data)  

def main(request=None):
    subreddits = ["apple", "google", "teslamotors", "worldnews", "peoplefuckingdying", "netflix", "witchesvspatriarchy", "manga", "watchpeopledieinside", "sports"]
    symbols = ["AAPL", "GOOGL", "TSLA", "VOO", "PAWZ", "NFLX", "XOM", "SONY", "GME", "DKNG"]
    symbol_counter = 0

    # Federal Holidays in which the stock market is closed..
    skip_dates = ['2023-01-02', '2023-01-16', '2023-02-20', '2023-04-07', '2023-05-29', '2023-06-19', '2023-07-04', '2023-09-04', '2023-11-23', '2023-12-25', '2024-01-01', '2024-01-15', '2024-02-19', '2024-03-29', '2024-05-27', '2024-06-19', '2024-07-04', '2024-09-02', '2024-11-28', '2024-12-25', '2025-01-01', '2025-01-20', '2025-02-17', '2025-04-18', '2025-05-26', '2025-06-19', '2025-07-04', '2025-09-01', '2025-11-27', '2025-12-25'] 

    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
  
    if date_str in skip_dates:
        return ('Data collection skipped for this date.', 200)
  
    for i, symbol in enumerate(symbols):
        get_stock_data(symbol)
        print(f"Stock data for {symbol} collected.")
        symbol_counter += 1
        if symbol_counter == 4:
            time.sleep(60)
            symbol_counter = 0

    for i, subreddit in enumerate(subreddits):
        get_activity_data(subreddit)
        print(f"Subreddit data for {subreddit} collected.")

    return ('Data collection completed successfully.', 200)
import pandas as pd
import yfinance as yf
import numpy as np
import requests
import base64
import json
from datetime import datetime
import io
import os
import time

GITHUB_TOKEN = os.getenv("TOKEN_GITHUB")
REPO_OWNER = "sohamdeshpande"
REPO_NAME = "nifty-analysis"
CSV_FILE_PATH = "data/ADANIENT.NS.csv"
STOCK_NAME = ['ADANIENT.NS',
 'ADANIPORTS.NS',
 'APOLLOHOSP.NS',
 'ASIANPAINT.NS',
 'AXISBANK.NS',
 'BAJAJ-AUTO.NS',
 'BAJFINANCE.NS',
 'BAJAJFINSV.NS',
 'BEL.NS',
 'BPCL.NS',
 'BHARTIARTL.NS',
 'BRITANNIA.NS',
 'CIPLA.NS',
 'COALINDIA.NS',
 'DRREDDY.NS',
 'EICHERMOT.NS',
 'GRASIM.NS',
 'HCLTECH.NS',
 'HDFCBANK.NS',
 'HDFCLIFE.NS',
 'HEROMOTOCO.NS',
 'HINDALCO.NS',
 'HINDUNILVR.NS',
 'ICICIBANK.NS',
 'ITC.NS',
 'INDUSINDBK.NS',
 'INFY.NS',
 'JSWSTEEL.NS',
 'KOTAKBANK.NS',
 'LT.NS',
 'M&M.NS',
 'MARUTI.NS',
 'NTPC.NS',
 'NESTLEIND.NS',
 'ONGC.NS',
 'POWERGRID.NS',
 'RELIANCE.NS',
 'SBILIFE.NS',
 'SHRIRAMFIN.NS',
 'SBIN.NS',
 'SUNPHARMA.NS',
 'TCS.NS',
 'TATACONSUM.NS',
 'TATAMOTORS.NS',
 'TATASTEEL.NS',
 'TECHM.NS',
 'TITAN.NS',
 'TRENT.NS',
 'ULTRACEMCO.NS',
 'WIPRO.NS']

DATA_DIR = "data"  # Consistent definition of the data directory

def get_existing_csv(stock_name):
    """
    Gets the existing CSV data from the local file system.

    Args:
        stock_name (str): The name of the stock (e.g., 'ADANIENT.NS').

    Returns:
        pandas.DataFrame: The existing CSV data, or None on error.
    """
    csv_file_path = os.path.join(DATA_DIR, f"{stock_name}.csv")
    try:
        df = pd.read_csv(csv_file_path, index_col=0, parse_dates=True)
        return df, None  # Return None for SHA as we're reading locally
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}")
        return None, None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None, None

# def get_existing_csv(STOCK_NAME):
#     # Get the existing CSV from GitHub
#     CSV_FILE_PATH = f'''data/{STOCK_NAME}.csv'''
#     url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{CSV_FILE_PATH}"
#     print(f'''this is url {url}''')
#     headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         content = response.json()["content"]
#         decoded_content = base64.b64decode(content).decode('utf-8')
#         df = pd.read_csv(io.StringIO(decoded_content), index_col=0, parse_dates=True)
#         sha = response.json()["sha"]  # Required for updating the file
#         return df, sha
#     else:
#         print("Error fetching CSV:", response.status_code)
#         return None, None
    
def get_last_day_data(STOCK_NAME):
    # Fetch latest data for the last day
    time.sleep(15)
    stock_data = yf.download(STOCK_NAME, period="2d", interval="1d")
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.droplevel(1)
    stock_data.columns.name = None
    return stock_data.tail(1)

def update_indicators(df, STOCK_NAME):
    # Calculate the 20-day moving average
    df['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
    # Calculate the 200-day moving average
    df['SMA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
    df['Golden Cross'] = (df['SMA_20'].shift(1) < df['SMA_200'].shift(1)) & (df['SMA_20'] >= df['SMA_200'])
    df['Trend'] = (df['SMA_20'] > df['SMA_200'])  
    df['Trend']=df['Trend'].map({True:'POSITIVE', False:'NEGATIVE'})
    df['stock'] = STOCK_NAME
    return df

def get_existing_csv(stock_name):
    """
    Gets the existing CSV data from the local file system.

    Args:
        stock_name (str): The name of the stock (e.g., 'ADANIENT.NS').

    Returns:
        pandas.DataFrame: The existing CSV data, or None on error.
    """
    csv_file_path = os.path.join(DATA_DIR, f"{stock_name}.csv")
    try:
        df = pd.read_csv(csv_file_path, index_col=0, parse_dates=True)
        return df, None  # Return None for SHA as we're reading locally
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}")
        return None, None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None, None
    
def update_csv_on_github(df, stock_name):
    """
    Updates the CSV file on GitHub.

    Args:
        df (pandas.DataFrame): The DataFrame to save to CSV.
        stock_name (str): The name of the stock.
    """
    csv_file_path = os.path.join(DATA_DIR, f"{stock_name}.csv")
    try:
        # Save the dataframe locally.
        df.to_csv(csv_file_path)
        print(f"✅ CSV updated successfully locally at {csv_file_path}!")

    except Exception as e:
        print(f"❌ Error updating CSV: {e}")
        
# def update_csv_on_github(df, sha, STOCK_NAME):
#     # Convert DataFrame to CSV string
#     csv_content = df.to_csv()
#     encoded_content = base64.b64encode(csv_content.encode()).decode()

#     # Create commit data
#     commit_data = {
#         "message": f"Updated CSV with latest data on {datetime.today().strftime('%Y-%m-%d')}",
#         "content": encoded_content,
#         "sha": sha,
#         "branch": "main"
#     }

#     # Upload updated CSV to GitHub
#     CSV_FILE_PATH = f'''data/{STOCK_NAME}.csv'''
#     url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{CSV_FILE_PATH}"
#     headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
#     response = requests.put(url, headers=headers, data=json.dumps(commit_data))

#     if response.status_code == 200:
#         print("✅ CSV updated successfully on GitHub!")
#     else:
#         print("❌ Error updating CSV:", response.status_code, response.json())

def main():
    for STOCK in STOCK_NAME:
        df, sha = get_existing_csv(STOCK)
        if df is not None:
            time.sleep(1)
            new_data = get_last_day_data(STOCK)
            df = pd.concat([df, new_data]).drop_duplicates()
            df = update_indicators(df,STOCK)
            update_csv_on_github(df, STOCK)

if __name__ == "__main__":
    main()

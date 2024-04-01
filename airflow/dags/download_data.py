from bs4 import BeautifulSoup
import pandas as pd
import requests
import yfinance as yf

def scrape_components(url, industry):
    df = pd.DataFrame(columns=['Code', 'Company'])
    if not url.startswith('https://'):
        url = f'https://{url}'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    comp_header = [str(i.get_text()) for i in soup.find_all('h3')]
    industry_index = comp_header.index(industry)
    auto_comp = soup.find_all('table')[industry_index]
    for row in auto_comp.find_all('tr')[1::]:
        contents = [val.get_text() for val in row.find_all('td')]
        df.loc[len(df)] = contents
    print(df.shape)
    df.to_parquet("n225_code.parquet", engine='pyarrow', index=False)
    return True

def download_historical_data(ticker_file):
    tickerStrings = pd.read_parquet(ticker_file)['Code'].apply(lambda x: f"{x}.T").tolist()
    df_list = []
    for ticker in tickerStrings:
        data = yf.download(ticker, group_by="Ticker", period='1y')
        data['Ticker'] = ticker.strip(".T")  # Add ticker column
        df_list.append(data)
    df = pd.concat(df_list).reset_index()
    print(df.shape)
    df.to_parquet("n225_comp_hist.parquet", engine="pyarrow", coerce_timestamps="us")
    return True

def download_info_data(ticker_file):
    tickerStrings = pd.read_parquet(ticker_file)['Code'].apply(lambda x: f"{x}.T").tolist()
    df_list = []
    for ticker in tickerStrings:
        t_shares = ticker.strip(".T"), yf.Ticker(ticker).get_fast_info()['shares']
        df_list.append(t_shares)
    df = pd.DataFrame(df_list, columns=['Ticker', 'Shares'])
    print(df.shape)
    df.to_parquet("n225_info.parquet", engine="pyarrow")
    return True
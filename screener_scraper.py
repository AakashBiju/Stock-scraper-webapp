import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import statistics
import pandas as pd
import matplotlib.pyplot as plt
import time

def remove_non_numeric(s):
    """Remove non-numeric characters from a string."""
    return re.sub(r'\D', '', s)

def get_numeric_value(text):
    """Extract numeric value from text, removing non-numeric characters."""
    return int(remove_non_numeric(text))

def calculate_intrinsic_pe(cost_of_capital, roce, growth_high_period, high_period_years, fade_period_years, terminal_growth_rate):
    # Implement the growth-RoC DCF model to calculate intrinsic PE

    intrinsic_pe = cost_of_capital / (roce - growth_high_period)

    # Apply linear fade during the fade period to terminal growth rate
    fade_years = fade_period_years
    growth_diff = growth_high_period - terminal_growth_rate
    fade_increment = growth_diff / fade_years
    fade_growth_rates = [growth_high_period - i * fade_increment for i in range(1, fade_years + 1)]

    return intrinsic_pe, fade_growth_rates


# Define the get_data function

def get_data(symbol):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    url = f'https://www.screener.in/company/{symbol}'

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    #------scraping the Market Cap data-------------
    market_cap_text = soup.find('li',{'class':'flex flex-space-between'}).text
    market_cap_value = get_numeric_value(market_cap_text)
    
    #------scraping the FY23 Net Profit--------------
    profit_text = soup.find('table',{'class':'data-table responsive-text-nowrap'}).find_all_next('tr',{'class':'strong'})[5].text
    profit_value_17 = get_numeric_value(profit_text.split('\n')[17])

    FY23_PE = (market_cap_value / profit_value_17)

    #-------Scraping the RoCE of the last 5 years excluding 2023------------
    roce22 = soup.find('section',{'id':'ratios'}).find_all_next('td')[76].text
    roce21 = soup.find('section',{'id':'ratios'}).find_all_next('td')[75].text
    roce20 = soup.find('section',{'id':'ratios'}).find_all_next('td')[74].text
    roce19 = soup.find('section',{'id':'ratios'}).find_all_next('td')[73].text
    roce18 = soup.find('section',{'id':'ratios'}).find_all_next('td')[72].text
    #---------------Computing the median--------------------
    median_roce = [roce22,roce21,roce20,roce19,roce18]
    roce_values = [int(roce[:-1]) for roce in median_roce]
    median = statistics.median(roce_values)
    
    #-------------Scraping the current price of the stock-----------
    price = soup.find('div',{'class':'flex flex-align-center'}).text.strip()
    Price = price[0:7]

    #------------------Scraping the Compounded Sales Growth table -------------
    csg = soup.find('table',{'class':'ranges-table'}).text
    csg_values= re.findall(r'\d+%', csg)

    #------------Scraping the Compounded Profit Growth table ---------------
    cpg = soup.find_all('table',{'class':'ranges-table'})[1].text
    cpg_values = re.findall(r'\d+%', cpg)

    stock = {
        'Symbol': symbol,
        'Name': soup.find('h1',{'class':'h2 shrink-text'}).text.strip(),
        'Price': Price,
        'FY23 PE': "{:.2f}".format(FY23_PE),
        'RoCE' : median,
        'CSG': [int(value[:-1]) for value in csg_values],  # Remove percentage sign and convert to int
        'CPG': [int(value[:-1]) for value in cpg_values]  # Remove percentage sign and convert to int
    }
    
    return stock

def main():
    st.set_page_config(page_title="Stock Data", page_icon="💹",layout = 'wide')
    
    st.title('Stock Data Scraper')
    symbol_input = st.text_input("Enter the NSE/BSE symbol of the company:")

    #----------Initialize session state-----------
    if "load_state" not in st.session_state:
        st.session_state.load_state = False
    if st.button('Get Stock Data') or st.session_state.load_state:
        st.session_state.load_state = True
        stock_data = get_data(symbol_input)
        if stock_data:
            left_column, right_column = st.columns(2)
            with left_column:
                st.write("Stock Symbol:", stock_data['Symbol'])
                st.write("Company Name:", stock_data['Name'])
                stock_price_str = stock_data['Price']
                stock_price_numeric = float(''.join(filter(str.isdigit, stock_price_str)))
                st.write("Price:", stock_price_numeric)
                st.write("FY23 PE:", stock_data['FY23 PE'])
                st.write("5-yr median pre-tax RoCe(%):", stock_data['RoCE'])

            st.write("---")

            with right_column:
                # ---------Create DataFrame for CSG and CPG values--------------
                data_dict = {'': ['10 YRS','5 YRS','3 YRS','TTM'],
                            'Sales Growth': stock_data['CSG'],
                            'Profit Growth': stock_data['CPG']
                            }
                df = pd.DataFrame(data_dict)
                df = df.transpose()  # Transpose the DataFrame
                st.table(df)

            left_chart, right_chart = st.columns(2)

            with left_chart:
                # --------------Plot horizontal bar chart for CSG-------------
                plt.figure(figsize=(8, 6))
                plt.barh(df.columns, df.iloc[1].values, color='skyblue')
                plt.xlabel('Sales Growth(%)')
                plt.ylabel('Time Period')
                plt.title('Compounded Sales Growth (CSG)')
                st.pyplot(plt)

            with right_chart:
                # -------------Plot horizontal bar chart for CPG-----------------
                plt.figure(figsize=(8, 6))
                plt.barh(df.columns, df.iloc[2].values, color='salmon')
                plt.xlabel('Profit Growth(%)')
                plt.ylabel('Time Period')
                plt.title('Compounded Profit Growth (CPG)')
                st.pyplot(plt)

            # -------Add user inputs and calculations for intrinsic PE and degree of overvaluation-------
            st.sidebar.title('DCF Model and Overvaluation Calculation')
            st.sidebar.write('Play with inputs to see changes in intrinsic PE and overevaluation:')
            cost_of_capital = st.sidebar.slider('Cost of Capital(CoC): %', min_value=8.0, max_value=16.0, value=12.0)
            roce = st.sidebar.slider('Return on Capital Employed (RoCE): %', min_value=10.0, max_value=100.0, value=20.0)
            growth_high_period = st.sidebar.slider('Growth during High Growth Period: $', min_value=8.0, max_value=20.0, value=12.0)
            high_period_years = st.sidebar.slider('High Growth Period (Years)', min_value=10, max_value=25, value=15)
            fade_period_years = st.sidebar.slider('Fade Period (Years)', min_value=5, max_value=20, value=15)
            terminal_growth_rate = st.sidebar.slider('Terminal Growth Rate (%)', min_value=0.0, max_value=7.5, value=5.0)

            intrinsic_pe, fade_growth_rates = calculate_intrinsic_pe(cost_of_capital, roce, growth_high_period, high_period_years, fade_period_years, terminal_growth_rate)

            current_pe = stock_price_numeric / float(stock_data['FY23 PE'])
            if current_pe < float(stock_data['FY23 PE']):
                degree_of_overvaluation = (current_pe / intrinsic_pe) - 1
            else:
                degree_of_overvaluation = (float(stock_data['FY23 PE']) / intrinsic_pe) - 1

            st.sidebar.write('Intrinsic PE:', "{:.2f}".format(intrinsic_pe))
            st.sidebar.write('Degree of Overvaluation:', "{:.2f}%".format(degree_of_overvaluation * 100))
            #st.warning("No data available for the entered symbol.")

if __name__ == '__main__':
    main()
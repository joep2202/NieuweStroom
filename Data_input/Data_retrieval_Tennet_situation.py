import pandas as pd
from test_2 import test

class import_data_per_day:
    def __init__(self):
        # get data from CSV
        self.allocatie_trading = pd.read_csv('data/DecemberDataAlloTrading.csv')
        self.onbalanskosten = pd.read_csv('data/DecemberDataOnbalanskosten.csv')
        self.ZWC = pd.read_csv('data/DecemberDataZWC.csv')
        self.DA_bid = pd.read_csv('data/e_prog_dec.csv')
        # List to select necessary data from csv
        self.allocatie_trading_columns = ['From_NL','Total_Allocation_MWh_both_tenants','Imbalance_Short_EurMWh', 'Imbalance_Long_EurMWh', 'EPEX_EurMWh', 'Buy_MW', 'Sell_MW','Traded_Volume_MWh', 'Price_Eur']
        self.DA_bid_columns = ['From_NL', 'Abs_E_Volume_MWh_both_tenants']
        self.test = test(self.onbalanskosten)

    def interval_to_time(self, interval):
        hours = interval // 4  # Each interval represents 15 minutes, so 4 intervals = 1 hour
        minutes = (interval % 4) * 15  # Remaining intervals represent minutes
        return f"{hours:02d}:{minutes:02d}"

    def get_data(self, day, current_interval, length_forecast):
        self.time = self.interval_to_time(current_interval)
        #Get right data for allocation and trading
        self.start_allocatie_trading = self.allocatie_trading[self.allocatie_trading['From_NL'].str.contains(day + ' ' + self.time)]
        self.start_allocatie_trading = self.start_allocatie_trading.index[0]
        self.allocatie_trading = self.allocatie_trading.iloc[self.start_allocatie_trading:self.start_allocatie_trading + (2 * length_forecast)]
        #self.allocatie_trading = self.allocatie_trading[self.allocatie_trading['From_NL'].str.contains(day)]
        self.tenant_1_allocatie =  self.allocatie_trading[self.allocatie_trading['Tenant'] == 1]
        self.allocatie_trading = self.allocatie_trading[self.allocatie_trading['Tenant'] == 0]
        self.allocatie_trading = self.allocatie_trading.fillna(0)
        self.allocatie_trading.reset_index(inplace=True, drop=True)
        self.tenant_1_allocatie.reset_index(inplace=True, drop= True)
        self.allocatie_trading['Total_Allocation_MWh_both_tenants'] = self.allocatie_trading['Total_Allocation_MWh'] + self.tenant_1_allocatie['Total_Allocation_MWh']
        self.allocatie_trading = self.allocatie_trading.filter(self.allocatie_trading_columns)
        #print(self.allocatie_trading.to_string())

        #Get right data for DA BID
        self.start_DA_bid = self.DA_bid[self.DA_bid['From_NL'].str.contains(day+' ' + self.time)]
        self.start_DA_bid = self.start_DA_bid.index[0]
        self.DA_bid = self.DA_bid.iloc[self.start_DA_bid:self.start_DA_bid+(2*length_forecast)]
        self.tenant_1_DA_bid = self.DA_bid[self.DA_bid['Tenant'] == 1]
        self.DA_bid = self.DA_bid[self.DA_bid['Tenant'] == 0]
        self.DA_bid = self.DA_bid.fillna(0)
        self.DA_bid.reset_index(inplace=True, drop=True)
        self.tenant_1_DA_bid.reset_index(inplace=True, drop=True)
        self.DA_bid['Abs_E_Volume_MWh_both_tenants'] = self.DA_bid['Abs_E_Volume_MWh'] + self.tenant_1_DA_bid['Abs_E_Volume_MWh']
        self.DA_bid = self.DA_bid.filter(self.DA_bid_columns)

        # Get right data for onbalanskosten
        self.start_onbalanskosten = self.onbalanskosten[self.onbalanskosten['datum'].str.contains(day) & self.onbalanskosten['periode_van'].str.contains(self.time)]
        self.start_onbalanskosten = self.start_onbalanskosten.index[0]
        self.onbalanskosten = self.onbalanskosten.iloc[self.start_onbalanskosten:self.start_onbalanskosten+length_forecast]
        self.onbalanskosten.reset_index(inplace=True, drop=True)

        # Get right data for ZWC we have to group by clusters to get the totals as most are divided in different clusters
        self.start_ZWC = self.ZWC[self.ZWC['Timestamp_NL'].str.contains(day + ' ' + self.time)]
        self.start_ZWC = self.start_ZWC.index[0]
        self.ZWC = self.ZWC.iloc[self.start_ZWC:self.start_ZWC + (20 * length_forecast)]
        #self.ZWC = self.ZWC[self.ZWC['Timestamp_NL'].str.contains(day)]
        self.ZWC_final = pd.DataFrame()
        self.ZWC_final['Timestamp_NL'] = self.ZWC['Timestamp_NL'].unique()
        self.ZWC = self.ZWC.drop_duplicates()
        self.ZWC['Sum_forecast'] = self.ZWC.groupby(['Timestamp_NL', 'ForecastClusterGroup'])['ForecastAfterScaling_MWh_PTE'].transform('sum')
        self.ZWC['Sum_allocatie'] = self.ZWC.groupby(['Timestamp_NL', 'ForecastClusterGroup'])['Cluster_Allocatie_MWh_PTE'].transform('sum')
        self.solar = self.ZWC[self.ZWC['ForecastClusterGroup'] == 'Solar']
        self.solar = self.solar.drop_duplicates(['Timestamp_NL', 'ForecastClusterGroup'])
        self.solar.reset_index(drop=True, inplace=True)
        self.wind = self.ZWC[self.ZWC['ForecastClusterGroup'] == 'Wind']
        self.wind = self.wind.drop_duplicates(['Timestamp_NL', 'ForecastClusterGroup'])
        self.wind.reset_index(drop=True, inplace=True)
        self.consumption = self.ZWC[self.ZWC['ForecastClusterGroup'] == 'Consumption']
        self.consumption = self.consumption.drop_duplicates(['Timestamp_NL', 'ForecastClusterGroup'])
        self.consumption.reset_index(drop=True, inplace=True)
        self.ZWC_final['Forecast_solar'] = self.solar['Sum_forecast']
        self.ZWC_final['Allocation_solar'] = self.solar['Sum_allocatie']
        self.ZWC_final['Forecast_wind'] = self.wind['Sum_forecast']
        self.ZWC_final['Allocation_wind'] = self.wind['Sum_allocatie']
        self.ZWC_final['Forecast_consumption'] = self.consumption['Sum_forecast']
        self.ZWC_final['Allocation_consumption'] = self.consumption['Sum_allocatie']
        return self.allocatie_trading, self.onbalanskosten, self.ZWC_final, self.DA_bid
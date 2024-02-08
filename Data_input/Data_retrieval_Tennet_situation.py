import pandas as pd

class import_data_per_day:
    def __init__(self):
        self.allocatie_trading = pd.read_csv('data/DecemberDataAlloTrading.csv')
        self.onbalanskosten = pd.read_csv('data/DecemberDataOnbalanskosten.csv')
        self.ZWC = pd.read_csv('data/DecemberDataZWC.csv')
        self.allocatie_trading_columns = ['From_NL','Total_Allocation_MWh_both_tenants','Imbalance_Short_EurMWh', 'Imbalance_Long_EurMWh', 'EPEX_EurMWh', 'Buy_MW', 'Sell_MW','Traded_Volume_MWh', 'Price_Eur']

    def get_data(self, day):
        #Get right data for allocation and trading
        self.allocatie_trading = self.allocatie_trading[self.allocatie_trading['From_NL'].str.contains(day)]
        self.tenant_1_allocatie =  self.allocatie_trading[self.allocatie_trading['Tenant'] == 1]
        self.allocatie_trading = self.allocatie_trading[self.allocatie_trading['Tenant'] == 0]
        self.allocatie_trading = self.allocatie_trading.fillna(0)
        self.allocatie_trading.reset_index(inplace=True, drop=True)
        self.tenant_1_allocatie.reset_index(inplace=True, drop= True)
        #self.allocatie_trading['Total_Allocation_kWh_both_tenants'] = self.allocatie_trading['Total_Allocation_kWh'] + self.tenant_1_allocatie['Total_Allocation_kWh']
        self.allocatie_trading['Total_Allocation_MWh_both_tenants'] = self.allocatie_trading['Total_Allocation_MWh'] + self.tenant_1_allocatie['Total_Allocation_MWh']
        self.allocatie_trading = self.allocatie_trading.filter(self.allocatie_trading_columns)
        #print(self.allocatie_trading.to_string())

        # Get right data for onbalanskosten
        self.onbalanskosten = self.onbalanskosten[self.onbalanskosten['datum'].str.contains(day)]
        self.onbalanskosten.reset_index(inplace=True, drop=True)
        #print(self.onbalanskosten.to_string())

        # Get right data for ZWC
        self.ZWC = self.ZWC[self.ZWC['Timestamp_NL'].str.contains(day)]
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
        #print(self.ZWC_final.to_string())

        return self.allocatie_trading, self.onbalanskosten, self.ZWC_final

# if __name__ == "__main__":
#     import_data = import_data_per_day()
#     import_data.get_data("10/12/2023")
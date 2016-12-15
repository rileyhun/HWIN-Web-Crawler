import pandas as pd
import datetime
import numpy as np

def calculate():
    data = pd.read_csv("Account Status June 02, 2016.csv")
    data = data[(data['Transaction Type'].str.contains("Registration")==False) & (data['Transaction Type'] != 'Prepaid')]
    data.Date = pd.to_datetime(data.Date)
    data['Amount'] = data['Amount'].astype(str)
    data['Amount'] = data['Amount'].str.lstrip('$')
    data['Amount'] = data['Amount'].astype(float)
    data = data[['GeneratorID', 'Date', 'Amount']]
    grouped = data.groupby('GeneratorID')
    result = grouped.apply(lambda x: x.set_index('Date').resample('M', how=np.sum))
    result.fillna(0, inplace=True)
    result.reset_index(inplace=True)
    result.set_index('Date', inplace=True)
    result = result.ix['2016-01-01':'2016-12-31']
    result = result.groupby('GeneratorID')['Amount'].sum()
    print(result)
    result.to_csv("HWIN LL.csv")

calculate()

# data = pd.read_csv("Account Status June 02, 2016.csv", parse_dates=True)
# data = data[(data['Transaction Type'].str.contains("Registration")==False) & (data['Transaction Type'] != 'Prepaid')]
# data.Date = pd.to_datetime(data.Date)
# data['Amount'] = data['Amount'].astype(str)
# data['Amount'] = data['Amount'].str.lstrip('$')
# data.reset_index(inplace=True)
# data.set_index(['Date Shipped'], inplace=True)
#
#
# grouper = data.groupby([pd.TimeGrouper('1M'), 'GeneratorID'])
# result = grouper['Amount'].sum()
# result = result.groupby(['GeneratorID'])
#
#
# print(result)
# print(data_Monthly)
# result.to_csv("HWIN LL.csv")


# average_tonnage = data.groupby(['GeneratorID'])['Amount'].mean()
# print(average_tonnage)
# average_tonnage.to_csv("average_tonnage.csv")
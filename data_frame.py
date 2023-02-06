import os
from decimal import Decimal
import pandas as pd
from datetime import datetime as dt

from card_filter import StatementFilter


class DataFrame:
    def __init__(self, data):
        self.df = pd.DataFrame.from_dict(data)
        self.bill_months = []
        self.bill_df = self.get_bill_df()
    
    
    def get_bill_df(self):
        data = []
        total_data = dict()
        self.df['Bill Month'] = self.df['Bill Date'].apply(lambda x: x.strftime('%b %y'))
        self.bill_months = self.df['Bill Month'].unique()
        
        for month in self.bill_months:
            apple_card = sum(self.df[(self.df['Provider'] == 'Apple') & (self.df['Bill Month'] == month)]['Amount'])
            chase_credit = sum(self.df[(self.df['Provider'] == 'Chase') & (self.df['Account'] == 'Credit') & (self.df['Bill Month'] == month)]['Amount'])
            chase_checking = sum(self.df[(self.df['Provider'] == 'Chase') & (self.df['Account'] == 'Checkings') & (self.df['Bill Month'] == month)]['Amount'])
            chase_saving = sum(self.df[(self.df['Provider'] == 'Chase') & (self.df['Account'] == 'Savings') & (self.df['Bill Month'] == month)]['Amount'])
            total_credit = apple_card + chase_credit
            data.append({
                "Bill Month": month,
                'Total Credit': total_credit,
                "Apple Card": apple_card,
                "Chase Credit": chase_credit,
                "Chase Checkings": chase_checking,
                "Chase Savings": chase_saving
            })
        
        partial_bill_df = pd.DataFrame.from_dict(data)
        for col in partial_bill_df.columns:
            if col == 'Bill Month':
                total_data[col] = 'Total'
            else:
                total_data[col] = partial_bill_df[col].sum()
        new_row_df = pd.DataFrame(total_data, index=[0])
        
        return pd.concat([new_row_df, partial_bill_df]).reset_index(drop=True)
    
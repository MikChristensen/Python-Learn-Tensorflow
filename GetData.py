from asyncio.windows_events import NULL
from symtable import Symbol
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import yfinance as yf
import pyodbc
import datetime as dt
class getData():

    def getHistoryYfinance(self, symbol, interval, period):

        data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers = symbol,

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        # period = "ytd",
        period = period,

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = interval,

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by = 'ticker',

        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust = False,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost = False,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads = True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy = None
    )
        return data


    def getHistoryAlphaVantage(self):

        ts = TimeSeries(key='JW775EM18T0NSBL7', output_format='pandas')
        data, meta_data = ts.get_intraday(symbol='MSFT',interval=self.interval, outputsize='full')
        
        return data

    def getEmaHistory(self):

        emasUsed = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]
        data = self.getHistory()
        
        for x in emasUsed:
            ema = x
            data["EMA_"+str(ema)] = round(data.iloc[:,0].ewm(span=ema,adjust=False).mean(),2)
        return data

    def getStockData(self, symbol, interval, date):
                
        conn_str = (
            r'Driver=SQL Server;'
            r'Server=.\SQLEXPRESS;'
            r'Database=StockData;'
            r'Trusted_Connectstr(ion=)yes;'
            )
        cnxn = pyodbc.connect(conn_str)
        sqlA2 = """SELECT [FK_SymbolID]
            ,[CompanyName]
            ,[SymbolName]
            ,[Interval]
            ,[FK_IntervalID]
            ,[Datetime]
            ,[Adj Close]
            ,[Close]
            ,[High]
            ,[Low]
            ,[Open]
            ,[Volume]
        FROM [StockData].[dbo].[VI_StockData]
        WHERE 
            [SymbolName] = '"""+ symbol + """'
            AND [Interval] = '"""+ interval + """'
            AND cast(CAST(Datetime AS Date) AS VARCHAR) = '""" + date + "'"
            
        df = pd.read_sql(sqlA2,cnxn)
        print(df.columns) 

    def getDateRange(self):
                
        myConnection = pyodbc.connect(
                    r'Driver=SQL Server;'
            r'Server=.\SQLEXPRESS;'
            r'Database=StockData;'
            r'Trusted_Connectstr(ion=)yes;')        

        sqlstr = ("""SELECT DISTINCT
                        CAST(Datetime AS Date) AS Date
                    FROM [StockData].[dbo].[VI_StockData]
                    order by CAST(Datetime AS Date) ASC 
                """)
        sql_query = pd.read_sql_query (sqlstr, myConnection)

        df = pd.DataFrame(sql_query, columns = ['Date'])
        return(df) 

    def getInterval(self):
                
        myConnection = pyodbc.connect(
                    r'Driver=SQL Server;'
            r'Server=.\SQLEXPRESS;'
            r'Database=StockData;'
            r'Trusted_Connectstr(ion=)yes;')        

        sqlstr = ("""SELECT [Interval]
                    FROM [StockData].[dbo].[VI_Interval] 
                """)

        sql_query = pd.read_sql_query (sqlstr, myConnection)

        df = pd.DataFrame(sql_query, columns = ['Interval'])
        return(df)       

    def getStockDataSQL(self, symbol, interval, date):
                    
        myConnection = pyodbc.connect(
                    r'Driver=SQL Server;'
            r'Server=.\SQLEXPRESS;'
            r'Database=StockData;'
            r'Trusted_Connectstr(ion=)yes;')

        sqlstr = ("""SELECT 
            [Datetime]
            ,[Adj Close]
            ,[Close]
            ,[High]
            ,[Low]
            ,[Open]
            ,[Volume]
            FROM [StockData].[dbo].[VI_StockData]
            WHERE 
            [SymbolName] = '""" + symbol + """'
            AND [Interval] = '""" + interval + """'
            AND CAST(Datetime AS Date) = '""" + date + """'
            """)
        sql_query = pd.read_sql_query (sqlstr, myConnection)

        df = pd.DataFrame(sql_query, columns = ['Datetime', 'AdjClose', 'Close', 'High', 'Low', 'Open', 'Volume'])
        df = df.set_index(['Datetime'])
        return(df)

    def getStockDataMonthSQL(self, symbol, interval):
                    
        myConnection = pyodbc.connect(
                    r'Driver=SQL Server;'
            r'Server=.\SQLEXPRESS;'
            r'Database=StockData;'
            r'Trusted_Connectstr(ion=)yes;')

        sqlstr = ("""SELECT 
            [Datetime]
            ,[Adj Close]
            ,[Close]
            ,[High]
            ,[Low]
            ,[Open]
            ,[Volume]
            FROM [StockData].[dbo].[VI_StockData]
            WHERE 
            [SymbolName] = '""" + symbol + """'
            AND [Interval] = '""" + interval + """'
            AND CAST(Datetime AS Date) BETWEEN '2022-02-01' AND '2022-03-01'
            """)
        sql_query = pd.read_sql_query (sqlstr, myConnection)

        df = pd.DataFrame(sql_query, columns = ['Datetime', 'AdjClose', 'Close', 'High', 'Low', 'Open', 'Volume'])
        df = df.set_index(['Datetime'])
        return(df)                
 
    def addTest(self, AlgorithmName, Interval, PeriodDescription):
        conn_str = (
                r'Driver=SQL Server;'
                r'Server=.\SQLEXPRESS;'
                r'Database=StockData;'
                r'Trusted_Connectstr(ion=)yes;'
                )
        cnxn = pyodbc.connect(conn_str)
        cnxnCursor = cnxn.cursor()
        cnxnCursor.execute("EXECUTE [dbo].[SP_AddTest] @AlgorithmName = ?, @Interval = ?, @PeriodDescription =?", AlgorithmName, Interval, PeriodDescription)
        cnxn.commit()


    def addParameter(self, AlgorithmName, Interval, PeriodDescription, StartCapital, Comission):
        conn_str = (
                r'Driver=SQL Server;'
                r'Server=.\SQLEXPRESS;'
                r'Database=StockData;'
                r'Trusted_Connectstr(ion=)yes;'
                )
        cnxn = pyodbc.connect(conn_str)
        cnxnCursor = cnxn.cursor()
        cnxnCursor.execute("EXECUTE [dbo].[SP_AddParameter] @AlgorithmName = ?, @Interval = ?, @PeriodDescription =?, @StartCapital = ?, @Comission = ?", AlgorithmName, Interval, PeriodDescription, StartCapital, Comission)
        cnxn.commit() 

    def addEarnings(self, AlgorithmName, Interval, PeriodDescription, FinalCapital, PercentageEarning):
        conn_str = (
                r'Driver=SQL Server;'
                r'Server=.\SQLEXPRESS;'
                r'Database=StockData;'
                r'Trusted_Connectstr(ion=)yes;'
                )
        cnxn = pyodbc.connect(conn_str)
        cnxnCursor = cnxn.cursor()
        cnxnCursor.execute("EXECUTE [dbo].[SP_AddEarning] @AlgorithmName = ?, @Interval = ?, @PeriodDescription =?, @FinalCapital = ?, @EarningPercentage = ?", AlgorithmName, Interval, PeriodDescription, FinalCapital, PercentageEarning)
        cnxn.commit() 

    def getSymbols(self):
                
        myConnection = pyodbc.connect(
                    r'Driver=SQL Server;'
            r'Server=.\SQLEXPRESS;'
            r'Database=StockData;'
            r'Trusted_Connectstr(ion=)yes;')        

        sqlstr = ("""SELECT [PK_SymbolID]
                        ,[SymbolName]
                        ,[CompanyName]
                    FROM [StockData].[dbo].[VI_Symbol] 
                """)
        sql_query = pd.read_sql_query (sqlstr, myConnection)

        df = pd.DataFrame(sql_query, columns = ['PK_SymbolID', 'SymbolName','CompanyName'])
        return(df)
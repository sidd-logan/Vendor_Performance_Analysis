import sqlite3
import pandas as pd
import logging
import ingest_db


logging.basicConfig(
    filename="logs/get_vendor_summ.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

def create_vendor_summary(conn):
    """ this function will merge the different tables to get the overall vendor summary and adding new column in the resultant data """
    vendor_summ_table=pd.read_sql_query(""" with freight_summ as(
select 
VendorNumber,
sum(Freight) as freight_cost 
from vendor_invoice group by VendorNumber
),
purchase_summ as(
select 
p.VendorName,
p.VendorNumber,
p.Brand,
p.Description,
p.PurchasePrice,
pp.Volume,
pp.price as actual_price,
sum(p.quantity) as total_purchase_quantity,
sum(p.Dollars) as total_purchase_dollars
from purchases p 
join purchase_prices pp
on p.Brand=pp.Brand
where p.PurchasePrice > 0
group by p.VendorName,p.VendorNumber,p.Brand,p.Description,p.PurchasePrice,pp.Volume,pp.price
order by total_purchase_dollars
),
sales_summ as(
select VendorNo,
Brand,
sum(SalesQuantity)as total_quantity,
sum(SalesDollars)as total_dollars,
sum(SalesPrice)as total_sales,
sum(ExciseTax)as total_ExciseTax
from sales
group by VendorNo,Brand
)

select 
ps.VendorName,
ps.VendorNumber,
ps.Brand,
ps.Description,
ps.PurchasePrice,
ps.actual_price,
ps.Volume,
ps.total_purchase_quantity,
ps.total_purchase_dollars,
ss.total_quantity,
ss.total_dollars,
ss.total_sales,
ss.total_ExciseTax,
fs.freight_cost
from purchase_summ ps
left join sales_summ ss
on ps.VendorNumber=ss.VendorNo
and ps.Brand=ss.Brand
left join freight_summ fs
on ps.VendorNumber=fs.VendorNumber
order by ps.total_purchase_dollars desc""",conn)
    return vendor_summ_table

def clean_data(df):
    """this function will clean the data """
    # changing data type to float
    df['Volume']=df['Volume'].astype('float64')
    #filling missing value with 0
    df.fillna(0,inplace=True)
    #remove spaces from categorical columns
    df['VendorName']=df['VendorName'].str.strip()
    df['Description']=df['Description'].str.strip()
    #creating new column for better analysis
    vendor_summ_table['GrossProfit']=vendor_summ_table['total_dollars']-vendor_summ_table['total_purchase_dollars']
    vendor_summ_table['ProfitMargin']=(vendor_summ_table['GrossProfit']/vendor_summ_table['total_dollars'])*100
    vendor_summ_table['StockTurnover']=vendor_summ_table['total_sales']/vendor_summ_table['total_purchase_quantity']
    vendor_summ_table['SalestoPurchaseRatio']=vendor_summ_table['total_dollars']/vendor_summ_table['total_purchase_dollars']
    return df

if __name__=='__main__':
    #create database connection
    conn=sqlite3.connect('inventory.db')
    logging.info('Creating vendor summary table ...')
    summary_df=create_vendor_summary(conn)
    logging.info(summary_df.head())
    logging.info("cleaning the data ...")
    clean_df=clean_data(summary_df)
    logging.info(clean_df.head())
    logging.info("ingestion data ...")
    ingest_db.ingest_db(clean_df,'vendor_summ_table',conn)
    logging.info("completed ...")





    
    

    
    


    
   




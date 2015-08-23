from googlefinance import getQuotes
from testing import listCompanies
import json,MySQLdb,threading


def financeDb(tradeSymbol):
    try:
        quote = getQuotes(tradeSymbol)
        return quote[0]['LastTradePrice'] 
    except:
        return None

def writeFinance():
    global listCompanies
    threading.Timer(float(720.0*len(listCompanies)), writeFinance).start()

    conn = MySQLdb.connect(host= "localhost",
                 user="root",
                 passwd="iamroot",
                 db="statschart")
    x = conn.cursor()
    for i in listCompanies.keys():
        tradePrice = financeDb(listCompanies[i][2])
        insertsql = "INSERT INTO financedata(company,stockdata) VALUES ('" +str(listCompanies[i][0])+"',"+ str(tradePrice)+");"
        try:
            x.execute(insertsql)
            conn.commit()
        except:
            conn.rollback()
    conn.close()

if __name__ == "__main__":
    writeFinance()


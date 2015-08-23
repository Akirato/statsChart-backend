import MySQLdb,datetime,re,threading
from testing import sentiment,listCompanies


def ccextractorDatabase(listCompany):
    company = listCompany[0]
    tags = listCompany[1]
    now = datetime.datetime.now()
    past = now - datetime.timedelta(hours=48)

    db = MySQLdb.connect(host="cc-db.cjfgtyzqqkfu.us-west-2.rds.amazonaws.com", port=3306, user="cc-user", passwd="w295jh8", db="cc")
    cursor = db.cursor()
    cursor.execute("select cc_data from programs where stop > '"+ str(past.strftime("%Y-%m-%d %H:%M:%S") + "';"))
    a = cursor.fetchall()

    text = ''
    for i in a:
        if len(i)>0 and i[0]!=None:
            for j in i[0].splitlines():
                text = text + ' ' + j
    db.close()
    lines = re.split(r'[.|!|)|?|}|]|"]',text)
    final_lines=[]
    for i in lines:
        if len(i)>0 and i!=None:
            final_lines.append((i.strip()).capitalize())

    feel = sentiment(final_lines,tags)
    pos = feel[0]
    neg = feel[1]
    conn = MySQLdb.connect(host= "localhost",
                  user="root",
                  passwd="iamroot",
                  db="statschart")
    x = conn.cursor()
    insertsql = "INSERT INTO ccextstats(company,positive,negative) VALUES ('" +str(company)+"',"+ str(pos)+","+str(neg)+");"
    try:
        x.execute(insertsql)
        conn.commit()
    except:
        conn.rollback()
    conn.close()

def writeCCext():
    global listCompanies
    threading.Timer(float((720.0)*len(listCompanies)), writeCCext).start()
    for i in listCompanies.keys():
        ccextractorDatabase(listCompanies[i])

if __name__ == "__main__":
    writeCCext()

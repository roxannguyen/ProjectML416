import traceback

import mysql.connector

from retail_project.model.Customer import Customer

server="localhost"
port=3306
database="k23416_retail"
username="root"
password="@Obama123"
try:
    conn = mysql.connector.connect(
                    host=server,
                    port=port,
                    database=database,
                    user=username,
                    password=password)
except:
    traceback.print_exc()
print("Thành công")
print("--CRUD--")
#Câu 1 -- đăng nhập user

def login_cusstomer(email, pwd):
    cursor = conn.cursor()
    sql = "SELECT * FROM customer" \
          " where Email='" + str(email) + "' and Password='" + str(pwd) + "'"
    cust = None
    cursor.execute(sql)
    dataset = cursor.fetchone()
    if dataset != None:
        cust = Customer()
        cust
        # print("ID===",dataset[0])
        # cust.ID,cust.Name,cust.Phone,cust.Email,cust.Password,cust.IsDeleted = dataset
    cursor.close()
    return cust
cust=login_cusstomer("ntruc@gmail.com", 1234)
if cust==None:
    print("Login failed")
else:
    print("Login succeeded")
    print(cust)
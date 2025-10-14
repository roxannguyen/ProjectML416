import traceback

import mysql.connector

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
    print(sql)
    cursor.execute(sql)
    dataset = cursor.fetchone()
    if dataset is not None:
        print(dataset)
    else:
        print("Login failed")
    cursor.close()

# Cách 1: ép str trong hàm (ở trên đã làm)
login_cusstomer("ntruc@gmail.com", 1234)

# hoặc Cách 2: truyền chuỗi
# login_cusstomer("ntruc@gmail.com", "1234")

#Đăng nhập cho employee
def login_employee(email, pwd):
    cursor = conn.cursor()
    sql = "SELECT * FROM employee" \
          " where Email=%s and Password=%s"
    val=(email, pwd)
    cursor.execute(sql, val)
    dataset = cursor.fetchone()
    if dataset != None:
        print(dataset)
    else:
        print("Login failed")
    cursor.close()
login_employee("Obama@gmail.com",123)

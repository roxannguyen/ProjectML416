import sqlite3, pandas as pd

def top_customers(n, db_path="../databases/Chinook_Sqlite.sqlite"):
    # Kết nối và đọc dữ liệu bảng Invoice
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Invoice")
        rows, cols = cur.fetchall(), [d[0] for d in cur.description]
    df = pd.DataFrame(rows, columns=cols)
    # Nhóm theo CustomerId, tính tổng Total và lấy top n giảm dần
    top_df = (
        df.groupby("CustomerId")["Total"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    return top_df
N = int(input("Nhập số lượng top khách hàng cần xem: "))
print(top_customers(N))

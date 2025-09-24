import pandas as pd

df = pd.read_csv("../dataset/SalesTransactions/SalesTransactions.csv")
df["Total"] = df["UnitPrice"] * df["Quantity"] * (1 - df["Discount"])
product_totals = df.groupby("ProductID")["Total"].sum()
top3 = product_totals.sort_values(ascending=False).head(3)
print("Top 3 sản phẩm bán ra có giá trị cao nhất:")
for pid, total in top3.items():
    print(f" - ProductID: {pid}, Doanh thu: {total:,.0f}")

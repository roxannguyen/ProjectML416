import pandas as pd

def find_orders_within_range(df, minValue, maxValue, sortType=True):
    # Tính tổng giá trị từng đơn hàng
    order_totals = df.groupby("OrderID", group_keys=False).apply(
        lambda x: (x['UnitPrice'] * x['Quantity'] * (1 - x['Discount'])).sum()
    )

    # Lọc đơn hàng trong khoảng min-max
    orders_within_range = order_totals[(order_totals >= minValue) & (order_totals <= maxValue)]

    # Sắp xếp theo sortType (True = tăng dần, False = giảm dần)
    orders_within_range = orders_within_range.sort_values(ascending=sortType)

    # Trả về danh sách OrderID
    unique_orders = orders_within_range.index.tolist()

    return unique_orders


# Đọc file CSV
df = pd.read_csv("../dataset/SalesTransactions/SalesTransactions.csv")

minValue = float(input("Nhập giá trị min: "))
maxValue = float(input("Nhập giá trị max: "))
sortType_input = input("Sắp xếp tăng dần? (True/False): ").strip().lower()

# Xử lý input
if sortType_input == "false":
    sortType = False
else:
    sortType = True

result = find_orders_within_range(df, minValue, maxValue, sortType)
print("Danh sách các hóa đơn trong phạm vi giá trị từ", minValue, "đến", maxValue, "là:", result)

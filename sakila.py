# sakila_web.py
# CHẠY 1 LẦN → TỰ MỞ TRÌNH DUYỆT → CHI TIẾT TẤT CẢ 3 YÊU CẦU

import pymysql
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
import base64
from io import BytesIO
from flask import Flask, render_template_string
import webbrowser
import threading
import time

# === KẾT NỐI SAKILA ===
def getConnect():
    try:
        return pymysql.connect(
            host='localhost', port=3306, database='sakila',
            user='root', password='@Obama123',  # THAY PASS CỦA BẠN
            charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print("Lỗi kết nối:", e)
        return None

def queryDataset(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [i[0] for i in cursor.description]
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=cols)

# === TỰ ĐỘNG TÌM k + ELBOW IMAGE ===
def auto_find_k(X, max_k=8):
    inertias = []
    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, init='k-means++', max_iter=500, random_state=42)
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)

    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(range(1, max_k+1), inertias, 'bo--', markersize=8)
    ax.set_title('ELBOW METHOD - TỰ ĐỘNG TÌM k')
    ax.set_xlabel('Số cụm (k)')
    ax.set_ylabel('Inertia')
    ax.grid(alpha=0.3)
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    encoded = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close(fig)
    elbow_img = f'data:image/png;base64,{encoded}'

    x1, y1 = 1, inertias[0]
    x2, y2 = max_k, inertias[-1]
    distances = []
    for i in range(1, max_k):
        x0, y0 = i + 1, inertias[i]
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        distances.append(num / den if den != 0 else 0)
    k_opt = distances.index(max(distances)) + 2
    return k_opt, elbow_img

# === YÊU CẦU 1: CHI TIẾT KHÁCH THEO PHIM ===
def get_req1_detail(conn):
    df = queryDataset(conn, """
        SELECT f.title, c.customer_id, c.first_name, c.last_name
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film f ON i.film_id = f.film_id
        JOIN customer c ON r.customer_id = c.customer_id
        ORDER BY f.title, c.customer_id
    """)
    films_detail = {}
    for film in sorted(df['title'].unique()):
        cus = df[df['title'] == film][['customer_id', 'first_name', 'last_name']].copy()
        cus.columns = ['ID', 'Tên', 'Họ']
        films_detail[film] = {
            'count': len(cus),
            'customers': cus.to_dict('records')
        }
    return films_detail

# === YÊU CẦU 2: CHI TIẾT KHÁCH THEO CATEGORY ===
def get_req2_detail(conn):
    df = queryDataset(conn, """
        SELECT DISTINCT cat.name AS category, c.customer_id, c.first_name, c.last_name
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film f ON i.film_id = f.film_id
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category cat ON fc.category_id = cat.category_id
        JOIN customer c ON r.customer_id = c.customer_id
        ORDER BY cat.name, c.customer_id
    """)
    categories_detail = {}
    for cat in sorted(df['category'].unique()):
        cus = df[df['category'] == cat][['customer_id', 'first_name', 'last_name']].copy()
        cus.columns = ['ID', 'Tên', 'Họ']
        categories_detail[cat] = {
            'count': len(cus),
            'customers': cus.to_dict('records')
        }
    return categories_detail

# === YÊU CẦU 3: K-MEANS + CHI TIẾT ===
def get_kmeans_data(conn):
    df = queryDataset(conn, """
        SELECT 
            c.customer_id,
            COUNT(r.rental_id) AS total_rentals,
            COUNT(DISTINCT f.film_id) AS unique_films,
            AVG(f.rental_rate) AS avg_rental_rate
        FROM customer c
        LEFT JOIN rental r ON c.customer_id = r.customer_id
        LEFT JOIN inventory i ON r.inventory_id = i.inventory_id
        LEFT JOIN film f ON i.film_id = f.film_id
        GROUP BY c.customer_id
    """).fillna(0)

    X = df[['total_rentals', 'unique_films']].values
    k, elbow_img = auto_find_k(X, max_k=8)

    labels = KMeans(n_clusters=k, init='k-means++', max_iter=500, random_state=42).fit_predict(X)
    df['cluster'] = labels

    clusters_detail = {}
    summary = []
    for i in range(k):
        c = df[df['cluster'] == i]
        cluster_df = c[['customer_id', 'total_rentals', 'unique_films', 'avg_rental_rate']].copy()
        cluster_df.columns = ['ID', 'Lần thuê', 'Phim khác', 'Giá TB']
        clusters_detail[i+1] = cluster_df.to_dict('records')
        summary.append({
            'Cụm': i+1,
            'Số khách': len(c),
            'TB lần thuê': round(c['total_rentals'].mean(), 1),
            'TB phim': round(c['unique_films'].mean(), 1),
            'TB giá': round(c['avg_rental_rate'].mean(), 2)
        })
    summary_df = pd.DataFrame(summary)
    return k, elbow_img, summary_df, clusters_detail

# === FLASK WEB ===
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Sakila Analysis</title>
<style>
    body {font-family: Arial; margin: 40px; background: #f4f7f9;}
    h1, h3, h4 {color: #2c3e50;}
    table {border-collapse: collapse; width: 100%; margin: 15px 0;}
    th, td {border: 1px solid #ccc; padding: 10px; text-align: center;}
    th {background: #3498db; color: white;}
    tr:nth-child(even) {background: #f9f9f9;}
    img {max-width: 600px; border: 1px solid #ddd; border-radius: 8px;}
    .section {background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);}
    .item {margin: 15px 0;}
    .item h4 {margin: 10px 0 5px; color: #e74c3c;}
</style></head><body>
<h1>SAKILA CUSTOMER ANALYSIS – CHI TIẾT TẤT CẢ</h1>

<div class="section">
    <h3>1. KHÁCH HÀNG THEO TÊN PHIM</h3>
    {% for film, data in films_detail.items() %}
    <div class="item">
        <h4>{{ film }} ({{ data.count }} khách)</h4>
        <table>
            <tr><th>ID</th><th>Tên</th><th>Họ</th></tr>
            {% for cust in data.customers %}
            <tr><td>{{ cust.ID }}</td><td>{{ cust.Tên }}</td><td>{{ cust.Họ }}</td></tr>
            {% endfor %}
        </table>
    </div>
    {% endfor %}
</div>

<div class="section">
    <h3>2. KHÁCH HÀNG THEO CATEGORY</h3>
    {% for cat, data in categories_detail.items() %}
    <div class="item">
        <h4>{{ cat }} ({{ data.count }} khách)</h4>
        <table>
            <tr><th>ID</th><th>Tên</th><th>Họ</th></tr>
            {% for cust in data.customers %}
            <tr><td>{{ cust.ID }}</td><td>{{ cust.Tên }}</td><td>{{ cust.Họ }}</td></tr>
            {% endfor %}
        </table>
    </div>
    {% endfor %}
</div>

<div class="section">
    <h3>3. K-MEANS – TỰ ĐỘNG CHỌN k = {{ k }}</h3>
    <img src="{{ elbow_img }}">
    <h4>Tóm tắt các cụm</h4>
    {{ summary_table|safe }}

    <h4>Chi tiết từng khách trong cụm</h4>
    {% for cid, customers in clusters_detail.items() %}
    <div class="item">
        <h4>Cụm {{ cid }} ({{ customers|length }} khách)</h4>
        <table>
            <tr><th>ID</th><th>Lần thuê</th><th>Phim khác</th><th>Giá TB</th></tr>
            {% for cust in customers %}
            <tr>
                <td>{{ cust.ID }}</td>
                <td>{{ cust['Lần thuê'] }}</td>
                <td>{{ cust['Phim khác'] }}</td>
                <td>{{ "%.2f"|format(cust['Giá TB']) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endfor %}
</div>

<p><i>Generated by Python + MySQL + K-Means + Flask</i></p>
</body></html>
"""

@app.route('/')
def index():
    conn = getConnect()
    if not conn: return "Lỗi kết nối DB!"

    films_detail = get_req1_detail(conn)
    categories_detail = get_req2_detail(conn)
    k, elbow_img, summary_df, clusters_detail = get_kmeans_data(conn)
    summary_table = summary_df.to_html(index=False, escape=False)

    conn.close()
    return render_template_string(HTML_TEMPLATE,
                                  films_detail=films_detail,
                                  categories_detail=categories_detail,
                                  k=k, elbow_img=elbow_img,
                                  summary_table=summary_table,
                                  clusters_detail=clusters_detail)

# === MỞ TRÌNH DUYỆT TỰ ĐỘNG ===
def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")

# === CHẠY ===
if __name__ == "__main__":
    print("ĐANG KHỞI ĐỘNG WEB SERVER... (TỰ MỞ TRÌNH DUYỆT)")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(port=5000, debug=False, use_reloader=False)
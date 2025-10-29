import numpy as np
import pandas as pd
import pymysql
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import plotly.express as px
from sqlalchemy.dialects.mssql.information_schema import columns


def getConnect(server, port, database, user, password):
    try:
        conn = pymysql.connect(
            host=server,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor  # Returns dicts, easier for pandas
        )
        return conn
    except Exception as e:
        print("Error:", e)
        return None

def closeConnection(conn):
    if conn != None:
        conn.close()

def queryDataset(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    # Lấy tên cột từ cursor
    columns = [i[0] for i in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)  # Thêm columns
    return df


conn = getConnect('localhost', 3306, 'salesdatabase', 'root', '@Obama123')
sql1 = "select * from customer"
df1 = queryDataset(conn, sql1)
print(df1)

sql2 = "select distinct customer.CustomerId, Age, Annual_Income, Spending_Score " \
    "from customer, customer_spend_score " \
    "where customer.CustomerId = customer_spend_score.customerId"
df2 = queryDataset(conn, sql2)
df2.columns = ['CustomerId', 'Age', 'Annual Income', 'Spending Score']
print(df2)
print(df2.head())
print(df2.describe())

def showHistogram(df,columns):
    plt.figure(1, figsize=(7,8))
    n = 0
    for column in columns:
        n += 1
        plt.subplot(3, 1, n)
        plt.subplots_adjust(hspace=0.5, wspace=0.5)
        sns.histplot(df[column], bins=32, kde=True)  # Thay distplot → histplot + kde
        plt.title(f'Histogram of {column}')
    plt.show()
showHistogram(df2, df2.columns[1:])

def elbowMethod(df,colunmsForElbow):
    X = df.loc[:, colunmsForElbow].values
    inertia = []
    for n in range(1, 11):
        model = KMeans(n_clusters = n,
                       init='k-means++',
                       max_iter=500,
                       random_state=42)
        model.fit(X)
        inertia.append(model.inertia_)

    plt.figure(1, figsize = (15,6))
    plt.plot(np.arange(1, 11), inertia ,'o')
    plt.plot(np.arange(1, 11), inertia ,'--', alpha = 0.5)
    plt.xlabel('Number of CLusters')
    plt.ylabel('Cluster sum of squared distances')
    plt.show()
columns=['Age','Spending Score']
elbowMethod(df2,columns)

def runKMeans(X, cluster):
    model = KMeans(n_clusters=cluster,
                   init='k-means++',
                   max_iter=500,
                   random_state=42)

    model.fit(X)
    labels = model.labels_
    centroids = model.cluster_centers_
    y_kmeans = model.fit_predict(X)
    return y_kmeans, centroids, labels

columns = ['Age', 'Spending Score']
X = df2.loc[:, columns].values
cluster = 4
colors = ["red", "green", "blue", "purple", "black", "pink", "orange"]
y_kmeans, centroids, labels = runKMeans(X, cluster)
print(y_kmeans)
print(centroids)
print(labels)
df2["cluster"] = labels

def visualizeKMeans(X, y_kmeans, cluster, title, xlabel, ylabel, colors):
    plt.figure(figsize = (10,10))
    for i in range (cluster):
        plt.scatter(X[y_kmeans == i, 0],
                    X[y_kmeans == i, 1],
                    s = 100,
                    c = colors[i],
                    label = "Cluster %i"%(i+1))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()

X = df2.loc[:, ['Age', 'Spending Score']].values  # sửa đúng lỗi: thay columns bằng danh sách cột
cluster = 4
colors = ['red', 'green', 'blue', 'purple', 'black', 'pink', 'orange']

y_kmeans, centroids, labels = runKMeans(X, cluster)
print(y_kmeans)
print(centroids)
print(labels)
df2['cluster'] = labels

visualizeKMeans(X,
                y_kmeans,
                cluster,
                "Clusters of Customers - Age X Spending Score",
                "Age",
                "Spending_Score",
                colors)
closeConnection(conn)

def visualizeKMeans(X, y_kmeans, cluster, title, xlabel, ylabel, colors) :
    plt.figure(figsize=(10, 10))
    for i in range(cluster):
        plt.scatter(X[y_kmeans == i, 0], X[y_kmeans == i, 1], s=100, c=colors[i], label='Cluster %i'%(i+1))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt. legend()
    plt.show()

visualizeKMeans(X, y_kmeans, cluster,"Clusters of Customers - Age X Spending Score","Age","Spending Score",
colors)
# Gom cụm theo Income và Spending Score
columns = ['Annual Income', 'Spending Score']
elbowMethod(df2, columns)

X = df2.loc[:, columns].values
cluster = 5

y_kmeans, centroids, labels = runKMeans(X, cluster)
print(y_kmeans)
print(centroids)
print(labels)
df2['cluster'] = labels
visualizeKMeans(X,
                y_kmeans,
                cluster,
                "Clusters of Customers - Annual Income X Spending Score",
                "Annual_Income",
                "Spending_Score",
                colors)
def visualize3DKMeans(df, columns, hover_data, cluster):
    fig = px.scatter_3d(df,
                        x = columns[0],
                        y = columns[1],
                        z = columns[2],
                        color = "cluster",
                        hover_data = hover_data,
                        category_orders={'cluster': range(0, cluster)})
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    fig.show()
# Gom cụm với Age, Annual Income, Spending Score
columns = ['Age','Annual Income', 'Spending Score']
elbowMethod(df2, columns)
X = df2.loc[:, columns].values
cluster = 6
y_kmeans, centroids, labels = runKMeans(X, cluster)
print(y_kmeans)
print(centroids)
print(labels)
df2['cluster'] = labels
print(df2.head())

hover_data = df2.columns
visualize3DKMeans(df2, columns, hover_data, cluster)

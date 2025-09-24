from bs4 import BeautifulSoup

#Reading the data inside the xml file to a variable under the name data
with open("../dataset/SalesTransactions/SalesTransactions.xml","r") as f:
    data = f.read()
bs_data = BeautifulSoup(data,"xml")
UelSample = bs_data.find_all("UelSample")
print(UelSample)

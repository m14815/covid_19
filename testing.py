import shapefile
import  china_region
from dbfread import DBF
import mpl_toolkits.basemap as Basemap
print(china_region.search(city='巴州'))

# file = open('City/CN_city.dbf','rb')
# contents = file.read().strip()
# # print(contents)
# print(contents.decode('cp936',errors='ignore'))
# file.close()
table = DBF('City/CN_city.dbf')
count = 0
for record in table:
    print(record)
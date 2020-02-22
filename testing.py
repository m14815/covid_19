import shapefile
import  china_region
from dbfread import DBF
import mpl_toolkits.basemap as Basemap
# file = open('City/CN_city.dbf','rb')
# contents = file.read().strip()
# # print(contents)
# print(contents.decode('cp936',errors='ignore'))
# file.close()
table = DBF('City/CN_city.dbf')
count = 0
for record in table:
    for field in record:
        count+= 1
        print(field, "=", record[field], end = ",")
    print()
print(count)
print(china_region.search_all(county='眉山'))

integer = 1
float_num = 1.0
bool_num = True
complex_num = 1 + 3j
string = 'abcde'
char = 'a'
list_ = [0,1,2,3,4,5]
tuple_ = (0,1,2,3,4,5)
set_ = {0,1,2,3,4,5}
dictionary = {1:1, 2:2, 3:3}

class Test:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def find(self):
        return


def method(name1,name2):

    return


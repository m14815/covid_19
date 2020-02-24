"""
This python program get COVID-19 data from tencent, and visualize data, 2D line graph and China, Global map are used.
Version: 1.0

"""
import datetime
import json
import requests
import time
import warnings
import china_region
import matplotlib.dates as dt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Patch
from mpl_toolkits.basemap import Basemap
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


class Covid19Analysis:
    warnings.filterwarnings('ignore')

    def __init__(self):
        self.url_1 = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5"
        self.url_2 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_other'
        self.update_time = None

    def get_data(self):
        # get data from url
        area_data = json.loads(requests.get(self.url_1).json()['data'])
        china_data = json.loads(requests.get(self.url_2).json()['data'])
        # last update time
        self.update_time = area_data['lastUpdateTime']
        # total illness in china
        cn_total = area_data["chinaTotal"]
        # global areas  data
        area_tree = area_data['areaTree']
        # adding list
        adding_day_list = self.proseeing_data(china_data['chinaDayList'])
        # accumulated total
        accumulated_day_list = self.proseeing_data(china_data['chinaDayAddList'])
        return cn_total, area_tree, adding_day_list, accumulated_day_list

    def proseeing_data(self, data):
        result = {'date_list': [], 'confirm': [], 'suspect': [], 'dead': [], 'heal': []}
        for _ in data:
            month, day = _['date'].split('.')
            result['date_list'] += [datetime.datetime.strptime("2020-%s-%s" % (month, day), '%Y-%m-%d')]
            result['confirm'] += [int(_['confirm'])]
            result['dead'] += [int(_['dead'])]
            result['suspect'] += [int(_['suspect'])]
            result['heal'] += [int(_['heal'])]
        return result

    def processing_city_data(self, data, cat):
        d_cities = {'重庆': '重庆市', '北京': '北京市', '天津': '天津市', '上海': '上海市', '香港': '香港', '澳门': '澳门',
                    '台湾': '台湾'}
        special = {'兵团第四师': '伊犁州', '兵团第九师': '塔城市', '兴安盟乌兰浩特': '乌兰浩特市', '济源示范区': '济源市',
                   '湘西自治州': '吉首市', '普洱': '思茅市', '黔西南州': '兴义市', '第八师石河子': '石河子市',
                   '兵团第十二师': '乌鲁木齐', '六师五家渠': '五家渠市', '第七师': '胡杨河市', '宁东管委会': '银川市',
                   '赣江新区': '南昌市', '菏泽': '菏泽市'}
        province = {}
        for _ in data[0]['children']:
            heal = None
            if cat == 'total':
                heal = 0
            elif cat == 'net':
                heal = _['total']['heal']
            # add direct cities
            if _['name'] in d_cities.keys():
                province[d_cities[_['name']]] = _['total']['confirm'] - heal
            # add Xi Zang
            elif _['name'] == '西藏':
                province[_['name']] = {}
                province[_['name']] = {'拉萨市': _['total']['confirm'] - heal}
            # add cities based on province
            else:
                province[_['name']] = {}
                for c in _['children']:
                    if heal == 'net':
                        heal = c['total']['heal']
                    if (c['name'] != '地区待确认') and (c['name'] != '地区待确定'):
                        if c['name'] in special.keys():
                            if special[c['name']] in province[_['name']].keys():
                                province[_['name']][special[c['name']]] += c['total']['confirm'] - heal
                            else:
                                province[_['name']][special[c['name']]] = c['total']['confirm'] - heal
                        else:
                            search = china_region.search(province=_['name'], city=c['name'])
                            if len(search) > 0:
                                province[_['name']][search['city']] = c['total']['confirm'] - heal
                            else:
                                province[_['name']][c['name']] = c['total']['confirm'] - heal
        return province

    def coloring(self,data):
        color = '#ffffff'
        if data == 0:
            color = '#f0f0f0'
        elif data < 10:
            color = '#ffaa85'
        elif data < 100:
            color = '#ff7b69'
        elif data < 1000:
            color = '#bf2121'
        elif data >= 1000:
            color = '#7f1818'
        return color

    def plot_cn_map(self, *data, title=None):
        lat_min = 0
        lat_max = 60
        lon_min = 80
        lon_max = 150
        font = FontProperties(size=20)
        tw = ['基隆市', '台北市', '桃园县', '宜兰县', '新竹县', '苗栗县', '台中县', '莲花县', '金门县', '南投县', '台中市', '彰化县',
              '云林县', '嘉义县', '台东县', '凤山县', '诏安县', '台南县', '南澳县', '台南市', '屏东县', '高雄市', '台北县', ]
        special = {'大庸市': '张家界市', '株州市': '株洲市', '浑江市': '白城市', '巢湖市': '合肥市', '莱芜市': '济南市', '崇明県': '上海市',
                   '丽江纳西族自治县': '丽江市', '达川市': '达州市', '库尔勒市': '巴州', '叶鲁番市': '吐鲁番地区', '阿勒泰市': '伊犁州',
                   '烏海市': '乌海市', '沙湾县': '塔城市'}
        handles = [
            Patch(color='#ffaa85', alpha=1, linewidth=0),
            Patch(color='#ff7b69', alpha=1, linewidth=0),
            Patch(color='#bf2121', alpha=1, linewidth=0),
            Patch(color='#7f1818', alpha=1, linewidth=0)
        ]
        legend_labels = ['1-9', '10-99', '100-999', '>1000']
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 16)
        cn_map = Basemap(projection='lcc', width=5000000, height=5000000, lat_0=36, lon_0=102, llcrnrlon=lon_min,
                         llcrnrlat=lat_min, urcrnrlon=lon_max, urcrnrlat=lat_max, resolution='i', ax=ax)
        cn_map.readshapefile('City/CN_city', 'cities', drawbounds=True, antialiased=3)
        for info, shape in zip(cn_map.cities_info, cn_map.cities):
            city = info['NAME'].strip('\x00')
            color = '#ffffff'
            if city in tw:
                color = '#ff7b69'
            else:
                if city in special.keys():
                    city = special[city]
                for p_key in data[0].keys():
                    if p_key == city:
                        self.coloring(data[0][p_key])
                        break
                    elif isinstance(data[0][p_key], dict):
                        search = china_region.search(city=city)
                        sc = ''
                        if len(search) > 0:
                            sc = search['city']
                        for c in data[0][p_key].keys():
                            if ((city == c or c in city) or (sc == c or c in sc)) and len(c) > 0:
                                color = self.coloring(data[0][p_key][c])
                                break
                    if color != '#ffffff':
                        break
            if color == '#ffffff':
                print('Not match', city)
            poly = Polygon(shape, facecolor=color, edgecolor=color)
            ax.add_patch(poly)
        cn_map.drawcoastlines(color='black', linewidth=0.4, )
        cn_map.drawparallels(np.arange(lat_min, lat_max, 10), labels=[1, 0, 0, 1])
        cn_map.drawmeridians(np.arange(lon_min, lon_max, 10), labels=[0, 0, 0, 1])
        ax.legend(handles, legend_labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=4, prop={'size': 16})
        plt.title(title + '\n(Update: ' + self.update_time + ")", fontproperties=font)
        plt.show()
        fig.savefig(title + '.PNG')
        plt.close()
        return

    def plot_world_map(self, *data):
        lat_max = 90
        lat_min = -90
        lon_max = 180
        lon_min = -180
        legend_labels = ['1-9', '10-99', '100-999', '>1000']
        font = FontProperties(size=20)
        handles = [
            Patch(color='#ffaa85', alpha=1, linewidth=0),
            Patch(color='#ff7b69', alpha=1, linewidth=0),
            Patch(color='#bf2121', alpha=1, linewidth=0),
            Patch(color='#7f1818', alpha=1, linewidth=0)
        ]
        cdata = {}
        for _ in data[0]:
            if _['name'] == '钻石号邮轮':
                cdata['日本本土'] = _['total']['confirm']
            elif _['name'] in cdata.keys():
                cdata[_['name']] += _['total']['confirm']
            else:
                cdata[_['name']] = _['total']['confirm']
        print(cdata)
        fig, ax = plt.subplots()
        fig.set_size_inches(32, 16)
        world_map = Basemap( lat_0=0, lon_0=180, llcrnrlon=lon_min,
                         llcrnrlat=lat_min, urcrnrlon=lon_max, urcrnrlat=lat_max, resolution='i', ax=ax)
        world_map.readshapefile('世界国家/世界国家','countries', drawbounds=True, antialiased=3)
        for info, shape in zip(world_map.countries_info, world_map.countries):
            country = info['FCNAME']
            color = '#ffffff'
            for key in cdata.keys():
                if str(country) in key or key in str(country):
                    color = self.coloring(cdata[key])
                    break
            poly = Polygon(shape, facecolor=color, edgecolor=color)
            ax.add_patch(poly)
        world_map.drawparallels(np.arange(lat_min, lat_max, 10), labels=[1, 0, 0, 1])
        world_map.drawmeridians(np.arange(lon_min, lon_max, 10), labels=[0, 0, 0, 1])
        ax.legend(handles, legend_labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=4, prop={'size': 16})
        plt.title('COVID-19 world map\n(Update: ' + self.update_time + ")", fontproperties=font)
        plt.show()
        fig.savefig('COVID-19_world_map.PNG')
        plt.close()
        return

    def covid_19_data_plotting(self, title, date, data, legend_labels):
        plt.figure(title, figsize=(10, 8))
        for i in range(len(data)):
            plt.plot(date, data[i], label=legend_labels[i], linestyle='dashed', marker='o')
        plt.grid(linestyle=':')
        plt.legend(loc='best')
        plt.gca().xaxis.set_major_formatter(dt.DateFormatter('%m-%d'))
        plt.gcf().autofmt_xdate()
        plt.title(title + '\n(Update: ' + self.update_time + ')')
        plt.xlabel('Date')
        plt.ylabel('Population')
        plt.savefig(title + '.png')
        plt.show()
        plt.close()
        return

    def prediction(self):
        # the prediction with SEIR model with death, and will be more complex
        N = 10000000
        S = [0]
        E = [0]
        I = [0]
        R = [0]
        D = [0]
        NDs = 14  # Incubation period
        alpha = 0.021  # influce rate
        beta = 0.6  # recovery rate
        gamma = 0.021  # death rate
        theta = [0.0001]  # Explore rate
        r_days = [7, 15]  # recovery duration
        i = 0
        S[0] = N
        R[0] = 0
        I[0] = 0
        D[0] = 0
        while S[-1] > 0:
            S.append(S)
            # S.append(int(S[0] - I[i] - R[i] - D[i]))
            # if len(S) < 30:
            #     E.append(int(S[i] * theta[0]))
            # else:
            #     E.append(int(S[i] * random.randrange(1,3)/10000000))
            #
            # I.append(int(E[i]*alpha) + I[i] - R[i] - D[i])
            # r = random.randint(r_days[0],r_days[1])
            # if len(I) > r:
            #     R.append(int(I[i-r]*beta)+R[i])
            #     D.append(D[i]+int(I[i-r]*gamma))
            # else:
            #     R.append(R[i])
            #     D.append(D[i])
            i += 1
        plt.plot(S, label='suspected')
        plt.plot(E, label='exposed')
        plt.plot(I, label='Inception')
        plt.plot(R, label='Recovered')
        plt.legend(loc='best')
        plt.show()
        plt.close()
        print(S, E, I, R, D)
        return


if __name__ == '__main__':
    labels = ['confirmed', 'suspect', 'dead', 'heal']
    a = Covid19Analysis()
    result = a.get_data()
    print(city_data)
    print()
    # a.covid_19_data_plotting('COVID-19 Daily Data', daily_data[0], daily_data[1:], labels)
    # a.covid_19_data_plotting('COVID-19 Accumulated Tracing', accumulated_data[0], accumulated_data[1:], labels)
    # a.plot_cn_map(city_data, title='COVID-19 map')
    # city_data_net = a.processing_city_data(result[1], 'net')
    # a.plot_cn_map(city_data_net, title='COVID-19 map--net')
    # #
    # a.plot_world_map(result[1])
    # prediction()

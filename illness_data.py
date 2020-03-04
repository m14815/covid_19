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
from scipy import integrate, stats
import numpy as np
import random
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Patch
from mpl_toolkits.basemap import Basemap
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


class Covid19Analysis:
    warnings.filterwarnings('ignore')

    def __init__(self):
        # tencent data
        self.url_1 = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5"
        self.url_2 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_other'
        # alibaba data
        self.url_3 = "https://cdn.mdeer.com/data/yqstaticdata.js?callback=callbackstaticdata&t=1583292696"
        self.update_time = None

    def get_data(self):
        # get data from url
        data = json.loads(requests.get(self.url_3).content.decode('utf-8')[19:-1])
        area_data = json.loads(requests.get(self.url_1).json()['data'])
        china_data = json.loads(requests.get(self.url_2).json()['data'])
        print(data.keys())
        print(data['continentDataList'])
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
        result = {'date': [], 'confirm': [], 'suspect': [], 'dead': [], 'heal': []}
        for _ in data:
            month, day = _['date'].split('.')
            result['date'] += [datetime.datetime.strptime("2020-%s-%s" % (month, day), '%Y-%m-%d')]
            result['confirm'] += [int(_['confirm'])]
            result['dead'] += [int(_['dead'])]
            result['suspect'] += [int(_['suspect'])]
            result['heal'] += [int(_['heal'])]
        return result

    def processing_city_data(self, data, cat=None):
        d_cities = {'重庆': '重庆市', '北京': '北京市', '天津': '天津市', '上海': '上海市', '香港': '香港', '澳门': '澳门',
                    '台湾': '台湾'}
        special = {'兵团第四师': '伊犁州', '兵团第九师': '塔城市', '兴安盟乌兰浩特': '乌兰浩特市', '济源示范区': '济源市',
                   '湘西自治州': '吉首市', '普洱': '思茅市', '黔西南州': '兴义市', '第八师石河子': '石河子市',
                   '兵团第十二师': '乌鲁木齐', '六师五家渠': '五家渠市', '第七师': '胡杨河市', '宁东管委会': '银川市',
                   '赣江新区': '南昌市', '菏泽': '菏泽市'}
        province = {}
        for _ in data[0]['children']:
            heal = 0
            if cat == 'net':
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
                    if cat == 'net':
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

    def coloring(self, data):
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
                        color = self.coloring(data[0][p_key])
                        break
                    elif isinstance(data[0][p_key], dict):
                        search = china_region.search(city=city)
                        sc = ''
                        if len(search) > 0:
                            sc = search['city']
                        for c in data[0][p_key].keys():
                            if ((c in city) or (c in sc )) and len(c) > 0:
                                color = self.coloring(data[0][p_key][c])
                                break
                    if color != '#ffffff':
                        break
            if color == '#ffffff':
                print('Not match', city)
                color = '#f0f0f0'
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
        world_map = Basemap(lat_0=0, lon_0=180, llcrnrlon=lon_min, llcrnrlat=lat_min, urcrnrlon=lon_max,
                            urcrnrlat=lat_max, resolution='i', ax=ax)
        world_map.readshapefile('世界国家/世界国家', 'countries', drawbounds=True, antialiased=3)
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

    def covid_19_data_plotting(self, title, data, legend_labels):
        plt.figure(title, figsize=(10, 8))
        for i in range(len(legend_labels)):
            plt.plot(data['date'], data[legend_labels[i]], label=legend_labels[i], linestyle='dashed', marker='o')
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
        n = 10000000  # total number
        e = 0  # Exposed
        i = 1  # Infections
        r = 0  # Recovered
        d = 0 # death
        s = n - r - i - e - d # Susceptible

        # mu = 7
        # sd = 1
        # NDs = 14  # Incubation period
        alpha = 1/7  # eclipse period to infections rate
        beta = 2.1/n # influence rate
        gamma_1 = 100/n # recovery rate of exposed
        gamma_2 = 0.67  # recovery rate of infections
        omega = 0.02 #death rate
        # theta = [0.0001]   # Explore rate
        # r_days = [7, 15]   # recovery duration
        init_value = (s, e, i, r, d)
        days = np.arange(0, 90)

        def SEIR_model(init_value, _):
            Y = np.zeros(5)
            X = init_value
            # dS/dt = -beta * S * I
            Y[0] = -beta * X[0] * (X[2] + X[1])
            # dE/dt = beta * I * S - (alpha + gamma_1)E
            Y[1] = (beta * X[2] * X[0] * 6 / 10 - (alpha + gamma_1) * X[1])
            # dI/dt = alpha * E - gamma_2 * I
            Y[2] = (alpha * X[1] - gamma_2 * X[2] + beta * X[2] * X[0] / 10 * 4)
            # dR/dt = gamma_1 + gamma_2 * I
            Y[3] = gamma_1 * X[1] + gamma_2 * X[2]
            # dD/dt = omega * I
            Y[4] = omega * X[2]
            return Y

        func_1 = integrate.odeint(SEIR_model, init_value, days)
        plt.plot(func_1[:, 0], label='suspected', color = 'blue')
        plt.plot(func_1[:, 1], label='exposed', color = '#eeae00')
        plt.plot(func_1[:, 2], label='Inception', color = 'red')
        plt.plot(func_1[:, 3], label='Recovered', color = 'green')
        plt.plot(func_1[:, 4], label='Death', color = '#000000')
        plt.legend(loc='best')
        plt.show()
        plt.close()
        return


if __name__ == '__main__':
    labels = ['confirm', 'suspect', 'dead', 'heal']
    a = Covid19Analysis()
    result = a.get_data()
    city_data = a.processing_city_data(result[1], 'total')
    print(city_data)
    a.covid_19_data_plotting('COVID-19 Daily Data', result[3], labels)
    a.covid_19_data_plotting('COVID-19 Accumulated Tracing', result[2], labels)
    net = []
    for c,h,d in zip(result[2]['confirm'], result[2]['heal'], result[2]['dead']):
        net.append(c-h-d)
    result[2]['confirm'] = net
    a.covid_19_data_plotting('COVID-19 Accumulated--Net',result[2],labels)
    a.plot_cn_map(city_data, title='COVID-19 map')
    city_data_net = a.processing_city_data(result[1], 'net')
    print(city_data_net)
    a.plot_cn_map(city_data_net, title='COVID-19 map--net')
    a.plot_world_map(result[1])
    a.prediction()

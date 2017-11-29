from tkinter import *
import math
import urllib.request
import re
from lxml import etree
import time
import datetime
##YAY!
class Map():
    def __init__(self):
        self.tk = Tk()
        self.tk.title("Weather Map")
        self.tk.minsize(width=500,height=500)
        self.canvas = Canvas(self.tk, width=1000,height=600, highlightthickness=0)
        ##Ratio: W = 10.7947389 H = 8.5
        self.canvas_width = 1000
        self.canvas_height = 600
        self.canvas.pack()
        self.start_lat = 46##40.8507
        self.start_lng = -110##-97.4721389
        self.end_lat = 30##32.3122
        self.end_lng = -75##-86.6774
        self.lat_degree_ratio = self.canvas_height/(self.end_lat-self.start_lat)##
        self.lng_degree_ratio = self.canvas_width/(self.end_lng-self.start_lng)##
        self.displace = 0
        self.img = PhotoImage(file="C:\Users\Documents\GitHub\WeatherModel\map_usa.png")
        self.backgroundImage = self.canvas.create_image(0,0,image = self.img, anchor = 'nw')
    def lat_to_pixels(self,lat):
        return((lat-self.start_lat)*self.lat_degree_ratio)
    def lng_to_pixels(self,lng):
        return((lng-self.start_lng)*self.lng_degree_ratio)
    ##def mainloop(self):
    ##    pass
class Weather_station():
    def __init__(self,name,m,lat,lng,identifier,altitude):
        ## Actual locations
        self.name = name
        self.lat = lat
        self.lng = lng
        self.map = m
        self.wind_vector = 0
        self.wind_speed = 0
        self.cloud_status = cloud_keys[0]
        self.altitude = altitude
        ## Map coordinates for window
        ## Latitude is N or S -> Y and longitude is E or W -> X
        self.x = self.map.lng_to_pixels(self.lng)
        self.y = self.map.lat_to_pixels(self.lat)
##        print(self.x)
##        print(self.y)
##        print("_________________")
        self.object = self.map.canvas.create_rectangle(self.x-5,self.y-5,self.x+5,self.y+5,fill="Yellow")
        self.map.canvas.tag_bind(self.object,"<Button-1>",self.onclick)
        self.clouds = None
        self.wind_speed = None
        self.station_identifier = str(identifier)##'72327'
        self.url = self.create_link()##'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR=2017&MONTH=08&FROM=2712&TO=2712&STNM=72327'
    def onclick(self,e):
        print(self.name)
    def create_link(self):
        base_url = ['http://weather.uwyo.edu/cgi-bin/sounding?region=','&TYPE=TEXT%3ALIST&YEAR=']
        this_year = datetime.datetime.now().year
        this_month = datetime.datetime.now().month
        this_day = datetime.datetime.now().day
        this_hour = datetime.datetime.now().hour
        ## Urls are updated at 8:00 AM and 8:00 PM CST
        if this_hour<8:
            this_month-=1
            t_o_d = '00'
        elif this_hour<20:
            t_o_d = '12'
        else:
            t_o_d = '00'
        ## change TO based on time of day
        new_url = str(base_url[0])+'naconf'+str(base_url[1])+str(this_year)+'&MONTH='+str(this_month)+'&FROM='+str(this_day)+t_o_d+'&TO='+str(this_day)+t_o_d+'&STNM='+self.station_identifier
        ##print(new_url)
        return new_url
    def update_observations(self):
        ##print(self.name)
        ##print(self.url)
        data = urllib.request.urlopen(self.data_link)
        this_url = urllib.request.urlopen(self.url)
        table = etree.HTML(this_url.read()).find("body/pre")
        table = stringify_children(table).split()
        save_table = []
        this_bool = False
        altitude_factor = 0
        ##if self.altitude=='h':
            ##print("High Altitude!")
        ##    altitude_factor=80
        for item in table:
            if table.index(item)<24:
                pass
            elif float(item)>(1500):
                this_bool = True
            if this_bool:
                save_table.append(item)
        ##print(save_table)
        num_columns = 11
        index = 0
        wind_speeds = []
        meters = []
        wind_vectors = []
        for item in save_table:
            if index!=0 and (index-6)%11==0:
                wind_speeds.append(item)
            if index!=0 and (index-5)%11==0:
                wind_vectors.append(item)
            if index!=0 and index%11==0:
                meters.append(item)
            index+=1
        ##print(meters)
        ##print(wind_speeds)
        ##print(wind_vectors)
        ##print(len(wind_speeds))
        for x in range(len(wind_speeds)-5,len(wind_speeds)-2):##124,129):
            wind_speeds.pop(x)
        for x in range(len(wind_vectors)-5,len(wind_vectors)-2):
            wind_vectors.pop(x)
        for x in range(len(meters)-5,len(meters)-2):
            meters.pop(x)
        ##print(self.name)
        ##print("Vectors = "+str(wind_vectors))
        ##print("Speeds = "+str(wind_speeds))
        ##print("Mb = "+str(meters))
##        print("-------------------------------------")
##        print(self.url)
##        print("-------------------------------------")
        ##print(self.url)
        ##print(wind_speeds)
        ##print(meters)
        wind_speed_mean = mean_trimmed_data(meters,wind_speeds)
        wind_vector_mean = mean_trimmed_data(meters,wind_vectors)
        ##print(wind_speed_mean)
        ##print(wind_vector_mean)
        ##degrees are 111 km apart
        theta = 0
        if 0<=wind_vector_mean and wind_vector_mean<90:
            theta = 90 - wind_vector_mean
        elif wind_vector_mean>=90:
            theta = 450 - wind_vector_mean
        weather_system_latitude = math.sin((theta)*(math.pi/180)-math.pi)*(predict_distance(wind_speed_mean,12)/59)
        weather_system_longitude = math.cos((theta)*(math.pi/180)-math.pi)*(predict_distance(wind_speed_mean,12)/59)
        this_y = weather_map.lat_to_pixels(weather_system_latitude+weather_stations[self.name].lat)
        this_x = weather_map.lng_to_pixels(weather_system_longitude+weather_stations[self.name].lng)
        cloud_data = urllib.request.urlopen(self.data_link)
        self.cloud_status = parse_cloud_data(cloud_data)
        if self.cloud_status == None:
            print(self.data_link)
        weather_sys = Weather_system(this_x,this_y,10,weather_stations[self.name],wind_vector_mean,wind_speed_mean,self.cloud_status)
##        ##weather_map.canvas.create_rectangle(this_x,this_y,this_x+5,this_y+5,fill="Black")
class Weather_system():
    def __init__(self,x,y,size,base_location,wind_vector,wind_speed,cloud):
        self.cloud_status = cloud
        self.wind_speed = wind_speed
        self.wind_vector = wind_vector
        self.base_location = base_location
        self.size = size
        self.x = x
        self.y = y
        self.object = (base_location.map.canvas.create_oval(self.x-self.size,self.y-size,self.x+self.size,self.y+self.size,fill=cloud_colors[self.cloud_status]))
        self.vector = base_location.map.canvas.create_line(self.x,self.y,base_location.x,base_location.y,arrow=FIRST)
        self.base_location.map.canvas.tag_bind(self.object,"<Button-1>",self.onclick)
    def onclick(self,e):
        print(self.base_location.name)
class Report_area():
    def __init__(self,name,m,lat,lng):
        self.name = name
        self.map = m
        self.lat = lat
        self.lng = lng
        self.x = self.map.lng_to_pixels(self.lng)
        self.y = self.map.lat_to_pixels(self.lat)
        self.object = self.map.canvas.create_rectangle(self.x-5,self.y-5,self.x+5,self.y+5,fill="Green")
def haversine_distance(p1,p2):
    ##Finds the distance between two objects using their latitude and longitude
    ##Returns distance in km
    earth_radius = 6371000
    a = math.sin((p1.lat-p2.lat)/2)*math.sin((p1.lat-p2.lat)/2)+math.cos(p1.lat)*math.cos(p2.lat)*math.sin((p1.lng-p2.lng)/2)*math.sin((p1.lng-p2.lng)/2)
    c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    d = earth_radius*c
    d = d/1000
    return d
def stringify_children(node):
    from lxml.etree import tostring
    from itertools import chain
    parts = ([node.text] +
            list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
            [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))
weather_map = Map()
cloud_keys = ['SKC','FEW','SCT','BKN','OVC','NSC','CLR']
cloud_colors = {'SKC':'#ffffff','FEW':'#bfbfbf','SCT':'#808080','BKN':'#404040','OVC':'#0f0f0f','NSC':'#ffffff','CLR':'#ffffff'}
weather_stations = {"nashville_TN":Weather_station("nashville_TN",weather_map,36.1263,-86.6774,72327,'n'),"littleRock_AR":Weather_station("littleRock_AR",weather_map,34.7307,-92.2217,72340,'n'),"jackson_MS":Weather_station("jackson_MS",weather_map,32.3122,-90.0764,72235,'n'),"birmingham_AL":Weather_station("birmingham_AL",weather_map,33.5624,-86.7541,72230,'n'),"springfield_MO":Weather_station("springfield_MO",weather_map,37.2443,-93.3888,72440,'n'),"lincoln_IL":Weather_station("lincoln_IL",weather_map,40.0902,-89.2013,74560,'n'),"shreveport_LA":Weather_station("shreveport_LA",weather_map,32.4548,-93.8284,72248,'n'),"topeka_KS":Weather_station("topeka_KS",weather_map,39.0699,-95.6221,72456,'n'),"oklahomaCity_OK":Weather_station("oklahomaCity_OK",weather_map,35.2455556,-97.4721389,72357,'n'),"fortWorth_TX":Weather_station("fortWorth_TX",weather_map,32.8998,-97.0403,72249,'n'),"dodgeCity_KS":Weather_station("dodgeCity_KS",weather_map,37.7607, -99.9643,72451,'n'),"omaha_NE":Weather_station("omaha_NE",weather_map,41.3203,-96.3664,72558,'n'),"platte_NE":Weather_station("platte_NE",weather_map,41.1354,-100.7013,72562,'h'),"davenport_IA":Weather_station("davenport_IA",weather_map,41.6101, -90.5879,74455,'n'),"amarillo_TX":Weather_station("amarillo_TX",weather_map,35.2203,-101.7075,72363,'h'),"midland_TX":Weather_station("midland_TX",weather_map,31.9417,-102.2047,72265,'h'),"wilmington_OH":Weather_station("wilmington_OH",weather_map,39.4320,-83.7857,72426,'n'),"atlanta_GA":Weather_station("atlanta_GA",weather_map,33.3591,-84.2319,72215,'n'),"denver_CO":Weather_station("denver_CO",weather_map,39.8561,-104.6737,72469,'h')}
union = Report_area("Union University",weather_map,35.6774,-88.8596)
links_library = open('Links for data by station.txt')
links_library = links_library.read()
links_by_city = links_library.split('|')
links_dictionary = {}
for section in links_by_city:
    city = section.split('=')[0]
    link = section.split('=')[1]
    links_dictionary[city] = link
for city,station in weather_stations.items():
    station.data_link = links_dictionary[city]
    ##station.update_observations()
def parse_cloud_data(raw_data):
    for line in raw_data:
        this_line = str(line.decode("utf-8")).split(' ')
        for w in this_line:
            for keyword in cloud_keys:
                this_section = w.partition(keyword)
                if this_section[1]!='':
                    return keyword
def predict_distance(w_speed,hours):
    distance = (w_speed*1.85*hours)
    return distance
def mean_trimmed_data(meters,array):
    count=0
    mean = 0
    for item in meters:
        ##We are taking only data from 860 to 304 millibars
        ## or 1600 - 9700 meters
        if float(item) < 9700 and float(item) > 1600:
            mean+=float(array[meters.index(item)])
            count+=1
    ##print("Mean = "+str(mean))
    ##print("Count = "+str(count))
    return (mean/count)
for name,station in weather_stations.items():
    station.update_observations()
##weather_stations["midland_TX"].update_observations()
weather_map.tk.mainloop()

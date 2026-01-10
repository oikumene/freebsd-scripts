#! /usr/local/bin/python3

import datetime
import io
import json
import pathlib
import traceback

import requests

amedas_point_list = "amedastable.json"
amedas_points = ["東京", "札幌", "那覇"]

def get_amedas_point_code(aplist):
    rdata = {}
    with io.open("amedastable.json", "r", encoding="UTF-8") as fp:
        apdata = json.load(fp)
    for code in apdata:
        for name in aplist:
            if apdata[code]["kjName"] == name:
                rdata[name] = code
    return rdata

def generate_amedas_data_current_hour_uri():
    tzoffset = datetime.timedelta(hours=9)
    tz = datetime.timezone(tzoffset, name="jp")
    dtnow = datetime.datetime.now(tz)
    datafilename = f"{dtnow.year:04}{dtnow.month:02}{dtnow.day:02}{dtnow.hour:02}0000.json"
    uri = "https://www.jma.go.jp/bosai/amedas/data/map/" + datafilename
    return uri

def generate_weather_json(filename, uri, apdic):
    weather = {}
    olddata = {}
    tplist = []
    num_split = 6
    filepath = pathlib.Path(filename)
    if filepath.exists():
        with io.open(filepath, "r", encoding="UTF-8") as fp:
            weather = json.load(fp)
    else:
        weather["text"] = ""
        weather["tooltip"] = ""
        weather["class"] = "custom-weather"
    r = requests.get(uri)
    amedas_data = r.json()

    # 旧データをまず思い出す
    for line in weather["tooltip"].split("\r"):
        for point in amedas_points:
            if point in line:
                olddata[point] = line.split(' ')

    for point in amedas_points:
        has_olddata = point in olddata and len(olddata[point]) == num_split
        newdata = amedas_data[apdic[point]]

        # 温度
        tempstr = newdata["temp"][0]
        if tempstr is not None:
            tempstr = f"{tempstr:.1f}°Ｃ"
        elif has_olddata:
            tempstr = olddata[point][2]
        else:
            tempstr = "--°Ｃ"

        # 湿度
        humstr = newdata["humidity"][0]
        if humstr is not None:
            humstr = f"{humstr}%"
        elif has_olddata:
            humstr = olddata[point][3]
        else:
            humstr = "--%"

        # 風速
        windstr = newdata["wind"][0]
        if windstr is not None:
            windstr = f"{windstr:.1f}m/s"
        elif has_olddata:
            windstr = olddata[point][4]
        else:
            windstr = "--m/s"

        # 雨量
        precstr = newdata["precipitation1h"][0]
        if precstr is not None:
            precstr = f"{precstr:.1f}mm"
        elif has_olddata:
            precstr = olddata[point][5]
        else:
            precstr = "--mm"

        # 天気
        if has_olddata:
            weatherchar = olddata[point][0]
        else:
            weatherchar = "--"
        sun1h = newdata["sun1h"][0]
        snow1h = newdata["snow1h"][0]
        prec1h = newdata["precipitation1h"][0]
        if snow1h is not None and snow1h > 0.0:
            weatherchar = "☃️"
        elif prec1h is not None and prec1h > 0.0:
            weatherchar = "☔️"
        elif sun1h is not None and sun1h == 0.0:
            weatherchar = "☁️"
        elif sun1h is not None and sun1h > 0.0:
            weatherchar = "☀️"

        tplist.append(f"{point}: {weatherchar} {tempstr} {humstr} {windstr} {precstr}")
        if point == amedas_points[0]:
            weather["text"] = f"{point}: {weatherchar} {tempstr}"
    weather["tooltip"] = "\r".join(tplist)

    with io.open(filename, "w", encoding="UTF-8") as fp:
        json.dump(weather, fp, ensure_ascii=False)

def generate_weather():
    try:
        ap = get_amedas_point_code(amedas_points)
        amedas_data_uri = generate_amedas_data_current_hour_uri()
        generate_weather_json("weather.json", amedas_data_uri, ap)
    except Exception as e:
        print("fetching weather data failed:", str(e))
        print()
        traceback.print_exc()

if __name__ == "__main__":
    generate_weather()

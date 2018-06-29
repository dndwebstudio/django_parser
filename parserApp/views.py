from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from avtoportal.models import CarPropertyMark, CarPropertyModel, CarPropertyGen, CarBody, Car
from authApp.models import Country, Region, City
from statisticsApp.models import StatisticsCars
import csv
import hashlib
import datetime

def auto():
    # if not request.user.is_superuser:
    #     return redirect('/auth/')
    # else:
        with open('static/parser_files/auto/car_mark.csv', newline='') as csvfile:
            mark_read = csv.reader(csvfile, delimiter=',', quotechar='\'')
            mark_list = {}
            for ind, row in enumerate(mark_read):
                if int(ind) > 0:
                    mark_list[str(row[0])+"_car_mark"] = {"id": row[0], "name": row[1]}
                    mark_list[str(row[0]) + "_car_mark"]['hash'] = hashlib.sha1(row[1].encode('utf-8')).hexdigest()

        with open('static/parser_files/auto/car_model.csv', newline='') as csvfile:
            model_read = csv.reader(csvfile, delimiter=',', quotechar='\'')
            model_list = {}
            for ind, row in enumerate(model_read):
                if int(ind) > 0:
                    model_list[str(row[0]) + "_car_model"] = {"id": row[0], "mark": row[1], "name": row[2]}
                    mark_obj = mark_list[str(model_list[str(row[0]) + "_car_model"]['mark']) + "_car_mark"]
                    prehash = mark_obj['hash']+model_list[str(row[0]) + "_car_model"]['name']
                    model_list[str(row[0]) + "_car_model"]['hash'] = hashlib.sha1(prehash.encode('utf-8')).hexdigest()

        with open('static/parser_files/auto/car_generation.csv', newline='') as csvfile:
            gen_read = csv.reader(csvfile, delimiter=',', quotechar='\'')
            gen_list = {}
            for ind, row in enumerate(gen_read):
                if int(ind) > 0:
                    if not row[4] or row[4] == 'NULL':
                        now = datetime.datetime.now()
                        row[4] = str(now.year)
                    if not row[3] or row[3] == 'NULL':
                        row[3] = 1890
                    gen_list[str(row[0]) + "_car_generation"] = {"id": row[0], "model": row[2], "name": row[1], "year_begin": row[3], "year_end": row[4]}
                    model_obj = model_list[str(gen_list[str(row[0]) + "_car_generation"]['model']) + "_car_model"]
                    prehash = model_obj['hash']+gen_list[str(row[0]) + "_car_generation"]['name']
                    gen_list[str(row[0]) + "_car_generation"]['hash'] = hashlib.sha1(prehash.encode('utf-8')).hexdigest()

        for ind, elem in mark_list.items():
            try:
                mark = CarPropertyMark.objects.get(hash_sum=elem['hash'])
            except:
                mark = None
            if mark is not None:
                mark_list[ind]['id_elem'] = mark
            else:
                mark = CarPropertyMark.objects.create(hash_sum=elem['hash'], title=elem['name'])
                mark.save()
                mark_list[ind]['id_elem'] = mark

        for ind, elem in model_list.items():
            try:
                model = CarPropertyModel.objects.get(hash_sum=elem['hash'])
            except:
                model = None

            if model is not None:
                model_list[ind]['id_elem'] = model
            else:
                model = CarPropertyModel.objects.create(hash_sum=elem['hash'], title=elem['name'], mark=mark_list[str(elem['mark'])+"_car_mark"]['id_elem'])
                model.save()
                model_list[ind]['id_elem'] = model

        for ind, elem in gen_list.items():
            try:
                gen = CarPropertyGen.objects.get(hash_sum=elem['hash'])
            except:
                gen = None

            if gen is not None:
                gen.year_end = int(elem['year_end'])
                gen.save()
                gen_list[ind]['id_elem'] = gen
            else:
                print(elem)
                gen = CarPropertyGen.objects.create(hash_sum=elem['hash'], title=elem['name'],
                                                    model=model_list[str(elem['model']) + "_car_model"]['id_elem'],
                                                    year_begin=int(elem['year_begin']), year_end=int(elem['year_end']))
                gen.save()
                gen_list[ind]['id_elem'] = gen
def deleteAuto():
    try:
        gen = CarPropertyGen.objects.filter()
    except:
        gen = None

    if gen is not None:
        for gen_item in gen:
            gen_item.delete()
    try:
        model = CarPropertyModel.objects.filter()
    except:
        model = None

    if model is not None:
        for model_item in model:
            model_item.delete()
    try:
        mark = CarPropertyMark.objects.filter()
    except:
        mark = None

    if mark is not None:
        for mark_item in mark:
            mark_item.delete()

def city():
    with open('static/parser_files/city/countries.csv', newline='') as csvfile:
        country_read = csv.reader(csvfile, delimiter=',', quotechar='\'')
        country_list = {}
        for ind, row in enumerate(country_read):
            if int(ind) > 0:
                row[2] = row[2].strip()
                country_list[str(row[1])+"_country"] = {"id": row[1], "name": row[2], "currency_code": row[0], "currency": row[3]}
                country_list[str(row[1]) + "_country"]['hash'] = hashlib.sha1(row[2].encode('utf-8')).hexdigest()

    with open('static/parser_files/city/city.csv', newline='') as csvfile:
        city_read = csv.reader(csvfile, delimiter=',', quotechar='\'')
        region_list = {}
        for ind, row in enumerate(city_read):
            if int(ind) > 0:
                row[0] = row[0].strip()
                if not row[0] or row[0] is None or row[0] == "" or row[0] == " ":
                    row[0] = "Другие"

                pre_name = row[0]+str(row[1])
                name_hash = hashlib.sha1(pre_name.encode('utf-8')).hexdigest()
                region_list[str(name_hash)+"_region"] = {"id": name_hash, "name": row[0], 'country': row[1]}
                prehash = country_list[str(row[1])+"_country"]['hash']+region_list[str(name_hash)+"_region"]['name']
                region_list[str(name_hash) + "_region"]['hash'] = hashlib.sha1(prehash.encode('utf-8')).hexdigest()
    with open('static/parser_files/city/city.csv', newline='') as csvfile:
        city_read = csv.reader(csvfile, delimiter=',', quotechar='\'')
        city_list = {}
        for ind, row in enumerate(city_read):
            if int(ind) > 0:
                row[0] = row[0].strip()
                row[4] = row[4].strip()
                if not row[0] or row[0] is None or row[0] == "" or row[0] == " ":
                    row[0] = "Другие"
                pre_name = row[0]+str(row[1])
                region_hash = hashlib.sha1(pre_name.encode('utf-8')).hexdigest()
                city_list[str(row[2]) + "_city"] = {"id": row[2], "name": row[4], 'is_big': row[3], 'country': row[1], 'region': region_hash}
                prehash = country_list[str(row[1]) + "_country"]['hash'] + region_list[str(region_hash) + "_region"]['hash'] + city_list[str(row[2]) + "_city"]['name']
                city_list[str(row[2]) + "_city"]['hash'] = hashlib.sha1(prehash.encode('utf-8')).hexdigest()

    for ind, elem in country_list.items():
        try:
            country = Country.objects.get(hash_sum=elem['hash'])
        except:
            country = None

        if country is not None:
            country_list[ind]['id_elem'] = country
        else:
            country = Country.objects.create(hash_sum=elem['hash'], name=elem['name'],
                                             currency_code=elem['currency_code'],
                                             currency=elem['currency'])
            country.save()
            country_list[ind]['id_elem'] = country

    for ind, elem in region_list.items():
        try:
            region = Region.objects.get(hash_sum=elem['hash'])
        except:
            region = None

        if region is not None:
            region_list[ind]['id_elem'] = region
        else:
            region = Region.objects.create(hash_sum=elem['hash'], name=elem['name'],
                                            country=country_list[str(elem['country']) + "_country"]['id_elem'])
            region.save()
            region_list[ind]['id_elem'] = region

    for ind, elem in city_list.items():
        try:
            city = City.objects.get(hash_sum=elem['hash'])
        except:
            city = None

        if city is not None:
            city_list[ind]['id_elem'] = city
        else:
            print(elem)
            big = False
            if elem['is_big'] == 1:
                big = True
            city = City.objects.create(hash_sum=elem['hash'], name=elem['name'],
                                       country=country_list[str(elem['country']) + "_country"]['id_elem'],
                                       region=region_list[str(elem['region']) + "_region"]['id_elem'],
                                       biggest_city=big)
            city.save()
            city_list[ind]['id_elem'] = city

def deletCity():
    try:
        country = Country.objects.filter()
    except:
        country = None

    if country is not None:
        for country_item in country:
            country_item.delete()
    try:
        reg = Region.objects.filter()
    except:
        reg = None

    if reg is not None:
        for reg_item in reg:
            reg_item.delete()
    try:
        city = City.objects.filter()
    except:
        city = None

    if city is not None:
        for city_item in city:
            city_item.delete()


def changeBodyType(bodyType):
    returnData = {"type": bodyType, "name": None, "obj": None}
    if bodyType == "sedan":
        returnData['name'] = "Седан"
    elif bodyType == "wagon":
        returnData['name'] = "Универсал"
    elif bodyType == "3dr hb":
        returnData['name'] = "Хэтчбек 3 дв."
    elif bodyType == "5dr hb":
        returnData['name'] = "Хэтчбек 5 дв."
    elif bodyType == "coupe":
        returnData['name'] = "Купе"
    elif bodyType == "5d coupe":
        returnData['name'] = "Купе"
    elif bodyType == "cabriolet":
        returnData['name'] = "Кабриолет"
    elif bodyType == "hi roof blind van":
        returnData['name'] = "Фургон"
    elif bodyType == "2d coupe":
        returnData['name'] = "Купе"
    elif bodyType == "pickup":
        returnData['name'] = "Пикап"
    elif bodyType == "pickup":
        returnData['name'] = "Пикап"

    if returnData['name'] is not None:
        try:
            get_body = CarBody.objects.get(title=returnData['name'])
        except:
            get_body = None

        if get_body is not None:
            returnData['obj'] = get_body

    return returnData

def getMarkAndModel(mark, model):
    returnData = {"markName": mark, "modelName": model, "mark": None, "model": None}
    if mark.lower() == "ваз":
        returnData['markName'] = 'ВАЗ (Lada)'
    elif mark.lower() == "landrover":
        returnData['markName'] = 'land rover'
    elif mark.lower() == "chevrolet-dat":
        returnData['markName'] = 'chevrolet'
    elif mark.lower() == "ssang yong":
        returnData['markName'] = 'ssangyong'
    elif mark.lower() == "tagaz":
        returnData['markName'] = 'тагаз'

    try:
        get_mark = CarPropertyMark.objects.get(title__iexact=returnData['markName'].strip())
    except:
        get_mark = None

    if get_mark is not None:
        returnData['mark'] = get_mark
        try:
            get_model = CarPropertyModel.objects.get(title__iexact=returnData['modelName'].strip(), mark=get_mark)
        except:
            get_model = None

        if get_model is not None:
            returnData['model'] = get_model
    return returnData

def getGearBox(gb):
    result = None
    if gb == "MT":
        result = "MK"
    elif gb == "AT":
        result = "AK"
    elif gb == "CVT":
        result = "VR"
    elif gb == "MTA":
        result = "RK"

    return result

def getDVSID(dvs):
    dvs_str = str(dvs).replace(",", ".")
    for ind, num in enumerate(range(0, 101)):
        formatNum = "{:3.1f}".format((float(num)*0.1))
        if str(formatNum) == str(dvs_str):
            return str(ind)
    return "22"

def statics():
    with open('static/parser_files/statics/star.csv', newline='') as csvfile:
        car_read = csv.reader(csvfile, delimiter=';', quotechar='"')
        car_list = []
        for ind, row in enumerate(car_read):
            car_items = {'date_sell': None}
            if int(ind) > 0:
                try:
                    car_items['drive'] = row[2]
                    car_items['date_sell'] = row[1]
                    car_items['vin'] = row[3]
                    car_items['mark'] = row[4]
                    car_items['model'] = row[5]
                    car_items['mod'] = row[6]
                    car_items['year'] = row[8]
                    car_items['volume'] = row[9]
                    car_items['horsepower'] = row[10]
                    car_items['gear'] = row[11]
                    car_items['body'] = row[12]
                    car_items['mileage'] = row[13]
                    car_items['price'] = row[14]
                    car_items['color'] = row[15]
                    car_items['dealer'] = row[18]
                    car_list.append(car_items)
                except:
                    print("ошибка")
        # countCar = 0
        for ind, car in enumerate(car_list):
            get_body_type = changeBodyType(car['body'].lower())
            if get_body_type['name'] is None:
                del car_list[ind]
            else:
                if get_body_type['obj'] is None:
                    del car_list[ind]
                else:
                    get_model_and_mark = getMarkAndModel(car['mark'], car['model'])
                    if get_model_and_mark['mark'] is None or get_model_and_mark['model'] is None:
                        # countCar += 1
                        del car_list[ind]
                    else:
                        get_gb = getGearBox(car['gear'])
                        if get_gb is None:
                            del car_list[ind]
                        else:
                            try:
                                get_user = User.objects.get(username="fake_dealer")
                            except:
                                get_user = None

                            if get_user is not None:
                                carTitle = "%s %s" % (get_model_and_mark['mark'].title, get_model_and_mark['model'].title)
                                createCar = Car.objects.create(title=carTitle,
                                                               code="fake_car_for_stat",
                                                               mark=get_model_and_mark['mark'],
                                                               model=get_model_and_mark['model'],
                                                               author=get_user,
                                                               year=int(car['year']),
                                                               year_reg=int(car['year']),
                                                               horses_power=int(car['horsepower']),
                                                               mileage=int(car['mileage']),
                                                               price=int(car['price']),
                                                               ads_drop=True,
                                                               ads_stopped=True,
                                                               engine="BN",
                                                               dvs=getDVSID(str(car['volume'])),
                                                               drive_type="FL",
                                                               transmission=get_gb,
                                                               gear_count="3",
                                                               pts="OR",
                                                               owner_count="ONE",
                                                               state="NT",
                                                               door_count="4",
                                                               sts="11 11 № 111111",
                                                               address="sf",
                                                               price_guarantee=10000,
                                                               diagnostic="sgsdg",
                                                               description_car="sgsdg",
                                                               rpa="N",
                                                               vin=car['vin'].lower())

                                createCar.save()

                                dateDayFromStr = "%s 06:00:00" % car['date_sell']
                                now = datetime.datetime.strptime(dateDayFromStr, '%d.%m.%Y %H:%M:%S')

                                staticCode = "statics___for___%s___%s___%s" % (now.day, now.month, now.year)

                                try:
                                    get_stat = StatisticsCars.objects.get(code=staticCode)
                                except:
                                    get_stat = None

                                if get_stat is not None:
                                    get_stat.car.add(createCar)
                                    get_stat.save()
                                else:
                                    get_stat = StatisticsCars.objects.create(code=staticCode,
                                                                             date_create=now,
                                                                             datetime_create=now)
                                    get_stat.car.add(createCar)
                                    get_stat.save()
                                    get_stat.date_create = now
                                    get_stat.datetime_create = now
                                    get_stat.save()
                                print(get_stat.date_create)
                                print(get_stat.datetime_create)
                                # break
        # print(countCar)


# deletCity()
# city()
# deleteAuto()
# auto()
# statics()

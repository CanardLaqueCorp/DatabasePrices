import csv
import os
from datetime import datetime

carsDb = []
allCars = []
newCars = []
oldCars = []

scriptCarPrices = ""

def findCar(brand, model):
    res = []
    # We look for the exact car
    for car in allCars:
        if (car['brand'].lower() == brand.lower()) and (car['model'].lower() == model.lower()):
            res.append(car)
    # if no cars were found, we look for cars that contain the brand and model
    if (len(res) == 0):
        for car in allCars :
            if (car['brand'].lower() in brand.lower() or brand.lower() in car['brand'].lower()) and (car['model'].lower() in model.lower() or model.lower() in car['model'].lower()):
                res.append(car)
    return res

def getAvgData(brand, model) :
    res = findCar(brand, model)
    if (len(res) == 0):
        return None
    avgPrice = 0
    avgPriceEuro = 0
    avgMileage = 0
    for car in res:
        avgPrice += float(car['price'])
        avgPriceEuro += float(car['priceEuro']) 
        avgMileage += float(car['mileage'])
    avgPrice /= len(res)
    avgPriceEuro /= len(res)
    avgMileage /= len(res)
    return {
        'avgPrice': round(avgPrice),
        'avgPriceEuro': round(avgPriceEuro),
        'avgMileage': round(avgMileage),
        'cars' : res
    }

with open('data/data2023.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)

    id = 1
    for line in csv_reader:
        line = line[0].split(';')

        car = {
            'id': id,
            'brand': line[2],
            'model': line[3],
            'avgPrice': 0,
        }

        carsDb.append(car)
        id += 1

with open('data/prices.csv', 'r', encoding="utf8") as csv_file:
    csv_reader = csv.reader(csv_file)

    for line in csv_reader:
        # ignore first line
        if (line[0] == 'ID'):
            continue

        mileage = line[10].replace(' km', '')

        # convert price to euro
        
        # $
        price = line[1]

        # €
        priceEuro = str(round(float(price) * 0.95, 0))

        carPrice = {
            'brand': line[3],
            'model': line[4],
            'year': line[5],
            'price': price,
            'priceEuro': priceEuro,
            'mileage': mileage,
        }

        allCars.append(carPrice)

        if (float(mileage) <= 20):
            newCars.append(carPrice)
        else:
            oldCars.append(carPrice)

for car in carsDb:
    avgData = getAvgData(car['brand'], car['model'])
    if (avgData == None):
        continue
    car['avgPrice'] = avgData['avgPrice']
    car['avgPriceEuro'] = avgData['avgPriceEuro']
    car['avgMileage'] = avgData['avgMileage']

    for carPrice in avgData['cars']:
        scriptCarPrices += "INSERT INTO car_price (car_id, price, price_euro, mileage, year) VALUES (" + str(car['id']) + ", " + carPrice['price'] + ", " + carPrice['priceEuro'] + ", " + carPrice['mileage'] + ", " + carPrice['year'] + ");\n"


# move the files from the "exports" directory to the "old_exports" directory

for file in os.listdir('exports'):
    os.rename('exports/' + file, 'old_exports/' + file)

# We create the sql script fro the cars_th table

script = ""
for car in carsDb :
    if (car['avgPrice'] != 0):
        script += "UPDATE car_th SET price_used = " + str(car['avgPrice']) + " price_used_euro = " + str(car['avgPriceEuro']) + " WHERE id = " + str(car['id']) + ";\n"

# We create the file

now = datetime.now()
fileName = "carsTH-price-" + now.strftime("%d%m%Y%H%M%S") + ".sql"
file = open('exports/' + fileName, 'w')
file.write(script)
file.close()

# We create the sql script for the car_price table

now = datetime.now()
fileName = "old-carsTH" + now.strftime("%d%m%Y%H%M%S") + ".sql"
file = open('exports/' + fileName, 'w')
file.write(scriptCarPrices)
file.close()

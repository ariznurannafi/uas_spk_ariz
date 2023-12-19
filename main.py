from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api
from models import Smartphone as SmartphoneModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from tabulate import tabulate

session = Session(engine)

app = Flask(__name__)
api = Api(app)


class BaseMethod():

    def __init__(self):
        self.raw_weight = {'merek': 4, 'sistem_operasi': 3, 'baterai': 4,
                            'ram': 4, 'memori_internal': 5, 'harga': 5, 'ukuran_layar':3}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(SmartphoneModel.id, SmartphoneModel.merek, SmartphoneModel.sistem_operasi, SmartphoneModel.baterai,
                       SmartphoneModel.ram, SmartphoneModel.memori_internal, SmartphoneModel.harga, SmartphoneModel.ukuran_layar)
        result = session.execute(query).fetchall()
        print(result)
        return [{'id': Smartphone.id,'merek': Smartphone.merek, 'sistem_operasi': Smartphone.sistem_operasi,
                'baterai': Smartphone.baterai, 'ram': Smartphone.ram, 'memori_internal': Smartphone.memori_internal, 'harga': Smartphone.harga, 'ukuran_layar': Smartphone.ukuran_layar} for Smartphone in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        ukuran_layar_values = []  # max
        baterai_values = []  # max
        ram_values = []  # max
        memori_internal_values = []  # max
        harga_values = []  # min
        sistem_operasi_values = [] #max

        for data in self.data:
            # ukuran layar
            ukuran_layar_spec = data['ukuran_layar']
            numeric_values = [int(value.split()[0]) for value in ukuran_layar_spec.split(
                ',') if value.split()[0].isdigit()]
            max_ukuran_layar_value = max(numeric_values) if numeric_values else 1
            ukuran_layar_values.append(max_ukuran_layar_value)

            # sisem operasi
            sistem_operasi_spec = data['sistem_operasi']
            numeric_values = [int(value.split()[0]) for value in sistem_operasi_spec.split(
                ',') if value.split()[0].isdigit()]
            max_sistem_operasi_value = max(numeric_values) if numeric_values else 1
            sistem_operasi_values.append(max_sistem_operasi_value)

            # Baterai
            baterai_spec = data['baterai']
            baterai_numeric_values = [int(
                value.split()[0]) for value in baterai_spec.split() if value.split()[0].isdigit()]
            max_baterai_value = max(
                baterai_numeric_values) if baterai_numeric_values else 1
            baterai_values.append(max_baterai_value)

            # RAM
            ram_spec = data['ram']
            ram_numeric_values = [
                int(value) for value in ram_spec.split() if value.isdigit()]
            max_ram_value = max(
                ram_numeric_values) if ram_numeric_values else 1
            ram_values.append(max_ram_value)

           # Memori
            memori_internal_spec = data['memori_internal']
            memori_internal_numeric_values = [
            int(value) for value in memori_internal_spec.split() if value.isdigit()]
            max_memori_internal_value = max(
            memori_internal_numeric_values) if memori_internal_numeric_values else 1
            memori_internal_values.append(max_memori_internal_value)


       # Harga
            harga_cleaned = ''.join(
            char for char in str(data['harga']) if char.isdigit())
            harga_values.append(float(harga_cleaned) if harga_cleaned else 0)  # Convert to float

        return [
    {
            'id': data['id'],
            'merek': data['merek'],
            'sistem_operasi': sistem_operasi_value / max(sistem_operasi_values),
            'ukuran_layar': ukuran_layar_value / max(ukuran_layar_values),
            'baterai': baterai_value / max(baterai_values),
            'ram': ram_value / max(ram_values),
            'memori_internal': memori_internal_value / max(memori_internal_values),
            # To avoid division by zero
            'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0
             
    }
    for data,sistem_operasi_value, baterai_value, ram_value, memori_internal_value, ukuran_layar_value, harga_value
            in zip(self.data, sistem_operasi_values, baterai_values, ram_values, memori_internal_values, ukuran_layar_values, harga_values)
]


    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'id': row['id'],
                'merek': row['merek'],
                'produk': 
                row['ukuran_layar']**self.weight['ukuran_layar'] *
                row['baterai']**self.weight['baterai'] *
                row['ram']**self.weight['ram'] *
                row['memori_internal']**self.weight['memori_internal'] *
                row['sistem_operasi']**self.weight['sistem_operasi'] *
                row['harga']**self.weight['harga']
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'ID': product['id'],
                'score': round(product['produk'], 3)
            }
            for product in sorted_produk
        ]
        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'smartphone': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value


class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'ID': row['id'],
                'Score': round(row['ukuran_layar'] * weight['ukuran_layar'] +
                        row['baterai'] * weight['baterai'] +
                        row['ram'] * weight['ram'] +
                        row['memori_internal'] * weight['memori_internal'] +
                        row['sistem_operasi'] * weight['sistem_operasi'] +
                        row['harga'] * weight['harga'], 2)
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x['Score'], reverse=True)
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'smartphone': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value


class Smartphone(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Data Tidak Ditemukan.')
        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = session.query(SmartphoneModel).order_by(SmartphoneModel.id)
        result_set = query.all()
        data = [{'id': row.id, 'ukuran_layar': row.ukuran_layar, 'baterai': row.baterai,
                 'ram': row.ram, 'memori_internal': row.memori_internal, 'sistem_operasi': row.sistem_operasi, 'harga': row.harga}
                for row in result_set]
        return self.get_paginated_result('smartphone/', data, request.args), 200


api.add_resource(Smartphone, '/smartphone')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)
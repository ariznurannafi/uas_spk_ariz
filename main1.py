import sys
from colorama import Fore, Style
from models import Base, Smartphone
from engine import engine
from tabulate import tabulate

from sqlalchemy import select
from sqlalchemy.orm import Session
from settings import DEV_SCALE

session = Session(engine)


def create_table():
    Base.metadata.create_all(engine)
    print(f'{Fore.GREEN}[Success]: {Style.RESET_ALL}Database has created!')


def review_data():
    query = select(Smartphone)
    for phone in session.scalars(query):
        print(phone)


class BaseMethod():

    def __init__(self):
        # 1-5
        self.raw_weight = {'sistem_operasi': 3, 'baterai': 4,
                            'ram': 4, 'memori_internal': 5, 'harga': 5, 'ukuran_layar':3}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(Smartphone.id, Smartphone.merek, Smartphone.sistem_operasi, Smartphone.baterai,
                       Smartphone.ram, Smartphone.memori_internal, Smartphone.harga, Smartphone.ukuran_layar)
        result = session.execute(query).fetchall()
        return [{'id': phone.id, 'merek': phone.merek, 'sistem_operasi': phone.sistem_operasi, 'baterai': phone.baterai,
                 'ram': phone.ram, 'memori_internal': phone.memori_internal, 'harga': phone.harga, 'ukuran_layar': phone.ukuran_layar} for phone in result]

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
            {'id': data['id'],
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


class WeightedProduct(BaseMethod):
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
                'id': product['id'],
                'merek': product['merek'],
                'ukuran_layar': product['produk'] / self.weight['ukuran_layar'],
                'baterai': product['produk'] / self.weight['baterai'],
                'ram': product['produk'] / self.weight['ram'],
                'memori_internal': product['produk'] / self.weight['memori_internal'],
                'sistem_operasi': product['produk'] / self.weight['sistem_operasi'],
                'harga': product['produk'] / self.weight['harga'],
                'score': product['produk']  # Nilai skor akhir
            }
            for product in sorted_produk
        ]
        return sorted_data


class SimpleAdditiveWeighting(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = {row['id']:
                  round(row['ukuran_layar'] * weight['ukuran_layar'] +
                        row['baterai'] * weight['baterai'] +
                        row['ram'] * weight['ram'] +
                        row['memori_internal'] * weight['memori_internal'] +
                        row['sistem_operasi'] * weight['sistem_operasi'] +
                        row['harga'] * weight['harga'], 2)
                  for row in self.normalized_data
                  }
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1], reverse=True))
        return sorted_result


def run_saw():
    saw = SimpleAdditiveWeighting()
    result = saw.calculate
    print(tabulate(result.items(), headers=['Id','merek', 'Score'], tablefmt='pretty'))


def run_wp():
    wp = WeightedProduct()
    result = wp.calculate
    headers = result[0].keys()
    rows = [
        {k: round(v, 4) if isinstance(v, float) else v for k, v in val.items()}
        for val in result
    ]
    print(tabulate(rows, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == 'create_table':
            create_table()
        elif arg == 'saw':
            run_saw()
        elif arg == 'wp':
            run_wp()
        else:
            print('command not found')

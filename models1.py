from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Smartphone(Base):
    __tablename__ = "hp"
    id = Column(Integer, primary_key=True)
    merek = Column(String(255))
    ram = Column(String(255))
    sistem_operasi = Column(String(255))
    baterai = Column(String(255))
    ukuran_layar = Column(String(255))
    memori_internal = Column(String(255))
    harga = Column(Integer)

    def __init__(self,id, merek, ram, sistem_operasi, baterai, ukuran_layar, memori_internal, harga):
        self.id = id
        self.merek = merek
        self.ram = ram
        self.sistem_operasi = sistem_operasi
        self.baterai = baterai
        self.ukuran_layar = ukuran_layar
        self.memori_internal = memori_internal
        self.harga = harga

    def calculate_score(self, dev_scale):
        score = 0
        score += self.merek * dev_scale['merek']
        score += self.ram * dev_scale['ram']
        score += self.sistem_operasi * dev_scale['sistem_operasi']
        score += self.baterai * dev_scale['baterai']
        score += self.ukuran_layar * dev_scale['ukuran_layar']
        score += self.memori_internal * dev_scale['memori_internal']
        score -= self.harga * dev_scale['harga']
        return score

    def __repr__(self):
        return f"Smartphone(id={self.id!r}, merek={self.merek!r}, ram={self.ram!r}, sistem_operasi={self.sistem_operasi!r}, baterai={self.baterai!r}, ukuran_layar={self.ukuran_layar!r}, memori_internal={self.memori_internal!r}, harga={self.harga!r})"
 
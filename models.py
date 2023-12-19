from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Smartphone(Base):
    __tablename__ = "hp"
    id = Column(Integer, primary_key=True)
    merek = Column(String)
    sistem_operasi = Column(String)
    baterai = Column(Integer)
    ram = Column(String)
    memori_internal = Column(String)
    ukuran_layar = Column(String) 
    harga = Column(String) 
    
    def _repr_(self):
        return f"Smartphone(merek={self.merek!r}, sistem_operasi={self.sistem_operasi!r}, baterai={self.baterai!r}, ram={self.ram!r}, memori_internal={self.memori_internal!r}, harga={self.harga!r}, ukuran_layar={self.ukuran_layar!r}, benefit={self.benefit!r})"
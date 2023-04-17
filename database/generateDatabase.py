import random
import csv
from faker import Faker

fake = Faker()

# Función para generar una ciudad aleatoria
def generar_ciudad():
    return fake.city()

# Función para generar una edad aleatoria
def generar_edad():
    return random.randint(18, 80)

# Función para generar un sexo aleatorio
def generar_sexo():
    return random.choice(['M', 'F'])

# Función para generar un trabajo aleatorio
def generar_trabajo():
    return fake.job()

# Función para generar un correo electrónico aleatorio
def generar_correo(id, nombre):
    proveedor = fake.free_email_domain()
    return f"{nombre.replace(' ', '.').lower()}{id % 1000}@{proveedor}"

# Generar los datos aleatorios y escribirlos en el archivo CSV
with open("datos.csv", "w", newline="") as archivo:
    escritor_csv = csv.writer(archivo)
    escritor_csv.writerow(["id", "nombre", "email", "edad", "sexo", "ciudad", "trabajo"])
    for i in range(1000):
        id = random.randint(0, 99999)
        nombre = fake.name()
        correo = generar_correo(id, nombre)
        edad = generar_edad()
        sexo = generar_sexo()
        ciudad = generar_ciudad()
        trabajo = generar_trabajo()
        escritor_csv.writerow([id, nombre, correo, edad, sexo, ciudad, trabajo])

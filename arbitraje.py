import pandas as pd
import csv
from pycoingecko import CoinGeckoAPI

# Crear una instancia de CoinGeckoAPI
cg = CoinGeckoAPI()
monedas = ["algorand", "iota", "litecoin", "ripple", "stellar"]
exchanges_restringidos = ["Binance US","Otro Exchange restringido"]
redes_inhabilitadas = {"iota":["Gate.io", "KuCoin"]}

data = {}
gaps = {}
mined = []

# Obtener los datos del ticker 
for moneda in monedas:
    ticker = cg.get_coin_ticker_by_id(id=moneda, per_page=200)
    exchanges = ticker['tickers']
    exchange_data = []
    exchanges_prohibidos = set(exchanges_restringidos + redes_inhabilitadas.get(moneda, []))
    # Iterar sobre los exchanges y agregar los datos a la lista
    for exchange in exchanges:
        exchange_name = exchange['market']['name']
        if exchange_name not in exchanges_prohibidos:
            pair = exchange['target']
            exchange_pair = exchange_name +"/"+ pair
            price = exchange['converted_last']['usd']
            bid_ask_spread = exchange['bid_ask_spread_percentage']
            trust_score = exchange['trust_score']
            if trust_score == "green":
                exchange_data.append([exchange_pair, price, bid_ask_spread])
    # Crear un DataFrame de Pandas con los datos
    df = pd.DataFrame(exchange_data, columns=['Exchange_Par', 'Precio (USD)', 'Margen'])
    data[moneda] = df
    
# Obtener el Gap de la primer Moneda, considerar solo los Gap Positivos
for moneda in monedas:
    gap_local = []
    #Buscar el GAP local
    for index, row in data[moneda].iterrows():
        precio1 =  row["Precio (USD)"]
        exchange_par1 = row["Exchange_Par"]
        margen1 = row["Margen"]
        for index2, row in data[moneda].iterrows():
            precio2 = row["Precio (USD)"]
            exchange_par2 = row["Exchange_Par"]
            margen2 = row["Margen"]
            gap = (((float(precio1)-float(precio2))/float(precio1))*100)-(margen1+margen2)
            if gap > 0:
                gap_local.append([moneda, exchange_par1, exchange_par2, precio1, precio2, gap])
    #crear un segundo data frame de aproximadamente (n x n / 2) elementos
    df = pd.DataFrame(gap_local, columns=['Moneda','Exchange_Par1','Exchange_Par2', 'Precio1', 'Precio2', 'Gap'])
    gaps[moneda]= df
    
#Iterar el segundo dataframe de cada moneda, para buscar un Gap cruzado vs otras monedas
for moneda in monedas:
    for gap, row in gaps[moneda].iterrows():
        gap = row["Gap"]
        exchange_par1 = row["Exchange_Par1"]
        exchange_par2 = row["Exchange_Par2"]
        precio1 = row["Precio1"]
        precio2 = row["Precio2"]

        for moneda2 in monedas:
            if moneda2 != moneda:
                #buscar coincidencias
                indice_exchange1_par1 = data[moneda2].loc[data[moneda2]["Exchange_Par"] == exchange_par1].index
                if indice_exchange1_par1.size > 0:
                    indice_exchange2_par2 = data[moneda2].loc[(data[moneda2]["Exchange_Par"] == exchange_par2)].index
                    if indice_exchange2_par2.size > 0:
                        intercambio= moneda+"/"+moneda2
                        valor_precio1 = data[moneda2].at[indice_exchange1_par1[0], 'Precio (USD)']
                        valor_precio2 = data[moneda2].at[indice_exchange2_par2[0], 'Precio (USD)']
                        margen3 = data[moneda2].at[indice_exchange1_par1[0], 'Margen']
                        margen4 = data[moneda2].at[indice_exchange2_par2[0], 'Margen']
                        gap2 = -((valor_precio1 - valor_precio2)/valor_precio1)*100
                        gap_cruzado = (gap + gap2)-(margen3 + margen4)
                        precioMoneda1 = str(precio1)+"/"+str(precio2)
                        precioMoneda2 = str(valor_precio1)+"/"+str(valor_precio2)
                        if gap_cruzado > 0.1:
                            mined.append([intercambio, exchange_par1, exchange_par2, precioMoneda1, precioMoneda2, gap_cruzado])
                            
#Guardar los datos en un CSV
encabezados = ["Intercambio", "Exchange Par 1", "Exchange Par 2", "Moneda1", "Moneda2", "Gap"]                          
csv_file = 'mined_data.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(encabezados)
    writer.writerows(mined)

print("Archivo CSV guardado con éxito: mined_data.csv")
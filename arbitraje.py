import pandas as pd
from pycoingecko import CoinGeckoAPI

# Crear una instancia de CoinGeckoAPI
cg = CoinGeckoAPI()
monedas = ["algorand", "iota", "litecoin", "ripple", "stellar"]

data = {}
gaps = {}
mined = []

# Obtener los datos del ticker 
for moneda in monedas:
    ticker = cg.get_coin_ticker_by_id(id=moneda, per_page=200)
    exchanges = ticker['tickers']
    exchange_data = []

    # Iterar sobre los exchanges y agregar los datos a la lista
    for exchange in exchanges:
        exchange_name = exchange['market']['name']
        pair = exchange['target']
        price = exchange['converted_last']['usd']
        bid_ask_spread = exchange['bid_ask_spread_percentage']
        trust_score = exchange['trust_score']
        if trust_score == "green":
            exchange_data.append([exchange_name, pair, price, bid_ask_spread])

    # Crear un DataFrame de Pandas con los datos
    df = pd.DataFrame(exchange_data, columns=['Exchange', 'Par', 'Precio (USD)', 'Margen'])
    data[moneda] = df
    
    
for moneda in monedas:
    gap_local = []
    #Buscar el GAP local
    for index, row in data[moneda].iterrows():
        precio1 =  row["Precio (USD)"]
        exchange1 = row["Exchange"]
        par1 = row["Par"]
        for index2, row in data[moneda].iterrows():
            precio2 = row["Precio (USD)"]
            exchange2 = row["Exchange"]
            par2 = row["Par"]
            gap = ((float(precio1)-float(precio2))/float(precio1))*100
            gap_local.append([moneda, exchange1, exchange2, par1, par2, gap])
    df = pd.DataFrame(gap_local, columns=['Moneda','Exchange1','Exchange2','Par1','Par2','Gap'])
    gaps[moneda]= df
    

for moneda in monedas:
    for gap, row in gaps[moneda].iterrows():
        gap = row["Gap"]
        exchange1 = row["Exchange1"]
        exchange2 = row["Exchange2"]
        par1 = row["Par1"]
        par2 = row["Par2"]

        for moneda2 in monedas:
            if moneda2 != moneda:
                #buscar coincidencias
                existe_exchange1_par1 = data[moneda2].loc[(data[moneda2]["Exchange"] == exchange1) & (data[moneda2]["Par"] == par1)].shape[0] > 0
                existe_exchange2_par2 = data[moneda2].loc[(data[moneda2]["Exchange"] == exchange2) & (data[moneda2]["Par"] == par2)].shape[0] > 0

                if (existe_exchange1_par1 and existe_exchange2_par2):
                    print("e")

        #consolidar tablas y buscar gap inverso
        #existe_exchange1_par1 = df_ripple.loc[(df_ripple["Exchange"] == "binance") & (df_ripple["Par"] == "USD")].shape[0] > 0





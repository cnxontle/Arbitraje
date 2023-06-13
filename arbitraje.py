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
        exchange_pair = exchange_name +"/"+ pair
        price = exchange['converted_last']['usd']
        bid_ask_spread = exchange['bid_ask_spread_percentage']
        trust_score = exchange['trust_score']
        if trust_score == "green":
            exchange_data.append([exchange_pair, price, bid_ask_spread])

    # Crear un DataFrame de Pandas con los datos
    df = pd.DataFrame(exchange_data, columns=['Exchange_Par', 'Precio (USD)', 'Margen'])
    data[moneda] = df
    
    
for moneda in monedas:
    gap_local = []
    #Buscar el GAP local
    for index, row in data[moneda].iterrows():
        precio1 =  row["Precio (USD)"]
        exchange_par1 = row["Exchange_Par"]
        
        for index2, row in data[moneda].iterrows():
            precio2 = row["Precio (USD)"]
            exchange_par2 = row["Exchange_Par"]
            
            gap = ((float(precio1)-float(precio2))/float(precio1))*100
            if gap > 0:
                gap_local.append([moneda, exchange_par1, exchange_par2, gap])
    df = pd.DataFrame(gap_local, columns=['Moneda','Exchange_Par1','Exchange_Par2','Gap'])
    gaps[moneda]= df
    
x=0
for moneda in monedas:
    for gap, row in gaps[moneda].iterrows():
        gap = row["Gap"]
        exchange_par1 = row["Exchange_Par1"]
        exchange_par2 = row["Exchange_Par2"]
        
        for moneda2 in monedas:
            if moneda2 != moneda:
                #buscar coincidencias
                indice_exchange1_par1 = data[moneda2].loc[data[moneda2]["Exchange_Par"] == exchange_par1].index
                if indice_exchange1_par1 != 0:
                    indice_exchange2_par2 = data[moneda2].loc[(data[moneda2]["Exchange_Par"] == exchange_par2)].index
                    if indice_exchange2_par2 != 0:
                        intercambio= moneda+"/"+moneda2

                        valor_precio1 = data[moneda2].at[indice_exchange1_par1[0], 'Precio (USD)']
                        valor_precio2 = data[moneda2].at[indice_exchange2_par2[0], 'Precio (USD)']
                        gap2 = ((valor_precio1 - valor_precio2)/valor_precio1)*100

                        mined.append([intercambio, exchange_par1, exchange_par2, gap, gap2])
                        print(x, intercambio, exchange_par1, exchange_par2, gap, gap2)
                        x+=1

        #consolidar tablas y buscar gap inverso
        #existe_exchange1_par1 = df_ripple.loc[(df_ripple["Exchange"] == "binance") & (df_ripple["Par"] == "USD")].shape[0] > 0





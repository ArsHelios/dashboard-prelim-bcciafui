import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIG ---
PRODUCTS = [
    'Dove Shampoo', 'Dove Conditioner', 'Dove Hair Treatment', 
    'Dove Hair Mask', 'Dove Hair Serum', 'Dove Hairsprays'
]

LOCATIONS = {
    # HUB & PORTS
    'Port_Shanghai': {'lat': 31.2304, 'lon': 121.4737},
    'Port_TanjungPriok': {'lat': -6.101, 'lon': 106.883},
    'DC_Cikarang': {'lat': -6.285, 'lon': 107.155}, 
    
    # RETAIL (Titik Toko Spesifik - JABODETABEK)
    'Store_Kemang': {'lat': -6.273, 'lon': 106.810},
    'Store_Menteng': {'lat': -6.190, 'lon': 106.830},
    'Store_BSD': {'lat': -6.280, 'lon': 106.660},
    'Store_Bekasi': {'lat': -6.230, 'lon': 106.990},
    'Store_Bogor': {'lat': -6.590, 'lon': 106.800},
    'Store_Depok': {'lat': -6.400, 'lon': 106.810},
    'Store_KelapaGading': {'lat': -6.150, 'lon': 106.900},
    'Store_Pluit': {'lat': -6.110, 'lon': 106.780},
    'Store_Tangerang': {'lat': -6.170, 'lon': 106.640},
    'Store_Cibubur': {'lat': -6.370, 'lon': 106.900}
}

def generate_csv():
    data = []
    base_date = datetime(2024, 1, 1)
    
    print("⏳ Generating High Density Data (Supaya Peta Ramai)...")

    # 1. INBOUND (Kapal)
    for i in range(150): 
        dept = base_date + timedelta(days=np.random.randint(0, 360))
        dur = np.random.randint(15, 25)
        item = np.random.choice(['Raw Surfactant', 'Packaging Bottles', 'Active Ingredients'])
        
        data.append({
            'ID': f'IMP-{100+i}', 'Category': 'Inbound', 'Type': 'Ship', 'Item': item,
            'Origin': 'Port_Shanghai', 'Destination': 'Port_TanjungPriok',
            'Start_Lat': LOCATIONS['Port_Shanghai']['lat'], 'Start_Lon': LOCATIONS['Port_Shanghai']['lon'],
            'End_Lat': LOCATIONS['Port_TanjungPriok']['lat'], 'End_Lon': LOCATIONS['Port_TanjungPriok']['lon'],
            'Departure': dept, 'Arrival': dept + timedelta(days=dur),
            'Status_Detail': 'In Transit',
            'Warehouse': 'All',
            'Qty': np.random.randint(10000, 50000)
        })

    # 2. LAST MILE (Retail) - KITA GENJOT JUMLAHNYA
    # Generate 5000 pengiriman setahun = ~13 pengiriman per hari
    # Durasi kita set agak lama (6-12 jam) biar "nyangkut" di peta saat disimulasikan
    retail_nodes = [k for k in LOCATIONS.keys() if 'Store' in k]
    
    for i in range(5000): 
        dest = np.random.choice(retail_nodes)
        dept = base_date + timedelta(days=np.random.randint(0, 365))
        # Tambahkan jam acak (0-23) biar sebarannya merata sepanjang hari
        dept = dept + timedelta(hours=np.random.randint(0, 24))
        
        dur_hours = np.random.randint(6, 14) # Durasi perjalanan agak lama (macet Jakarta)
        item = np.random.choice(PRODUCTS)
        wh_origin = 'DC_Cikarang'
        
        data.append({
            'ID': f'DEL-{1000+i}', 'Category': 'Last Mile', 'Type': 'Van', 'Item': item,
            'Origin': wh_origin, 'Destination': dest,
            'Start_Lat': LOCATIONS[wh_origin]['lat'], 'Start_Lon': LOCATIONS[wh_origin]['lon'],
            'End_Lat': LOCATIONS[dest]['lat'], 'End_Lon': LOCATIONS[dest]['lon'],
            'Departure': dept, 'Arrival': dept + timedelta(hours=dur_hours),
            'Status_Detail': 'Out for Delivery',
            'Warehouse': wh_origin,
            'Qty': np.random.randint(50, 500)
        })
        
    # 3. INVENTORY SNAPSHOT DUMMY
    dcs = ['DC Cikarang', 'DC Surabaya', 'DC Medan']
    for dc in dcs:
        for prod in PRODUCTS:
            data.append({
                'ID': f'INV', 'Category': 'Inventory_Snapshot', 'Type': 'Static', 
                'Item': prod, 'Origin': dc, 'Destination': '-',
                'Start_Lat': 0, 'Start_Lon': 0, 'End_Lat': 0, 'End_Lon': 0,
                'Departure': base_date, 'Arrival': base_date,
                'Status_Detail': 'Available', 'Warehouse': dc, 'Qty': np.random.randint(2000, 15000)
            })

    df = pd.DataFrame(data)
    df.to_csv("data_supply_chain.csv", index=False)
    print("✅ Data Selesai! (Last Mile sudah diperbanyak)")

if __name__ == "__main__":
    generate_csv()
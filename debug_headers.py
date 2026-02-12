import pandas as pd
try:
    df = pd.read_excel('/home/joseph/Descargas/basededatosiniestros.xlsx', nrows=0)
    print("COLUMNS_FOUND:")
    for col in df.columns:
        print(col)
except Exception as e:
    print(f"ERROR: {e}")

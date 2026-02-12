import pandas as pd
try:
    df = pd.read_excel('/home/joseph/Descargas/basededatosiniestros.xlsx')
    
    vals = set()
    for col in df.columns:
        if 'RESULTADO' in col.upper() and 'VALORACIÓN' in col.upper():
            unique_vals = df[col].dropna().unique()
            for v in unique_vals:
                vals.add(str(v).upper())
                
    print("UNIQUE VALUES IN RESULTADO COLS:")
    for v in sorted(list(vals)):
        print(v)

except Exception as e:
    print(f"ERROR: {e}")

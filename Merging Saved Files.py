import pandas as pd

df = pd.read_excel("UCL_Eleme_Turları_Verisi.xlsx")
df1 = pd.read_excel("UCL_Kurtarilan_Veri.xlsx")
df2 = pd.read_excel("UCL_Kurtarilan_Veri2.xlsx")
df3 = pd.read_excel("UCL_Kurtarilan_Veri3.xlsx")

birlesik_df = pd.concat([df1, df2, df3], ignore_index=True)

# 3. ADIM: Kopyaları (Duplicates) Temizleme
# Tüm sütunlardaki verisi birebir aynı olan satırları bulur,
# ilkini tutar (keep='first') ve geri kalan kopyaları yok eder.
clean_df = birlesik_df.drop_duplicates(ignore_index=True)

df["Date"] = clean_df["Date"]
df["Referee"] = clean_df["Referee"]
df["Stadium"] = clean_df["Stadium"]
df["Attandence"] = clean_df["Attandence"]

df.to_excel("UCL_Eleme_Turları_Verisi2.xlsx")
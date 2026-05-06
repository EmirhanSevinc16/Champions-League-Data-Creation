import pandas as pd

df = pd.read_excel("UCL_Eleme_Turları_Verisi2.xlsx")

leg_list = []


# Adding Leg Column to Data Frame
for row in df["Stage"]:
    lower_row = str(row).lower()
    if "1st leg" in lower_row:
        leg_list.append("1st Leg")
    elif "2nd leg" in lower_row:
        leg_list.append("2nd Leg")
    else:
        leg_list.append("Single Game Elimination")

df["Leg"]=leg_list

# 'Stage' sütunundaki " 1st leg" ve " 2nd leg" ifadelerini bul ve hiçlikle (boş string) değiştir.
# case=False diyerek az önce başımızı ağrıtan büyük/küçük harf sorununu baştan engelliyoruz.
df["Stage"] = df["Stage"].str.replace("1st leg", "", case=False)
df["Stage"] = df["Stage"].str.replace("2nd leg", "", case=False)

# str.strip() hayat kurtarır! Yazıları sildikten sonra geriye kalan
# görünmez boşlukları (Örn: "Second Round   " -> "Second Round") temizler.
df["Stage"] = df["Stage"].str.strip()

duration_list = []

# Adding Game Duration Column
for score in df["Score"]:
    if "AET" in score:
        duration_list.append("Extra Time")
    elif "on pens" in score:
        duration_list.append("Penalties")
    else:
        duration_list.append("Normal Time")

df["Duration"] = duration_list


df["Attandence"] = df["Attandence"].str.replace("Attendance:", "", case=False)
df["Attandence"] = df["Attandence"].str.strip()

df["Score"] = df["Score"].str.replace("AET", "", case=False)
df["Score"] = df["Score"].str.replace("on pens", "", case=False)
df["Score"] = df["Score"].str.strip()

df[["Home Goals","Away Goals"]] = df["Score"].str.split(":", expand=True)
df.drop(columns=["Score"], inplace=True)

df.to_excel("Ucl_Eleme_Turları_Verisi3.xlsx", index=False)
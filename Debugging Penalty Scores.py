import random
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

normal_time_scores = []
df = pd.read_excel("Ucl_Eleme_Turları_Verisi3.xlsx")

df["Penalty Scores"] = np.where(df["Duration"] != "Penalties", "No Penalties", "Scraping Needed")
df["Home Penalty Score"] = np.where(df["Duration"] != "Penalties", "No Penalties", "Scraping Needed")
df["Away Penalty Score"] = np.where(df["Duration"] != "Penalties", "No Penalties", "Scraping Needed")


penalti_maclari = df[df["Penalty Scores"] == "Scraping Needed"]



for index, row in penalti_maclari.iterrows():
    # Sezon bilgisinden yılı çekiyoruz (Örn: "2015-2016" içinden "2015"i alıyoruz)
    # Senin verinde Sezonlar sadece rakam (2015) ise bu split'e gerek kalmaz, direkt str(row["Season"]) yazabilirsin.
    season_year = str(row["Season"]).split("-")[0]

    season_url = f"https://www.transfermarkt.com/uefa-champions-league/startseite/pokalwettbewerb/CL?saison_id={season_year}"
    kimlik = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        answer_season = requests.get(season_url, headers=kimlik)
        soup_season = BeautifulSoup(answer_season.content, "html.parser")
        print(f"📡 BAŞARILI! {season_year} sezonunun ana sayfasına sızıldı.")
        time.sleep(random.randint(100, 500)/100)

        game_rows = soup_season.find_all("tr", class_="begegnungZeile")

        home_team = row["Home Teams"]
        away_team = row["Away Teams"]

        for row in game_rows:
            teams = row.find_all("span",class_="vereinsname")
            if teams[0].text.strip() == home_team and teams[1].text.strip() == away_team:
                print(f"Eşleşme bulundu maç: {home_team} vs {away_team}")
                game_link = row.find("a", title="Match report")
                half_link = game_link["href"]
                full_url = "https://www.transfermarkt.com" + half_link

                time.sleep(random.randint(100, 300)/100)
                detay_cevap = requests.get(full_url, headers=kimlik)
                match_soup = BeautifulSoup(detay_cevap.content, "html.parser")
                print("İçerideyiz! Maç Sayfası Başlığı:")
                print(match_soup.title.text.strip())
                penalty_rows = match_soup.find_all("li", class_=["sb-aktion-heim","sb-aktion-spielstand"])
                goals_header = match_soup.find("h2", class_="content-box-headline",
                                               string=lambda text: text and "Goals" in text)
                if goals_header:
                    # 2. ADIM: Başlığın ait olduğu ana kutuyu (div class="box") buluyoruz.
                    # Artık elimizde sadece normal süre gollerinin olduğu kutu var!
                    goals_box = goals_header.find_parent("div", class_="box")

                    # 3. ADIM: Skorları SADECE bu kutunun içinde arıyoruz
                    normal_scores = goals_box.find_all(class_="sb-aktion-spielstand")

                    if normal_scores:
                        # Liste içindeki en son eleman [-1], hakem düdüğü çalmadan önceki son skordur
                        normal_time_score = normal_scores[-1].text.strip()
                        normal_time_scores.append(normal_time_score)
                        print(f"Normal Süre Skoru Bulundu: {normal_time_score}")
                    else:
                        # Kutu var ama skor yoksa?
                        normal_time_score = "0:0"
                        normal_time_scores.append(normal_time_score)
                        print("Gol kutusu var ama skor yok, muhtemelen 0:0 bitti.")
                else:
                    # Sayfada "Goals" diye bir kutu HİÇ yoksa, maç banko 0-0 bitmiş ve direkt penaltılara (veya uzatmaya) geçilmiştir.
                    normal_time_score = "0:0"
                    normal_time_scores.append(normal_time_score)
                    print("Goals başlığı yok, maç normal sürede 0:0 bitmiş.")



    except Exception as e:

        print(f"🚨 SİSTEMSEL HATA ({season_year} Sezonu - {home_team} vs {away_team}): {e}")

        # Hata durumunda listeler patlamasın diye yedek skor ekliyoruz

        normal_time_scores.append("0:0")

        df.at[index, "Penalty Scores"] = "Hata"

        print("💾 Olası bir çökmeye karşı o ana kadarki tüm veriler kurtarılıyor...")

        df.to_excel("UCL_Acil_Durum_Yedek.xlsx", index=False)

        print("✅ Veriler 'UCL_Acil_Durum_Yedek.xlsx' dosyasına güvenle kilitlendi. Koda devam ediliyor...\n")


#FINAL MANIPULATIONS
penalti_maclari["Penalty Scores"] = normal_time_scores
penalti_maclari[["Home Penalty Score","Away Penalty Score"]] = penalti_maclari["Penalty Scores"].str.split(":", expand=True)
penalti_maclari[['Home Goals', 'Home Penalty Score']] = penalti_maclari[['Home Penalty Score', 'Home Goals']].values
penalti_maclari[['Away Goals', 'Away Penalty Score']] = penalti_maclari[['Away Penalty Score', 'Away Goals']].values
penalti_maclari['Home Penalty Score'] = penalti_maclari['Home Penalty Score'].astype(int) - penalti_maclari['Home Goals'].astype(int)
penalti_maclari['Away Penalty Score'] = penalti_maclari['Away Penalty Score'].astype(int) - penalti_maclari['Away Goals'].astype(int)
penalti_maclari['Home Goals'] = penalti_maclari['Home Goals'].astype(int)
penalti_maclari['Away Goals'] = penalti_maclari['Away Goals'].astype(int)
penalti_maclari['Home Penalty Score'] = penalti_maclari['Home Penalty Score'].astype(str)
penalti_maclari['Away Penalty Score'] = penalti_maclari['Away Penalty Score'].astype(str)
df.update(penalti_maclari)

df.to_excel("UCL_Eleme_Turları_Verisi_Finished.xlsx",index=False)
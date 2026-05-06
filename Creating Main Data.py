import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

seasons_list = []
for i in range(1992,2026):
    seasons_list.append(i)
all_home_teams = []
all_away_teams = []
all_game_results = []
all_seasons = []
stage_list = []
for season in seasons_list:
    url = f"https://www.transfermarkt.com/uefa-champions-league/startseite/pokalwettbewerb/CL/saison_id/{season}"

# Python'a standart bir web tarayıcısı (Google Chrome) kılığına girmesini söylüyoruz
    kimlik = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

# Kapıyı çalarken bu sahte kimliği (headers) güvenliğe gösteriyoruz
    cevap = requests.get(url, headers=kimlik)

# Çorbayı tekrar kuruyoruz
    soup = BeautifulSoup(cevap.content, "html.parser")

# Şimdi testi tekrarlayalım
    print("Sayfa Başlığı:", soup.title.text)

    tablo = soup.find("table")

# Eğer tablo geldiyse, HTML'in çok küçük bir kısmını (örneğin id'sini) yazdıralım
    if tablo:
        print("Müjde! Güvenliği aştık, tablo bulundu.")
    else:
        print("Tablo hala yok.")

    stage_rows = soup.find_all("tr", class_="rundenzeile")
    for row in stage_rows:
        stage_name = row.text.strip()
        game_counter = 0
        next_stage = row.find_next_sibling("tr")
        while next_stage and "rundenzeile" not in next_stage.get("class", []):
            # Eğer bu satırın içinde oynanmış bir maç skoru varsa sayacı 1 artır
            if next_stage.find("span", class_="matchresult finished"):
                game_counter += 1

            # Sayma işlemi bitince bir alt satıra (bir sonraki kardeşe) geç
            next_stage = next_stage.find_next_sibling("tr")

        for game in range(game_counter):
            stage_list.append(stage_name)


    game_rows= soup.find_all("tr", class_="begegnungZeile")

    teams_list = []
    game_scores = []


    for row in game_rows:
        result = row.find("span", class_="matchresult finished")
        if result:
            clean_result = result.text.strip()
            game_scores.append(clean_result)
            teams = row.find_all("span", class_="vereinsname")
            for team in teams:
                team = team.text.strip()
                teams_list.append(team)

    home_teams = teams_list[0::2]
    away_teams = teams_list[1::2]




    for team in home_teams:
        all_home_teams.append(team)
        all_seasons.append(f"{season}-{season+1}")
    for team in away_teams:
        all_away_teams.append(team)
    for game in game_scores:
        all_game_results.append(game)
    time.sleep(3)


df = pd.DataFrame({
    "Season": all_seasons,
    "Home Teams": all_home_teams,
    "Away Teams": all_away_teams,
    "Score": all_game_results,
    "Stage": stage_list
})

df.to_excel("UCL_Eleme_Turları_Verisi.xlsx", index=False)



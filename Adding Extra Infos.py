import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


seasons_list = []
attandence_list = []
referee_list = []
stadium_list = []
date_list = []

for i in range(2025,2026):
    seasons_list.append(i)
try:
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

        game_rows = soup.find_all("tr", class_="begegnungZeile")

        for row in game_rows:
            game_link = row.find("a",title="Match report")
            if game_link:
                # 1. Yarım olan linki ('/spielbericht/...') çekip tam bir web adresine çeviriyoruz
                half_link = game_link["href"]
                tam_url = "https://www.transfermarkt.com" + half_link
                time.sleep(2)

                detay_cevap = requests.get(tam_url, headers=kimlik)
                match_soup = BeautifulSoup(detay_cevap.content, "html.parser")

                print("İçerideyiz! Maç Sayfası Başlığı:")
                print(match_soup.title.text.strip())

                #Adding Attandence to Df
                attandence_line_list = []
                attandence_line = match_soup.find_all("strong")

                # 1. Başlangıçta şalterimiz kapalı (Henüz seyirci verisini bulmadık)
                attendance_found = False

                for attandence in attandence_line:
                    # 2. Üretim bandından geçen metnin içinde o kelime geçiyor mu?
                    if "Attendance" in attandence.text:
                        # Bulduk! Ana listeye doğrudan ekle. (strip() ile sağdaki soldaki boşlukları temizliyoruz)
                        attandence_list.append(attandence.text.strip())

                        # Şalteri kaldır ve döngüyü kır (Çünkü bulduk, diğerlerine bakıp vakit kaybetmeye gerek yok)
                        attendance_found = True
                        break

                        # 3. Döngü bitti. Banttaki her şeye baktık. Şalter hala kapalı mı?
                if not attendance_found:
                    # Demek ki seyirci verisi yokmuş (Covid maçı vs.). Ana listeye boş (None) değer atıyoruz.
                    attandence_list.append(None)



                referee_label = match_soup.find("a", href=lambda href: href and "schiedsrichter" in href)
                if referee_label:
                    referee = referee_label.text
                    referee_list.append(referee)
                else:
                    referee_list.append(None)

                stadium_label = match_soup.find("a", href=lambda href: href and "stadion" in href)
                if stadium_label:
                    stadium = stadium_label.text
                    stadium_list.append(stadium)
                else:
                    stadium_list.append(None)

                date_row = match_soup.find("a", href=lambda href: href and "aktuell/waspassiertheute" in href)
                if date_row:
                    date = date_row.text
                    date_list.append(date)
                else:
                    date_list.append(None)

    df = pd.read_excel("UCL_Eleme_Turları_Verisi.xlsx")

    df["Date"] = date_list
    df["Stadium"] = stadium_list
    df["Attandence"] = attandence_list
    df["Referee"] = referee_list

    df.to_excel("UCL_Eleme_Turları_Kurtarma4.xlsx")

except Exception as e:
    print(f"\nBÜYÜK ÇÖKÜŞ YAŞANDI! Hata: {e}")
    print("Kurtarma operasyonu başlatılıyor...")

    # 1. ADIM: Listelerin uzunluklarını buluyoruz
    len_att = len(attandence_list)
    len_ref = len(referee_list)
    len_sta = len(stadium_list)
    len_dat = len(date_list)

    # 2. ADIM: En kısa listenin uzunluğunu buluyoruz (Ortak payda)
    min_len = min(len_att, len_ref, len_sta, len_dat)
    print(f"Eksiksiz çekilebilen tam maç sayısı: {min_len}")

    # 3. ADIM: Tüm listeleri o en kısa uzunluğa göre "kırpıyoruz" (Tıraşlıyoruz)
    # Böylece Pandas "Listeler eşit değil" diye hata veremez!
    mini_df = pd.DataFrame({
        "Stadium": stadium_list[:min_len],
        "Date": date_list[:min_len],
        "Attandence": attandence_list[:min_len],
        "Referee": referee_list[:min_len]
    })

    # 4. ADIM: Kurtarılan veriyi Excel'e basıyoruz
    mini_df.to_excel("UCL_Kurtarilan_Veri4.xlsx", index=False)
    print("MÜJDE! Çöküş anına kadar olan veriler UCL_Kurtarilan_Veri4.xlsx dosyasına kaydedildi.")









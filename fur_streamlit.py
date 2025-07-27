import math
import json
import os
from datetime import datetime
import streamlit as st

def lager_datei(hotel):
    return f"lager_{hotel}.json"
def history_datei(hotel):
    return f"history_{hotel}.json"

def lade_lager(hotel):
    pfad = lager_datei(hotel)
    if os.path.exists(pfad):
        with open(pfad, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

#Сохранение лагеря и даты

MAX_HISTORY = 50

def speichere_lager(hotel, lager):
    lager["__zeit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pfad = lager_datei(hotel)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(lager, f, ensure_ascii=False, indent=2)

def speichere_history(hotel, daten):
    pfad = history_datei(hotel)
    eintrag = {
        "zeit": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hotel": hotel,
        "daten": daten
    }
    history = []
    if os.path.exists(pfad):
        with open(pfad, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append(eintrag)
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

#Резерв

def reserve_20(wert, prozent=20):
    return math.ceil(wert * (1 + prozent / 100))

def reserve_10(wert, prozent=10):
    return math.ceil(wert * (1 + prozent / 100))
    
def main():
    hotel = st.text_input("🔍 Geben Sie den Namen des Hotels ein (Oben / Blau) / Введите название отеля:").strip().lower()
    if not hotel:
        return

    lager = lade_lager(hotel)
    
    #BLAU
    
    if hotel == "blau":
        zimmer_klein = st.number_input("🔹 Geben Sie die Anzahl der kleinen Zimmer ein / Введите количество маленьких комнат:", min_value=0, step=1)
        zimmer_gross = st.number_input("🔷 Geben Sie die Anzahl der großen Zimmer ein / Введите количество больших комнат:", min_value=0, step=1)
        
        if st.button("Berechnen / Рассчитать"):
            bettlaken_klein = zimmer_klein          
            bettlaken_gross = zimmer_gross         
            bezug_gross = zimmer_klein + zimmer_gross
            bezug_klein = math.ceil((zimmer_klein + zimmer_gross) * 0.1)
            kissen = 4 * (zimmer_klein + zimmer_gross)
            duschtuch = 2 * (zimmer_klein + zimmer_gross)
            handtuch = 2 * (zimmer_klein + zimmer_gross)
            fussmatte = zimmer_klein + zimmer_gross
            geschirrtuch = zimmer_klein + zimmer_gross 
            sack = 1 if zimmer_klein + zimmer_gross < 2 else (zimmer_klein + zimmer_gross + 1) // 2 
            
            st.write("📋 Die Menge an Bettwäsche und Handtüchern, die bestellt werden muss:")
            st.write(f"- Bezüge 240x210: {reserve_10(bezug_gross)}")
            st.write(f"- Bezüge 140x230: {reserve_10(bezug_klein)}")
            st.write(f"- Bettlaken 280x300: {reserve_10(bettlaken_gross)}")
            st.write(f"- Bettlaken 220x300: {reserve_10(bettlaken_klein)}")
            st.write(f"- Kissen 80x80: {reserve_10(kissen)}")
            st.write(f"- Duschtuch 70x140: {reserve_20(duschtuch)}")
            st.write(f"- Handtuch 50x100: {reserve_20(handtuch)}")
            st.write(f"- Vorleger 50x90: {reserve_20(fussmatte)}")
            st.write(f"- Geschirrtücher 60x80: {geschirrtuch}")
            st.write("- Plastiksack rot: Bestimmen Sie die optimale Anzahl an Säcken für beschädigte Bettwäsche / Определите оптимальное количество пакетов для повреждённого белья")
            st.write(f"- Transportsack 70x110: {sack}")
            st.write("- Container zur Abholung: 0")
            st.write("- Container Bestellung leer: 0")
            
            daten = {
                "Bezüge 240x210": reserve_10(bezug_gross),
                "Bezüge 140x230": reserve_10(bezug_klein),
                "Bettlaken 280x300": reserve_10(bettlaken_gross),
                "Bettlaken 220x300": reserve_10(bettlaken_klein),
                "Kissen 80x80": reserve_10(kissen),
                "Duschtuch 70x140": reserve_20(duschtuch),
                "Handtuch 50x100": reserve_20(handtuch),
                "Vorleger 50x90": reserve_20(fussmatte),
                "Geschirrtücher 60x80": geschirrtuch,
                "Transportsack 70x110": sack
            }
            st.write("❓ Speichern Sie das Ergebnis und fügen Sie den Lagerbestand hinzu? / Сохранить результат и прибавить запасы на склад?")
            col1, col2 = st.columns(2)
            with col1:
                speichern = st.button("✅ Speichern")
            with col2:
                nicht_speichern = st.button("✖️ Nicht speichern")
            if speichern:
                for name, menge in daten.items():
                lager[name] = lager.get(name, 0) + menge
            speichere_lager(hotel, lager)
            speichere_history(hotel, daten)
            st.success("✅ Gespeichert")
            elif nicht_speichern:
            st.info("✖️ Nicht gespeichert")

  #OBEN

    elif hotel == "oben":
        zimmer_klein = st.number_input("🔹 Geben Sie die Anzahl der kleinen Zimmer ein / Введите количество маленьких комнат:", min_value=0, step=1)
        zimmer_gross = st.number_input("🔷 Geben Sie die Anzahl der großen Zimmer ein / Введите количество больших комнат:", min_value=0, step=1)
        
        if st.button("Berechnen / Рассчитать"):
            bettlaken_klein = zimmer_klein        
            bettlaken_gross = zimmer_gross         
            bezug_gross = zimmer_gross 
            bezug_klein = zimmer_klein
            kissen = (2 * zimmer_klein) + (4 * zimmer_gross)
            duschtuch = (2 * zimmer_gross) + zimmer_klein 
            handtuch = (2 * zimmer_gross) + zimmer_klein
            fussmatte = zimmer_klein + zimmer_gross
            geschirrtuch = zimmer_klein + zimmer_gross 
                
            st.write("📋 Die Menge an Bettwäsche und Handtüchern, die bestellt werden muss:")
            st.write(f"- Bezüge 240x210: {reserve_10(bezug_gross)}")
            st.write(f"- Bezüge 140x230: {reserve_10(bezug_klein)}")
            st.write(f"- Bettlaken 280x300: {reserve_10(bettlaken_gross)}")
            st.write(f"- Bettlaken 220x300: {reserve_10(bettlaken_klein)}")
            st.write(f"- Kissen 80x80: {reserve_10(kissen)}")
            st.write(f"- Duschtuch 70x140: {reserve_20(duschtuch)}")
            st.write(f"- Handtuch 50x100: {reserve_20(handtuch)}")
            st.write(f"- Vorleger 50x90: {reserve_20(fussmatte)}")
            st.write(f"- Geschirrtücher 60x80: {geschirrtuch}")
            st.write("- Plastiksack rot: Bestimmen Sie die optimale Anzahl an Säcken für beschädigte Bettwäsche / Определите оптимальное количество пакетов для повреждённого белья")
            st.write("- Transportsack 70x110: 0")
            st.write("- Container zur Abholung: Den Lagerbestand überprüfen / Свериться со складом")
            st.write("- Container Bestellung leer: Den Lagerbestand überprüfen / Свериться со складом")
            
            daten = {
                "Bezüge 240x210": reserve_10(bezug_gross),
                "Bezüge 140x230": reserve_10(bezug_klein),
                "Bettlaken 280x300": reserve_10(bettlaken_gross),
                "Bettlaken 220x300": reserve_10(bettlaken_klein),
                "Kissen 80x80": reserve_10(kissen),
                "Duschtuch 70x140": reserve_20(duschtuch),
                "Handtuch 50x100": reserve_20(handtuch),
                "Vorleger 50x90": reserve_20(fussmatte),
                "Geschirrtücher 60x80": geschirrtuch,
            }
            st.write("❓ Speichern Sie das Ergebnis und fügen Sie den Lagerbestand hinzu? / Сохранить результат и прибавить запасы на склад?")
            col1, col2 = st.columns(2)
            with col1:
            speichern = st.button("✅ Speichern")
            with col2:
            nicht_speichern = st.button("✖️ Nicht speichern")
            if speichern:
                for name, menge in daten.items():
                lager[name] = lager.get(name, 0) + menge
            speichere_lager(hotel, lager)
            speichere_history(hotel, daten)
            st.success("✅ Gespeichert")
            elif nicht_speichern:
            st.info("✖️ Nicht gespeichert")

    else:
        st.error("Hotel nicht gefunden, überprüfen Sie den Namen / Отель не найден, проверьте название")

#Склад

def zeige_lager(hotel):
    lager = lade_lager(hotel)
    if not lager:
        st.info("Das Lager ist leer oder nicht initialisiert")
        return

    zeit = lager.get("__zeit")
    if zeit:
        st.write(f"📅 Das Lager ist für das nächste Datum relevant: {zeit}")
    else:
        st.write("📅 Das Datum der letzten Änderung ist unbekannt")

    st.write("📦 Rückstände im Lager:")
    for name, menge in lager.items():
        if name != "__zeit":
            st.write(f"- {name}: {menge}")

#История заказов

def zeige_history(hotel):
    pfad = history_datei(hotel)
    if not os.path.exists(pfad):
        st.info("Die Geschichte ist leer")
        return
    with open(pfad, "r", encoding="utf-8") as f:
        history = json.load(f)
    if not history:
        st.info("Die Geschichte ist leer")
        return
    st.write("⏳ Auftragsverlauf / История заказов:")
    for eintrag in history:
        zeit = eintrag.get("zeit", "die Zeit ist unbekannt")
        hotel_ = eintrag.get("hotel", "das Hotel ist unbekannt")
        daten = eintrag.get("daten", {})
        st.write(f"- [{zeit}] Hotel: {hotel_}")
        for name, menge in daten.items():
            st.write(f"    {name}: {menge}")
        st.write("")

#Очистка склада

def lager_loeschen(hotel):
    st.write("❗ Sind Sie sicher, dass Sie das Lager räumen möchten? / Вы уверены, что хотите очистить склад?")
    col1, col2 = st.columns(2)
    with col1:
        ja = st.button("✅ Ja")
    with col2:
        nein = st.button("✖️ Nein")
    if ja:
        pfad = lager_datei(hotel)
        if os.path.exists(pfad):
            os.remove(pfad)
            st.success(f"✅ Das Lager für {hotel} ist geräumt")
        else:
            st.error("✖️ Die Lagerdatei wurde nicht gefunden")
    elif nein:
        st.info("✖️ Vorgang abgebrochen / Операция отменена")

#Вычет со склада

def verbrauch_berechnen(hotel, zimmer_klein, zimmer_gross):
    lager = lade_lager(hotel)
    daten = {}
    if hotel == "blau":
        daten = {
            "Bezüge 240x210": reserve_10(zimmer_klein + zimmer_gross),
            "Bezüge 140x230": reserve_10(math.ceil((zimmer_klein + zimmer_gross) * 0.1)),
            "Bettlaken 280x300": reserve_10(zimmer_gross),
            "Bettlaken 220x300": reserve_10(zimmer_klein),
            "Kissen 80x80": reserve_10(4 * (zimmer_klein + zimmer_gross)),
            "Duschtuch 70x140": reserve_20(2 * (zimmer_klein + zimmer_gross)),
            "Handtuch 50x100": reserve_20(2 * (zimmer_klein + zimmer_gross)),
            "Vorleger 50x90": reserve_20(zimmer_klein + zimmer_gross),
            "Geschirrtücher 60x80": zimmer_klein + zimmer_gross,
            "Transportsack 70x110": 1 if zimmer_klein + zimmer_gross < 2 else (zimmer_klein + zimmer_gross + 1) // 2
             }
    elif hotel == "oben":
        daten = {
            "Bezüge 240x210": reserve_10(zimmer_gross),
            "Bezüge 140x230": reserve_10(zimmer_klein),
            "Bettlaken 280x300": reserve_10(zimmer_gross),
            "Bettlaken 220x300": reserve_10(zimmer_klein),
            "Kissen 80x80": reserve_10((2 * zimmer_klein) + (4 * zimmer_gross)),
            "Duschtuch 70x140": reserve_20((2 * zimmer_gross) + zimmer_klein),
            "Handtuch 50x100": reserve_20((2 * zimmer_gross) + zimmer_klein),
            "Vorleger 50x90": reserve_20(zimmer_klein + zimmer_gross),
            "Geschirrtücher 60x80": zimmer_klein + zimmer_gross
        }
    else:
        st.error("Hotel nicht gefunden / Отель не найден")
        return
        
    fehlende = []
    for name, menge in daten.items():
        if lager.get(name, 0) < menge:
            fehlende.append(f"{name} (man soll: {menge}, gibt es: {lager.get(name, 0)})")
    if fehlende:
        st.error("❌ Es fehlen folgende Positionen im Lager:")
        for f in fehlende:
            st.write(f"- {f}")
        return

    for name, menge in daten.items():
        lager[name] -= menge

    speichere_lager(hotel, lager)
    speichere_history(hotel + " (Verbrauch)", {k: -v for k, v in daten.items()})
    st.success("✅ Wäsche wurde vom Lager abgezogen")

#Меню

st.sidebar.title("▫️Aktion auswählen:")
menu = st.sidebar.radio("", (
    "0 – 🪫Vom Lager abschreiben  / Списать со склада",
    "1 – 🔋Wäsche berechnen / Рассчитать белье",
    "2 – 📦Lagerreste anzeigen / Показать остатки на складе",
    "3 – ⏳Auftragsverlauf anzeigen / Показать историю заказов",
    "4 – 🧹Lager räumen / Очистить склад",
    "5 – 🖋️ Lager manuell bearbeiten / Редактировать склад вручную"
))

if menu.startswith("1"):
    main()

elif menu.startswith("2"):
    hotel = st.text_input("🔍 Geben Sie den Namen des Hotels ein (Oben / Blau) / Введите название отеля:").strip().lower()
    if hotel:
        zeige_lager(hotel)

elif menu.startswith("3"):
    hotel = st.text_input("🔍 Geben Sie den Namen des Hotels ein (Oben / Blau) / Введите название отеля:").strip().lower()
    if hotel:
        zeige_history(hotel)

elif menu.startswith("4"):
    hotel = st.text_input("🔍 Geben Sie den Namen des Hotels ein (Oben / Blau) / Введите название отеля:").strip().lower()
    if hotel:
        lager_loeschen(hotel)

elif menu.startswith("0"):
    hotel = st.text_input("🔍 Geben Sie den Namen des Hotels ein (Oben / Blau) / Введите название отеля:").strip().lower()
    if hotel:
        zimmer_klein = st.number_input("🔹 Wie viele kleine Zimmer wurden gereinigt? / Сколько маленьких комнат было убрано?", min_value=0, step=1)
        zimmer_gross = st.number_input("🔷 Wie viele große Zimmer wurden gereinigt? Сколько больших комнат было убрано?", min_value=0, step=1)
        if st.button("Vom Lager abschreiben / Списать со склада"):
            verbrauch_berechnen(hotel, zimmer_klein, zimmer_gross)

elif menu.startswith("5"):
    hotel = st.text_input("🔍 Geben Sie den Namen des Hotels ein (Oben / Blau) / Введите название отеля:").strip().lower()
    if hotel:
        lager = lade_lager(hotel)
        st.write("📋 Aktuelles Lager:")
        for name, menge in lager.items():
            if name != "__zeit":
                st.write(f"- {name}: {menge}")
        name = st.text_input("✏️ Name der Position zur Änderung / Название позиции для изменения:").strip().lower()
        if name:
            lager_suchname = None
            for key in lager:
                if key.lower() == name and key != "__zeit":
                    lager_suchname = key
                    break
            if lager_suchname is None:
            	st.error("✖️ Diese Position ist nicht auf Lager")
            else:
            	neue_menge = st.number_input(f"🔢 Neue Menge für '{lager_suchname}' \nNeue Menge für '{lager_suchname}' / Новое количество для '{lager_suchname}' \nNeue Menge für '{lager_suchname}':", min_value=0, step=1)
            	if st.button("Speichern / Сохранить"):
            	         lager[lager_suchname] = neue_menge
            	         speichere_lager(hotel, lager)
            	         st.success("✅ Erneut gespeichert")

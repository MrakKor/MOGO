import math
import json
import os
from datetime import datetime
import streamlit as st  
import tempfile
from json import JSONDecodeError
import traceback

st.image("logo.png", width=200)

#Пароль
PASSWORD = st.secrets["auth"]["password"]
if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False
if not st.session_state.auth_ok:
    st.title("🔐 Geschützter Zugriff")
    pw = st.text_input("Passwort eingeben", type="password")
    if pw == PASSWORD:
        st.session_state.auth_ok = True
        st.rerun()
    elif pw:
        st.error("❌ Falsches Passwort")
    st.stop()

hotel_liste = ["", "blau", "oben"] 
if "hotel" not in st.session_state:
    st.session_state.hotel = ""
st.session_state.hotel = st.selectbox(
    "🏨 Wählen Sie ein Hotel / Выберите отель:",
    options=hotel_liste,
    index=hotel_liste.index(st.session_state.hotel) if st.session_state.get("hotel") in hotel_liste else 0
)

def lager_datei(hotel):
    return f"lager_{hotel}.json"
def history_datei(hotel):
    return f"history_{hotel}.json"

def lade_lager(hotel):
    pfad = lager_datei(hotel)
    if os.path.exists(pfad):
        try:
            with open(pfad, "r", encoding="utf-8") as f:
                return json.load(f)
        except (JSONDecodeError, IOError):
            return {}  
    return {}
    
#Сохранения для моментальной подгрузки склада

def get_lager(hotel):
    key = f"lager_{hotel}"
    if key in st.session_state:
        return st.session_state[key]
    lager = lade_lager(hotel)
    st.session_state[key] = lager
    return lager

def set_lager(hotel, lager):
    st.session_state[f"lager_{hotel}"] = lager
    speichere_lager(hotel, lager)

#Сохранение лагеря и даты

MAX_HISTORY = 50

def speichere_lager(hotel, lager):
    try:
        lager["__zeit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pfad = lager_datei(hotel)
        atomic_write(pfad, lager)
    except Exception:
        st.error("Fehler beim Speichern des Lagers"); st.text(traceback.format_exc())

def atomic_write(path, data):
    dirn = os.path.dirname(path) or "."
    with tempfile.NamedTemporaryFile("w", delete=False, dir=dirn, encoding="utf-8") as tf:
        json.dump(data, tf, ensure_ascii=False, indent=2)
        tf.flush()
        os.fsync(tf.fileno())
        tempname = tf.name
    os.replace(tempname, path)  

def speichere_history(hotel, daten):
    pfad = history_datei(hotel)
    eintrag = {
        "zeit": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hotel": hotel,
        "daten": daten
    }
    history = []
    if os.path.exists(pfad):
        try:
            with open(pfad, "r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except (JSONDecodeError, IOError):
            history = []
    history.append(eintrag)
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    try:
        atomic_write(pfad, history)
    except Exception:
        st.error("Fehler beim Schreiben der Historie in die Datei"); st.text(traceback.format_exc())

#Резерв

def reserve_20(wert, prozent=20):
    return math.ceil(wert * (1 + prozent / 100))

def reserve_10(wert, prozent=10):
    return math.ceil(wert * (1 + prozent / 100))
    
def main():
    hotel = st.session_state.hotel
    if "last_hotel" in st.session_state and st.session_state.last_hotel != hotel:
        st.session_state.pop(f"lager_{st.session_state.last_hotel}", None)
    st.session_state.last_hotel = hotel

    if not hotel:
        return

    lager = get_lager(hotel)
    
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
            st.session_state.aktuelle_daten = daten
            st.session_state.berechnet = True

        if st.session_state.get("berechnet"):
            st.write("📋 Die Menge an Bettwäsche und Handtüchern, die bestellt werden muss:")
            for name, menge in st.session_state.aktuelle_daten.items():
                st.write(f"- {name}: {menge}")
            st.write("❓ Speichern Sie das Ergebnis und fügen Sie den Lagerbestand hinzu? / Сохранить результат и прибавить запасы на склад?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Speichern", key="blau_speichern"):
                    lager = get_lager(hotel)
                    daten = st.session_state.get("aktuelle_daten", {})
                    for name, menge in daten.items():
                        lager[name] = lager.get(name, 0) + menge
                    set_lager(hotel, lager)
                    speichere_history(hotel, daten)
                    st.success("✅ Gespeichert")
                    st.session_state.berechnet = False  
            with col2:
                if st.button("✖️ Nicht speichern", key="blau_nicht_speichern"):
                    st.info("✖️ Nicht gespeichert")
                    st.session_state.berechnet = False  

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
            st.session_state.aktuelle_daten = daten
            st.session_state.berechnet = True

        if st.session_state.get("berechnet"):
            st.write("❓ Speichern Sie das Ergebnis und fügen Sie den Lagerbestand hinzu? / Сохранить результат и прибавить запасы на склад?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Speichern", key="oben_speichern"):
                    lager = get_lager(hotel)
                    daten = st.session_state.get("aktuelle_daten", {})
                    for name, menge in daten.items():
                        lager[name] = lager.get(name, 0) + menge
                    set_lager(hotel, lager)
                    speichere_history(hotel, daten)
                    st.success("✅ Gespeichert")
                    st.session_state.berechnet = False  
            with col2:
                if st.button("✖️ Nicht speichern", key="oben_nicht_speichern"):
                    st.info("✖️ Nicht gespeichert")
                    st.session_state.berechnet = False

    else:
        st.error("Hotel nicht gefunden, überprüfen Sie den Namen / Отель не найден, проверьте название")

#Склад

def zeige_lager(hotel):
    lager = get_lager(hotel)
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
    history = list(reversed(history))
    st.write("⏳ Auftragsverlauf / История заказов:")
    for eintrag in history:
        zeit = eintrag.get("zeit", "die Zeit ist unbekannt")
        hotel_ = eintrag.get("hotel", "das Hotel ist unbekannt")
        daten = eintrag.get("daten", {})
        st.write(f"- [{zeit}] Hotel: {hotel_}")
        for name, menge in daten.items():
            st.write(f"    {name}: {menge}")
        st.write("")

#Вычет со склада

def verbrauch_berechnen(hotel, zimmer_klein, zimmer_gross):
    lager = get_lager(hotel)
    daten = {}
    tatsächlich_verbraucht = {}
    fehlende = []
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

    for name, menge in daten.items():
        verfügbar = lager.get(name, 0)
        if verfügbar >= menge:
            lager[name] -= menge
            tatsächlich_verbraucht[name] = -menge
        elif verfügbar > 0:
            lager[name] = 0
            tatsächlich_verbraucht[name] = -verfügbar
            fehlende.append(f"{name} (nur {verfügbar} von {menge} verfügbar)")
        else:
            fehlende.append(f"{name} (nicht verfügbar, benötigt: {menge})")

    if tatsächlich_verbraucht:
        set_lager(hotel, lager)
        speichere_history(hotel, tatsächlich_verbraucht)
        st.success("✅ Folgende Mengen wurden vom Lager abgezogen:")
        for name, menge in tatsächlich_verbraucht.items():
            st.write(f"- {name}: {-menge}")
    else:
        st.warning("⚠️ Keine Artikel konnten abgezogen werden")

    if fehlende:
        st.error("❌ Nicht ausreichend im Lager:")
        for f in fehlende:
            st.write(f"- {f}")

#Меню

st.sidebar.title("▫️Aktion auswählen:")
menu = st.sidebar.radio("", (
    "0 – 🪫Vom Lager abschreiben  / Списать со склада",
    "1 – 🔋Wäsche berechnen / Рассчитать белье",
    "2 – 📦Lagerreste anzeigen / Показать остатки на складе",
    "3 – ⏳Auftragsverlauf anzeigen / Показать историю заказов",
    "4 – 🖋️ Lager manuell bearbeiten / Редактировать склад вручную"
))

if "last_menu" not in st.session_state:
    st.session_state.last_menu = None
if st.session_state.last_menu != menu:
    st.session_state.berechnet = False
    st.session_state.last_menu = menu

if menu.startswith("1"):
    hotel = st.session_state.hotel
    if hotel:
        main()
    else:
        st.warning("Bitte wählen Sie ein Hotel")

elif menu.startswith("2"):
    hotel = st.session_state.hotel
    if hotel:
        zeige_lager(hotel)
    else:
        st.warning("Bitte wählen Sie ein Hotel")

elif menu.startswith("3"):
    hotel = st.session_state.hotel
    if hotel:
        zeige_history(hotel)
    else:
        st.warning("Bitte wählen Sie ein Hotel")

elif menu.startswith("0"):
    hotel = st.session_state.hotel
    if hotel:
        zimmer_klein = st.number_input("🔹 Wie viele kleine Zimmer wurden gereinigt? / Сколько маленьких комнат было убрано?", min_value=0, step=1)
        zimmer_gross = st.number_input("🔷 Wie viele große Zimmer wurden gereinigt? / Сколько больших комнат было убрано?", min_value=0, step=1)
        if st.button("Vom Lager abschreiben / Списать со склада"):
            verbrauch_berechnen(hotel, zimmer_klein, zimmer_gross)
    else:
        st.warning("Bitte wählen Sie ein Hotel")

elif menu.startswith("4"):
    hotel = st.session_state.hotel
    if not hotel:
        st.warning("Bitte wählen Sie ein Hotel")
    else:
        st.subheader("✏️ Lager manuell bearbeiten / Редактировать склад вручную")

        lager = get_lager(hotel)

        if not lager:
            st.info("📭 Lager ist leer. Keine Daten zum Bearbeiten")
        else:
            with st.form("lager_editor_form"):
                edited_lager = {}
                st.write("📅 Datum der letzten Änderung / Дата последнего изменения:")
                zeit = lager.get("__zeit", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                neue_zeit = st.text_input("⏱️ Änderbares Zeitfeld (YYYY-MM-DD HH:MM:SS):", value=zeit)

                st.write("📦 Lagerdaten / Данные склада:")

                for key, value in lager.items():
                    if key == "__zeit":
                        continue
                    neue_menge = st.number_input(f"{key}:", min_value=0, value=value, step=1)
                    edited_lager[key] = neue_menge

                submitted = st.form_submit_button("💾 Speichern / Сохранить")
                if submitted:
                    edited_lager["__zeit"] = neue_zeit.strip() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    set_lager(hotel, edited_lager)
                    st.success("✅ Lager wurde gespeichert")

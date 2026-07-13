# Igor's Food Tracker — Projektna dokumentacija

**Namen tega dokumenta:** popoln pregled aplikacije — kaj je zgrajeno, zakaj so bile izbrane določene tehnologije, kako je vse povezano, in kako nadaljevati/popravljati v prihodnje. Piši ga kot referenco, na katero se vrneš, ko se po daljšem premoru spomniš, "kaj sem pravzaprav naredil in zakaj".

---

## 1. Kaj aplikacija dela (na kratko)

Osebna aplikacija za sledenje prehrani in energijskemu saldu:
- Obkljukaš živila/obroke, ki si jih pojedel, z vneseno količino (grami ali kosi)
- Aplikacija izračuna kalorije, beljakovine, maščobe, ogljikove hidrate in mikrohranila (železo, B12, vitamin D, omega-3)
- Iz Garmin Connect računa pridobi porabljene kalorije (aktivnost + BMR)
- Prikaže **saldo**: vnos hrane − poraba

Namenjena je izključno tebi (en uporabnik), ne gre za javno/tržno aplikacijo.

---

## 2. Arhitektura — helikopterski pogled

```
                    TVOJ BRSKALNIK / TELEFON
                            │
                            ▼
              FRONTEND (React + TypeScript)
              gostuje na: Netlify
              naslov: https://[ime].netlify.app
                            │
                    (HTTP klici, CORS)
                            │
                            ▼
              BACKEND (Python + FastAPI)
              gostuje na: Render
              naslov: https://igors-food-tracker.onrender.com
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
      USDA FoodData   Open Food Facts   Garmin Connect
      Central API     API               (python-garminconnect)
      (osnovna živila) (pakirani izdelki) (poraba kalorij)
```

**Zakaj ločen frontend in backend (ne eno samo)?**
- Frontend (brskalnik) ne sme neposredno klicati Garmina, ker bi moral tvoje geslo hraniti v kodi, ki jo vidi vsak, ki odpre stran (nevarno).
- Backend teče na strežniku, kjer so občutljivi podatki (API ključi, Garmin geslo) skriti v okoljskih spremenljivkah, nikoli vidni uporabniku.

---

## 3. Zakaj te tehnologije (in ne kakšne druge)

| Tehnologija | Vloga | Zakaj ta izbira |
|---|---|---|
| **Python + FastAPI** | Backend | Enostaven za pisanje API-jev, hitro se poveže z zunanjimi API-ji (USDA, Garmin), dobra podpora za async klice |
| **React + TypeScript** | Frontend | Standarden, razširjen način za interaktivne spletne strani; TypeScript doda preverjanje tipov, kar zmanjša napake pri povezavi s podatki iz backend-a |
| **Vite** | Orodje za gradnjo frontend-a | Hitrejši in enostavnejši od starejših orodij (npr. Create React App), standarden izbor za nove React projekte |
| **JSON datoteke (namesto baze)** | Shranjevanje podatkov | Za enega uporabnika in ~200 zapisov je prava baza (MySQL, PostgreSQL) nepotreben overkill — JSON je enostaven za branje/pisanje, brez nastavitve in vzdrževanja |
| **GitHub** | Shranjevanje/verzioniranje kode | (1) varnostna kopija kode, (2) zgodovina sprememb, (3) **obvezen** vmesni korak za avtomatski deploy na Render/Netlify — oba se povežeta neposredno z GitHub repozitorijem |
| **Render** | Gostovanje backend-a | Eno redkih brezplačnih/poceni okolij, ki dejansko **poganja** Python kodo 24/7 (za razliko od Netlify ali Google Drive, ki gostita samo statične datoteke) |
| **Netlify** | Gostovanje frontend-a | Specializiran za statične/frontend strani (React, Vite), avtomatski deploy ob vsakem push-u na GitHub, brezplačen za osebno uporabo |
| **python-garminconnect** | Knjižnica za Garmin | Odprtokodna knjižnica, ki že rešuje zapleteno avtentikacijo in komunikacijo z Garmin strežniki — brez nje bi bilo treba to pisati od začetka |
| **python-dotenv** | Branje `.env` datotek | Python privzeto ne bere `.env` datotek samodejno — ta knjižnica omogoči `load_dotenv()`, da so spremenljivke (API ključi, gesla) dostopne kodi, ne da bi bile zapisane neposredno v njej |

---

## 4. Struktura projekta

```
igors-food-tracker/
├── backend/
│   ├── main.py                  — FastAPI aplikacija, endpointi (/health, /meals, /foods, /daily-log)
│   ├── garmin_service.py        — prijava v Garmin, pridobitev porabljenih kalorij, lazy cache
│   ├── nutrition_service.py     — klici USDA in Open Food Facts API-jev
│   ├── seed_foods.py            — enkratna skripta, ki napolni foods.json s ~165 živili
│   ├── .venv/                   — Python virtualno okolje (paketi tega projekta, ločeno od ostalih)
│   ├── data/
│   │   ├── foods.json           — knjižnica živil (165 vnosov, na 100g ali 1 kos)
│   │   ├── meals.json           — sestavljeni obroki (11 obrokov, s količinami)
│   │   ├── daily-log.json        — dnevni vnos (kaj si danes obkljukal)
│   │   ├── garmin-cache.json     — shranjena Garmin poraba (osveži se, ko je stara >12h)
│   │   └── daily-summary.json    — izračunan povzetek (vnos, poraba, saldo)
│   ├── requirements.txt          — seznam Python paketov (fastapi, uvicorn, garminconnect, ...)
│   └── .env                      — USDA_API_KEY, GARMIN_EMAIL, GARMIN_PASSWORD (NIKOLI na GitHub)
├── frontend/
│   ├── src/
│   │   ├── App.tsx               — glavna komponenta, checkbox seznami, prikaz salda
│   │   ├── components/           — manjše komponente (posamezne sekcije)
│   │   └── api.ts                — funkcije za klice na backend
│   ├── package.json
│   └── .env                       — VITE_API_URL (naslov backend-a)
├── .gitignore                     — pove git-u, katere datoteke NIKOLI ne smejo iti na GitHub
└── README.md
```

**V `.gitignore` (ključno za varnost):** `.env`, `__pycache__/`, `node_modules/`, `data/garmin-cache.json`

---

## 5. Podatkovni model — kako so shranjena živila in obroki

### `foods.json` — osnovna živila

Vsako živilo ima vrednosti na **standardno enoto** — 100 g (večina živil) ali 1 kos (jajca, žemlje):

```json
{
  "chicken_breast": {
    "name": "Piščančje prsi",
    "unit": "100g",
    "calories": 165,
    "protein_g": 31,
    "fat_g": 3.6,
    "carbs_g": 0,
    "iron_mg": 0.4,
    "vitamin_b12_µg": 0.3,
    "vitamin_d_µg": 0.1,
    "omega_3_g": 0.02
  }
}
```

**Zakaj enote namesto fiksnih količin (npr. "2 jajci")?** Ker omogoča preračun na **poljubno** dejansko zaužito količino (npr. "150 g piščančjih prsi", "40 g sira") — brez tega bi imel samo vnaprej določene, toge količine.

### `meals.json` — sestavljeni obroki

Vsak obrok združi več živil, vsako s svojo količino; backend preračuna in sešteje vrednosti glede na `unit` in količino vsake sestavine.

### Preračun količine (kako backend to naredi)

```
faktor = vnesena_količina / referenčna_enota
kalorije_dejanske = kalorije_na_enoto × faktor

Primer: 200 g riža, referenca je 130 kcal/100g
faktor = 200 / 100 = 2
kalorije = 130 × 2 = 260 kcal
```

---

## 6. Zgodovina gradnje — faze, ki so bile narejene

### Faza 1 — Backend osnove (FastAPI)
- Postavljena osnovna FastAPI aplikacija z endpointom `/health` (test, da backend "živi")
- CORS omogočen za `localhost:5173` (lokalni razvoj frontend-a)

### Faza 2 — Knjižnica hranil
- `nutrition_service.py`: funkciji `fetch_from_usda()` in `fetch_from_openfoodfacts()`
- Popravek podatkovnega modela: standardizirane enote (100g/1 kos) namesto fiksnih količin
- `seed_foods.py`: skripta, ki za ~165 živil poskusi USDA, nato (fallback) Open Food Facts, in **sproti** (merge) zapisuje v `foods.json`, da se pri prekinitvi ne izgubi napredek

### Faza 3 — Knjižnica obrokov
- `meals.json` z 11 sestavljenimi obroki (npr. "Losos s krompirjem", "Rižota z mesom")
- Endpoint `/meals` za branje
- Preračun: vrednosti sestavin × količina, nato seštevek v skupno vrednost obroka

### Faza 4 — Garmin integracija
- `garmin_service.py` z `python-garminconnect`
- Prijava z `GARMIN_EMAIL`/`GARMIN_PASSWORD` iz `.env`
- **Pomemben popravek med gradnjo:** prvotna zasnova ("enkrat dnevno v ozadju") ni delovala na Render free tier, ker se instanca izklopi ob neaktivnosti in nikoli ne "čaka" v ozadju. Popravljeno na **lazy fetch**: Garmin podatki se osvežijo šele, ko pride dejanska zahteva (obisk strani), in če je cache star >12 ur

### Faza 5 — Frontend (React + TypeScript)
- Postavitev z Vite
- Checkbox seznam živil/obrokov (skupine: Zajtrk, Kosilo, Večerja), brez slik (namerna odločitev za hitrejši MVP)
- Polje za vnos količine ob vsakem elementu
- Prikaz dnevnega vnosa, Garmin porabe, salda
- Kasnejši popravek: responzivna (mobilna) postavitev, ker se je prvotna zasnova na majhnih zaslonih stiskala

### Faza 6 — Povezava frontend ↔ backend
- `VITE_API_URL` v `frontend/.env`, med razvojem kaže na `http://localhost:8000`

### Faza 7 — Deploy
- Backend → **Render** (podrobnosti spodaj)
- Frontend → **Netlify** (podrobnosti spodaj)
- CORS popravek: backend je moral eksplicitno dovoliti novi Netlify naslov (ne samo `localhost`)

---

## 7. Environment spremenljivke — kje kaj gre (POMEMBNO za varnost)

| Spremenljivka | Kje NAJ bo | Kje NIKOLI ne sme biti |
|---|---|---|
| `USDA_API_KEY` | `backend/.env` (lokalno) + Render Environment Variables | Netlify, GitHub, koda |
| `GARMIN_EMAIL` / `GARMIN_PASSWORD` | `backend/.env` (lokalno) + Render Environment Variables | Netlify, GitHub, koda |
| `VITE_API_URL` | `frontend/.env` (lokalno) + Netlify Environment Variables | Render (ni backend spremenljivka) |

**Med gradnjo se je zgodila napaka:** Garmin/USDA podatki so bili pomotoma dodani tudi na Netlify — to je bilo popravljeno (izbrisano), ker Netlify gosti samo frontend in ti podatki tam ne potrebujejo biti in ne sodijo tja.

**Pravilo za prihodnost:** karkoli je "skrivnost" (geslo, ključ) in ga potrebuje **backend** logika (klici na zunanje API-je), gre na Render. Karkoli frontend potrebuje za **sestavljanje URL-jev** (kot `VITE_API_URL`) gre na Netlify.

---

## 8. Deploy proces — korak za korakom

### Backend → Render

1. Render.com → New → Web Service → poveži GitHub repozitorij
2. **Root Directory:** `backend` (ključno — Render mora vedeti, da `requirements.txt` in `main.py` nista v korenu repozitorija)
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables: `USDA_API_KEY`, `GARMIN_EMAIL`, `GARMIN_PASSWORD`
6. Render da javni URL: `https://igors-food-tracker.onrender.com`

**Opomba o free tier:** brezplačna Render instanca "zaspi" po obdobju neaktivnosti — prva zahteva po tem lahko traja 30-60 sekund ("cold start"). To je razlog, zakaj je bil potreben popravek Garmin logike (Faza 4).

### Frontend → Netlify

1. Netlify.com → Add new site → Import from GitHub → isti repozitorij
2. **Base directory:** `frontend`
3. Build command: `npm run build`
4. Publish directory: `dist` (relativno od base directory)
5. Environment Variables: `VITE_API_URL` = Render URL
6. Netlify da javni URL: `https://[ime].netlify.app`

**Pomembno:** `VITE_API_URL` se "vgradi" v kodo **ob gradnji**, ne bere se dinamično kot pri backend `.env`. Če jo spremeniš, moraš sprožiti nov build ("Clear cache and deploy site").

### CORS — zakaj je bil potreben dodaten popravek

Backend privzeto sprejema zahteve samo iz naslovov, ki so eksplicitno navedeni na "dovoljenem seznamu" (`allow_origins` v `main.py`). Ko je frontend dobil pravi javni naslov (namesto `localhost:5173`), je bilo treba ta novi naslov dodati na seznam — sicer backend zavrne zahtevo kot varnostni ukrep (prepreči, da bi katerakoli tuja stran brez dovoljenja klicala tvoj API).

---

## 9. Kako nadaljevati/popravljati v prihodnje

### Osnovni delovni tok za VSAKO spremembo:

```
1. Odpri VS Code, mapo projekta igors-food-tracker
2. Odpri Claude Code panel
3. Opiši spremembo, ki jo želiš (v naravnem jeziku)
4. Claude Code predlaga kodo — preglej diff, potrdi
5. Preizkusi lokalno (backend: uvicorn main:app --reload, frontend: npm run dev)
6. Ko deluje, reci Claude Code: "naredi commit in pushaj"
7. Render (backend) in/ali Netlify (frontend) se AVTOMATSKO znova zgradita
8. Preveri na živi strani, da sprememba deluje
```

### Pogosti scenariji

**"Želim dodati novo živilo/obrok"**
> Reci Claude Code: "Dodaj [ime živila] v foods.json, pridobi podatke iz USDA/Open Food Facts" ali za obrok: "Dodaj nov obrok v meals.json: [ime], sestavljen iz [živila + količine]"

**"Nekaj ne deluje na živi strani, a lokalno je OK"**
- Preveri Render/Netlify **Logs** (ne samo "Events") za natančno sporočilo napake
- Pogost vzrok: manjkajoča environment variable na Render/Netlify (lokalno jo imaš v `.env`, na strežniku pa ni bila nastavljena)

**"Želim spremeniti izgled strani"**
> Reci Claude Code natančno, kaj naj bo drugače (barve, razporeditev, velikost) — čim bolj konkretno, manj "naredi lepše"

**"Pozabil sem, zakaj je nekaj narejeno na določen način"**
> Vrni se v ta dokument, razdelek 6 (Zgodovina gradnje) — tam so zapisani razlogi za ključne odločitve in popravke

### Stvari, ki jih NIKOLI ne narediš sam ročno (prepusti Claude Code / infrastrukturi)
- Ne popravljaj `foods.json`/`meals.json` ročno za nove izračune — prepusti backend logiki
- Ne vpisuj gesel/ključev v kodo — vedno v `.env` (lokalno) ali Environment Variables (Render/Netlify)
- Ne commitaj `.env` datoteke — `.gitignore` to prepreči, a bodi pozoren, če ga kdaj spremeniš

---

## 10. Znane omejitve in stvari za razmislek v prihodnje

- **Render free tier "spi"** — prvi klic po neaktivnosti je počasnejši (do 50 sekund). Rešitev: nadgradnja na plačljiv Render tier, če te to moti.
- **"Rezine" in nestandardne enote** (npr. "2 rezini sira") — trenutno vnašaš v gramih; možna prihodnja izboljšava: polje `avg_piece_g` za priročne bližnjice.
- **Ni avtentikacije/prijave** — ker je aplikacija samo zate, ni potrebe po uporabniških računih; če bi kdaj to postala večuporabniška aplikacija, bi to bilo treba dodati.
- **Slike živil** — namerno izpuščene za hitrejši MVP; možna prihodnja nadgradnja.

---

## 11. Uporabne povezave

- GitHub repozitorij: `github.com/igorfurst/igors-food-tracker`
- Backend (Render): `https://igors-food-tracker.onrender.com`
- Frontend (Netlify): preveri trenutno ime na netlify.com nadzorni plošči
- USDA FoodData Central: https://fdc.nal.usda.gov/api-key-signup
- Open Food Facts API dokumentacija: https://world.openfoodfacts.org/data
- python-garminconnect: https://github.com/cyberjunky/python-garminconnect

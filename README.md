# Speech Prep Bot — Malaysia universiteti bilan speech uchun tayyorgarlik

Bu bot sizga 1 oy davomida quyidagilarda yordam beradi:
- 📚 Partnership/ta'lim mavzusidagi vocabulary (4 haftaga bo'lingan)
- 🗣 Taqdimot uchun tayyor jumla qoliplari (structures) + Claude tekshiruvi
- 🎤 **Speaking practice** — bot savol beradi, siz OVOZLI xabar bilan javob berasiz, bot ovozni matnga o'giradi va grammatika/tezlik/ravonlik bo'yicha baho beradi
- ✍️ Speech matningizni yozib, Claude'dan tuzatish va tavsiyalar olish
- ❓ Universitet paneli beradigan mumkin savollarga tayyorgarlik (matn yoki ovoz bilan javob berish mumkin)
- 📊 Progress kuzatuvi

## 🆕 **YANGI XUSUSIYATLAR** (So'nggi yangilanish)

### 🔔 Kunlik Eslatma (Daily Reminder)
- **Belgilangan vaqtda** "Bugun mashq qilmadingiz" deb avtomatik xabar yuboradi
- Sozlamalardan eslatma vaqtini o'zingiz tanlaysiz
- Muntazam mashqni qilishga urg'u qiladi

### 🎧 Talaffuz Namunasi (TTS — Text-to-Speech)
- Bot vocabulary so'zlarini **ovoz chiqarib aytib beradi**
- Siz takrorlaysiz va dinglaysiz
- Hozirgi hafta yoki oldingi haftalar so'zlarini tanlasiz
- `gtts` kutubxonasi orqali ishlaydi (allaqachon o'rnatilgan)

### ⏱️ Filler So'z Hisoblagichi
- Speaking practice'da ovozni matnga o'girganidan keyin bot **"um", "uh", "like" kabi fillerlarni sanaydi**
- Har biri necha marta ishlatilganini ko'rsatadi
- **Filler so'zlarni kamaytirish bo'yicha maslahat beradi**
- Taqdimotda rasmiylik va jonlilik uchun kerak

### 🔁 Spaced Repetition (Qayta O'rgatish)
- O'rgangan so'zlarni **unutmaslik uchun ma'lum kunlar oralig'ida qayta so'raydi**
- "Bildim" desangiz, so'z 7 kundan keyin qayta chiqadi
- "Unuttim" desangiz, 2 kundan keyin qayta chiqadi
- Ilmiy usul — xotirni mustahkamlaydi

### 🎭 To'liq Mock-Meeting Rejimi
- **Realidagi uchrashuv kabi bir nechta savolni ketma-ket beramiz** (3, 5 yoki 8 ta)
- Hamma savolga javob berganingizdan keyin **umumiy baho beradi**
- Stress ostida gapirish amaliyoti

### ⏳ Vaqt Chegarasi Bilan Mashq
- **"60 soniyada javob bering" kabi real bosim**
- Timed practice rejimida 30, 60 yoki 120 soniya tanlasiz
- Real uchrashuv kabi vaqt tugagach to'xtasiz

### 📄 Speech Eksporti (PDF/Word)
- Tuzatilgan **yakuniy matnni PDF sifatida eksport qilishiz mumkin**
- Printlash yoki sotuvlashtirish uchun
- Haftalik hisobot ham PDF sifatida yuboriladi

### 📈 Haftalik Hisobot (Weekly Report)
- **Har hafta oxirida avtomatik xulosa** — necha session, necha so'z, progress
- PDF sifatida eksport qilish mumkin
- Speaking practice'dagi rekoringlarning statistikasi: WPM, filler so'zlar, sifat

### 🗂️ Ovozli Mashqlar Tarixi
- **Barcha speaking practice sessiyalaringiz saqlanadi** — qayta ko'rish/taqqoslash
- Har birining: tarih, savol, WPM, filler count, sifat baho
- **Fluency yaxshilanayotganini ko'rish mumkin**
- PDF sifatida eksport qila olasiz

### ⚙️ Sozlamalar
- Eslatma vaqti o'zgartirim
- Filler so'zlarni kamaytirish bo'yicha maslahatlar
- Qo'llanma va yordam

---

## 1. Kerakli narsalar

- Python 3.11+ (sizda 3.13 bor, yaxshi)
- Telegram bot token (BotFather orqali)
- Google Gemini API key (aistudio.google.com) — **BEPUL**, kredit karta shart emas

## 2. Telegram bot yaratish

1. Telegram'da **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring, nom va username bering
3. Sizga beriladigan tokenni saqlab qo'ying (masalan `123456:ABC-DEF...`)

## 3. Gemini API key olish (bepul)

1. https://aistudio.google.com/app/apikey ga kiring (Google hisobingiz bilan)
2. "Create API key" tugmasini bosing
3. Kalitni saqlab qo'ying

**Eslatma:** bepul tarifda kuniga ~1500 so'rov, daqiqasiga ~15 so'rov limiti bor — shaxsiy loyiha uchun to'liq yetarli.

## 4. O'rnatish (Windows PowerShell)

```powershell
cd speech_bot
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Endi `.env` faylini oching va quyidagilarni to'ldiring:

```
TELEGRAM_BOT_TOKEN=BotFather'dan olgan tokeningiz
GEMINI_API_KEY=aistudio.google.com'dan olgan keyingiz
GEMINI_MODEL=gemini-2.5-flash
```

## 5. Ishga tushirish

```powershell
python bot.py
```

**Eslatma:** Birinchi marta "Speaking practice" yoki ovozli javobdan foydalanganingizda, dastur speech-to-text uchun kerak bo'ladigan modelni (~500 MB) avtomatik yuklab oladi — bu bir martalik jarayon, internet kerak.

## 6. Botdan foydalanish

### 📚 Vocabulary
- Joriy hafta va oldingi hafta so'zlari
- "Bildim" bosilgan so'zlar qayta chiqmaydi

### 🎧 Talaffuz Namunasi (TTS)
- So'zlarni ovozli tinglang
- Takrorlay olasiz
- Hozirgi yoki oldingi hafta tanlaysiz

### 🔁 Spaced Repetition Review
- O'rgangan so'zlarni qayta o'rganing
- Xotirni mustahkamlang
- Ilmiy interval bilan

### 🗣 Grammar Practice
- Pattern beriladi
- O'z jumla yozasiz
- Claude tekshirib baho beradi

### 🎤 Speaking Practice
- Bot savol beradi
- Siz 🎤 ovozli javob berasiz
- **Filler so'zlar avtomatik hisoblanadi**
- WPM (so'z/daqiqa) va sifat baho

### ⏱️ Timed Practice
- 30, 60 yoki 120 soniya
- Real bosim ostida gapirish
- Stressga tayyorlanish

### 🎭 Mock Meeting
- 3, 5 yoki 8 ta savollar
- Ketma-ket qayta shunday yalpi baho
- Realidagi meeting simulyatsiyasi

### ✍️ Speech Tuzatish
- Nutq matningizni yuboring
- Claude tuzatadi va tavsiyalar beradi

### ❓ Q&A Tayyorgarlik
- Bot 3 ta mumkin savol beradi
- Birini tanlaysiz
- Matn yoki ovozli javob

### 📊 Progress
- Umumiy statistika
- O'rgangan so'zlar, sessiyalar
- Turi bo'yicha bo'linish

### 📈 Haftalik Hisobot
- Haftalik xulosa
- Sessions, so'zlar, progress
- PDF sifatida eksport

### 🗂️ Voice History
- Barcha speaking sessiyalarni ko'rish
- Statistika va taraqqiy
- PDF sifatida eksport

### ⚙️ Sozlamalar
- Eslatma vaqti
- Yordam va qo'llanma
- Filler tips

## 7. Ma'lumotlar qayerda saqlanadi?

Barcha progress `speech_bot.db` (SQLite) faylida saqlanadi — kompyuteringiz papkasida:
- Learned words va next review dates
- Speaking practice recordings va analysis
- Weekly reports
- Voice history with WPM, fillers, quality scores
- User settings va reminder times

## 8. Eslatmalar

- **Muhim: talaffuz haqida.** Bot ovozni matnga aylantirib, o'sha matnni tahlil qiladi
- Filler so'zlar avtomatik sanab, maslahat beradi
- Spaced repetition ilmiy usul — xotira kuchaytiradi
- Weekly reports o'z progress'ingizni korib olishga yordam beradi
- Voice history orqali fluency yaxshilanayotganini korib olasiz
- Bot bitta odam (siz) uchun mo'ljallangan
- Gemini API bepul tarifda ishlaydi — hech qanday to'lov talab qilinmaydi

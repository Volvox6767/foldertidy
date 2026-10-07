# foldertidy 🗂️✨

**EN | Clean up your messy Downloads folder in seconds — safely, offline, with one command.**
**TR | Dağınık İndirilenler klasörünüzü saniyeler içinde, güvenle ve çevrimdışı temizler.**

Sorts files into `Pictures / Videos / Documents / Music / Archives / Programs / ...`
and finds duplicate files. **Nothing is deleted, ever** — duplicates go to a
`_duplicates` folder. **Dry-run by default** — you see the plan before anything moves.

Dosyaları `Pictures / Videos / Documents / Music / Archives / Programs / ...`
klasörlerine ayırır ve kopya (duplicate) dosyaları bulur. **Hiçbir şey asla silinmez** —
kopyalar `_duplicates` klasörüne taşınır. **Varsayılan kuru çalışma (dry-run)** — bir şey
taşınmadan önce planı görürsünüz.

```bash
python foldertidy.py                 # EN: preview ~/Downloads | TR: İndirilenler önizleme
python foldertidy.py --apply         # EN: actually organize | TR: gerçekten düzenle
python foldertidy.py ./Photos --by-month --apply
python foldertidy.py ./Messy --dedupe --apply
```

```
📁 C:\Users\you\Downloads   (organize)
  [dry] installer (1).exe  →  Programs\installer (1).exe
  [dry] report.pdf         →  Documents\report.pdf
  [dry] photo.jpg          →  Pictures\photo.jpg
  ...
  PREVIEW: 47 file(s)
  👍 looks right? run again with --apply
```

---

## 🇬🇧 English

### Why?

"I have 3,000 files in Downloads and I'm scared to touch it" — the most human
situation on Earth. Existing tools are paid, bloated, or want cloud access.

`foldertidy` is one Python file. No install, no account, no upload. It only
**moves** files into clear folders and never deletes anything.

### Safety first

| Guarantee | How |
|---|---|
| Never deletes | Duplicates are *moved* to `_duplicates/` (same relative path) |
| Preview first | Dry-run by default; add `--apply` to execute |
| Skips partial downloads | `.crdownload .part .tmp .download` are left alone |
| Skips system/hidden mess | `.git`, `node_modules`, `__pycache__` untouched |
| No name collisions | Auto-renames to `file (2).ext` instead of overwriting |
| Oldest copy wins | Duplicate groups keep the oldest file |

### Install

Python 3.9+ — that's all:

```bash
curl -LO https://raw.githubusercontent.com/Volvox6767/foldertidy/main/foldertidy.py
```

Single file, zero dependencies, works offline.

### Usage

```
python foldertidy.py [FOLDER] [--apply] [--by-month] [--by-date] [--dedupe]

FOLDER        folder to tidy (default: ~/Downloads)
--apply       really move files (default: preview only)
--by-month    Pictures also sorted into YYYY-MM subfolders
--by-date     ALL files sorted into YYYY-MM-DD subfolders
--dedupe      find duplicates → move them to _duplicates/
```

Examples:

```bash
python foldertidy.py                              # preview Downloads
python foldertidy.py --apply                      # organize Downloads
python foldertidy.py D:\Camera --by-month --apply # photos by month
python foldertidy.py ./Desktop --dedupe --apply   # clear duplicate clutter
```

Categories: Pictures, Videos, Documents, Music, Archives, Programs, Code,
Fonts, Torrents, Others — 100+ extensions recognized.

### FAQ

**Can it delete my files?** No. It only moves. `--apply` + `_duplicates/` folder. Delete that folder yourself when you're sure.

**Is my data sent anywhere?** No. 100 % offline.

**What about files with no extension?** Left in place — better safe than sorry.

---

## 🇹🇷 Türkçe

### Neden?

"İndirilenler'de 3.000 dosya var, dokunmaya korkuyorum" — dünyanın en insani
durumu. Mevcut araçlar ya ücretli, ya şişkin, ya da bulut erişimi istiyor.

`foldertidy` tek bir Python dosyasıdır. Kurulum yok, hesap yok, yükleme yok.
Yalnızca dosyaları anlaşılır klasörlere **taşır** ve hiçbir şeyi silmez.

### Önce güvenlik

| Garanti | Nasıl? |
|---|---|
| Asla silmez | Kopyalar `_duplicates/` klasörüne *taşınır* (aynı göreli yol) |
| Önce önizleme | Varsayılan dry-run; uygulamak için `--apply` |
| Yarım indirmelere dokunmaz | `.crdownload .part .tmp .download` dosyaları atlanır |
| Sistem/gizli klasörlere dokunmaz | `.git`, `node_modules`, `__pycache__` olduğu gibi kalır |
| İsim çakışması yok | Üzerine yazmak yerine `dosya (2).ext` olarak yeniden adlandırır |
| En eski kopya kalır | Kopya gruplarında en eski dosya yerinde tutulur |

### Kurulum

Python 3.9+ — hepsi bu:

```bash
curl -LO https://raw.githubusercontent.com/Volvox6767/foldertidy/main/foldertidy.py
```

Tek dosya, sıfır bağımlılık, çevrimdışı çalışır.

### Kullanım

```
python foldertidy.py [KLASÖR] [--apply] [--by-month] [--by-date] [--dedupe]

KLASÖR        düzenlenecek klasör (varsayılan: ~/Downloads)
--apply       dosyaları gerçekten taşı (varsayılan: sadece önizleme)
--by-month    Pictures ayrıca YYYY-MM alt klasörlerine ayrılır
--by-date     TÜM dosyalar YYYY-MM-DD alt klasörlerine ayrılır
--dedupe      kopyaları bulur → _duplicates/ klasörüne taşır
```

Örnekler:

```bash
python foldertidy.py                              # Downloads önizleme
python foldertidy.py --apply                      # Downloads'ı düzenle
python foldertidy.py D:\Kamera --by-month --apply # fotoğraflar aylara göre
python foldertidy.py ./Masaüstü --dedupe --apply  # kopya kalabalığını temizle
```

Kategoriler: Pictures, Videos, Documents, Music, Archives, Programs, Code,
Fonts, Torrents, Others — 100+ uzantı tanınır.

### SSS

**Dosyalarımı silebilir mi?** Hayır. Sadece taşır. `--apply` + `_duplicates/` klasörü. Emin olduğunuzda o klasörü kendiniz silebilirsiniz.

**Verilerim bir yere gönderiliyor mu?** Hayır. %100 çevrimdışı.

**Uzantısı olmayan dosyalar?** Yerinde bırakılır — tedbiri elden bırakmamak gerek.

---

Made with ❤ by **Ahmet Gedik** — [instagram.com/ahmetgedik67](https://www.instagram.com/ahmetgedik67)
Follow on Instagram for more free everyday tools.
Daha fazla ücretsiz günlük araç için Instagram'da takip edin.

License / Lisans: [MIT](LICENSE)

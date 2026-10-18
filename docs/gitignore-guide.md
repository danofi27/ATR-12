2. Explicația fiecărei secțiuni
2.1 Python
Ce ignoră	De ce
__pycache__/	Cache Python (se regenerează automat)
*.pyc, *.pyo	Fișiere compilate
build/, dist/	Fișiere de build
*.egg-info/	Metadata pachete
.venv/, venv/	Medii virtuale (fiecare are propriul)
2.2 Sisteme de operare
Ce ignoră	De ce
.DS_Store	Fișier macOS (inutil pentru alții)
Thumbs.db	Fișier Windows (inutil pentru alții)
*~	Backup Linux (temporar)
2.3 Date și figuri
Ce ignoră	De ce
data/raw/	Date brute (mari, regenerabile)
*.h5, *.hdf5	Fișiere HDF5 (mari)
*.npy, *.npz	Arrays NumPy (mari)
*.pkl	Pickle (mari, potențial nesigure)
2.4 Credențiale
Ce ignoră	De ce
*.key, *.pem	Chei private (securitate)
secrets.json	Date sensibile
.env.local	Configurare locală
2.5 IDE
Ce ignoră	De ce
.vscode/	Configurare VS Code (personală)
.idea/	Configurare PyCharm (personală)
*.sublime-*	Configurare Sublime (personală)
3. Cum să creezi fișierul
Metoda 1: Din terminal
bash

cd ART-12D
touch .gitignore
nano .gitignore

Apoi copiază conținutul de mai sus și salvează (Ctrl+O, Enter, Ctrl+X).
Metoda 2: Din GitHub

Când creezi repository-ul, GitHub oferă opțiunea „Add .gitignore". Selectează Python din listă. GitHub va crea automat un .gitignore standard.
Metoda 3: Manual

    Deschide Notepad (Windows) sau TextEdit (Mac)

    Copiază conținutul

    Salvează ca .gitignore (cu punct la început)

    Asigură-te că nu are extensie .txt

4. Cum să verifici că funcționează
Pasul 1: Verifică statusul Git
bash

git status

Ar trebui să vezi doar fișierele pe care vrei să le urmărești (nu __pycache__, nu .DS_Store).
Pasul 2: Verifică ce este ignorat
bash

git status --ignored

Aceasta îți arată ce fișiere sunt ignorate.
Pasul 3: Testează

Creează un fișier temporar:
bash

echo "test" > test.tmp
git status

test.tmp nu ar trebui să apară (este ignorat).
5. Ce să NU pui în .gitignore
5.1 Nu ignora fișiere esențiale

Nu ignora:

    README.md — esențial pentru repository

    LICENSE — esențial pentru legalitate

    requirements.txt — esențial pentru instalare

    CITATION.cff — esențial pentru citare

    src/*.py — codul tău

    figures/*.png — dacă vrei să le arăți pe GitHub

5.2 Nu ignora ce vrei să partajezi

Exemplu: Dacă vrei ca figurile să fie vizibile pe GitHub, nu ignora figures/*.png.

Decizia ta:

    Vrei figuri pe GitHub? → Nu le ignora

    Nu vrei figuri pe GitHub? → Ignoră-le (figures/*.png)

6. Structura finală a repository-ului
text

ART-12D/
│
├── .gitignore              ← Fișierul de ignorare
├── README.md               ← Descriere
├── LICENSE                 ← MIT License
├── requirements.txt        ← Dependențe
├── CITATION.cff            ← Cum să citezi
│
├── src/                    ← Codul sursă
│   ├── __init__.py
│   ├── config.py
│   ├── akashic_field.py
│   ├── consciousness.py
│   ├── fermions.py
│   ├── temporal_modes.py
│   ├── empathy.py
│   ├── word_excitation.py
│   └── simulation.py
│
├── notebooks/              ← Jupyter notebooks
│   └── 01_full_simulation.ipynb
│
└── figures/                ← Figuri generate
    └── (se generează automat)

7. Comenzi Git complete

După ce ai creat toate fișierele (inclusiv .gitignore):
bash

# 1. Inițializează Git
git init

# 2. Adaugă toate fișierele
git add .

# 3. Verifică ce este adăugat
git status

# 4. Commit
git commit -m "Initial commit: ART-12D simulation code"

# 5. Conectează la GitHub
git remote add origin https://github.com/[username]/ART-12D.git

# 6. Trimite pe GitHub
git branch -M main
git push -u origin main

8. Rezumat

Ce pui în .gitignore:

    Python: __pycache__/, *.pyc, .venv/, build/, dist/

    OS: .DS_Store, Thumbs.db, *~

    Date mari: *.h5, *.npy, *.pkl

    Credențiale: *.key, *.pem, secrets.json

    IDE: .vscode/, .idea/, *.sublime-*

Ce NU pui în .gitignore:

    README.md

    LICENSE

    requirements.txt

    CITATION.cff

    src/*.py

    figures/*.png (dacă vrei să le arăți)

Timp: 5 minute.

Beneficiu: Repository curat, fără fișiere inutile.
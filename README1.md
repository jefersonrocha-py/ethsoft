ethsoft-flask/
│
├── README.md                      # Markdown da Aplicação
├── requirements.txt               # Libs da Aplicação
├── Dockerfile                     # Dockerfile para gerar image
├── docker-compose.yml             # Docker Compose para deploy
├── database.py                    # Banco de Dados SQLite
├── units.py                       # Lista com as Unidades
├── app.py                         # Script Principal
├── data/                          # Diretório de Files
│   ├── status_history.csv         # (inicialmente vazio ou não existe)
│   ├── users.db                   # (será criado automaticamente)
│   └── daily-reports/             # (PDFs gerados)
├── templates/                     # Diretorio dos Templates
│   ├── base.html                  # Base da aplicação
│   ├── login.html                 # Tela de Login
│   ├── register.html              # Tela de Registro
│   ├── welcome.html               # Tela de Boas Vindas
│   ├── status.html                # Tela de Status
│   └── dashboard.html             # Tela de Dashboard
└── static/                        # Diretório da Estilização
    ├── css/                       #  Pasta com os arquivos
    │   └── styles.css             #  Estilo da Tela Welcome,Status e Dashboard
    │   └── toggles.css            #  Botão toggle do status e dark mode
    │   └── login.css              #  Estilo da tela de login e registro
    ├── js/                        # Diretório JS
    │   └── theme-toggle.js        # Script Javascript para o Botão Switch Theme
    └── particles-config.json      # Json para o Particles.js

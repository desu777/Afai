# Tutorial: Deploy Aquaforest RAG na VPS

Kompletny poradnik krok po kroku do wdrożenia aplikacji [Aquaforest RAG](https://github.com/desu777/aquaforest-rag) na VPS z domeną `afai.life`.

## Krok 1: Przygotowanie serwera (jako root)

```bash
# Aktualizacja systemu
apt update && apt upgrade -y

# Instalacja podstawowych narzędzi
apt install -y curl wget git vim nginx python3 python3-pip python3-venv nodejs npm build-essential

# Weryfikacja wersji
python3 --version
node --version
npm --version
```

## Krok 2: Konfiguracja Node.js (najnowsza LTS)

```bash
# Instalacja Node.js 20.x LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Weryfikacja
node --version
npm --version
```

## Krok 3: Klonowanie repozytorium

```bash
# Przejście do katalogu docelowego
cd /var/www/

# Klonowanie repo
git clone https://github.com/desu777/aquaforest-rag.git
cd aquaforest-rag

# Sprawdzenie struktury
ls -la
```

## Krok 4: Konfiguracja backendu (Python/FastAPI)

```bash
# Tworzenie virtual environment
cd /var/www/aquaforest-rag
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności
pip install --upgrade pip
pip install -r requirements.txt

# Tworzenie pliku .env na podstawie .env.example
cp .env.example .env
vim .env
```

### Konfiguracja .env:
```bash
# API Keys (MUSISZ UZYSKAĆ TE KLUCZE)
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here

# Pinecone Configuration
PINECONE_INDEX_NAME=aqua
PINECONE_ENVIRONMENT=us-east-1-aws

# OpenAI Configuration
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_TOKENS=16384
OPENAI_TEMPERATURE=0.3

# App Configuration
DEFAULT_K_VALUE=12
ENHANCED_K_VALUE=12
CONFIDENCE_THRESHOLD=0.5
SUPPORTED_LANGUAGES=pl,en,de,fr,es,it

# Server Configuration
CORS_ORIGINS=https://afai.life,https://www.afai.life,http://afai.life,http://localhost:3000

# Debug
TEST_ENV=false
```

## Krok 5: Test backendu

```bash
cd /var/www/aquaforest-rag
source venv/bin/activate

# Test uruchomienia
python src/server.py

# Powinno uruchomić się na porcie 2103
# Zatrzymaj: Ctrl+C
```

## Krok 6: Konfiguracja frontendu

### Rozwiązanie problemów TypeScript:

```bash
cd /var/www/aquaforest-rag/frontend

# Instalacja zależności
npm install

# Utwórz plik typów dla Vite
cat > src/vite-env.d.ts << 'EOF'
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_TEST_ENV: string
  readonly VITE_TEST_ACCESS: string
  readonly VITE_ADMIN_ACCESS: string
  readonly VITE_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
EOF

# Napraw tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": false,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": false,
    "types": ["vite/client"]
  },
  "include": ["src"],
  "exclude": ["node_modules"]
}
EOF

# Tworzenie pliku środowiskowego dla frontend
cat > .env.local << 'EOF'
VITE_API_URL=https://afai.life:2103
VITE_API_BASE_URL=https://afai.life:2103
VITE_TEST_ENV=false
VITE_TEST_ACCESS=test123
VITE_ADMIN_ACCESS=admin456
EOF

# Build produkcyjny
npm run build

# Sprawdzenie czy build się udał
ls -la dist/
```

## Krok 7: Konfiguracja Nginx z SSL

```bash
# Backup domyślnej konfiguracji
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# Tworzenie konfiguracji dla afai.life
vim /etc/nginx/sites-available/afai.life
```

### Zawartość pliku `/etc/nginx/sites-available/afai.life`:
```nginx
# Przekierowanie HTTP -> HTTPS
server {
    listen 80;
    server_name afai.life www.afai.life;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name afai.life www.afai.life;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/afai.life/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/afai.life/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend - React app
    location / {
        root /var/www/aquaforest-rag/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    
    # Backend API - proxy do FastAPI
    location /chat {
        proxy_pass http://localhost:2103;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Pozostałe API endpoints
    location ~ ^/(feedback|analytics|health|debug) {
        proxy_pass http://localhost:2103;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Statyczne pliki z cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/aquaforest-rag/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff always;
    }
}
```

### Aktywacja konfiguracji Nginx:
```bash
# Usunięcie domyślnej strony
rm /etc/nginx/sites-enabled/default

# Aktywacja naszej konfiguracji
ln -s /etc/nginx/sites-available/afai.life /etc/nginx/sites-enabled/

# Test konfiguracji
nginx -t

# Restart Nginx
systemctl restart nginx
systemctl enable nginx
```

## Krok 8: Generowanie certyfikatu SSL

```bash
# Wygeneruj certyfikat używając certbot
certbot --nginx -d afai.life -d www.afai.life

# Lista certyfikatów
certbot certificates

# Sprawdź automatyczne odnawianie
systemctl enable certbot.timer
systemctl start certbot.timer

# Test dry-run odnawiania
certbot renew --dry-run
```

## Krok 9: Tworzenie systemd service dla backendu

```bash
vim /etc/systemd/system/aquaforest-backend.service
```

### Zawartość service:
```ini
[Unit]
Description=Aquaforest RAG Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/aquaforest-rag
Environment=PATH=/var/www/aquaforest-rag/venv/bin
ExecStart=/var/www/aquaforest-rag/venv/bin/python src/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Aktywacja service:
```bash
# Reload systemd
systemctl daemon-reload

# Włączenie i uruchomienie
systemctl enable aquaforest-backend
systemctl start aquaforest-backend

# Sprawdzenie statusu
systemctl status aquaforest-backend
```

## Krok 10: Konfiguracja firewall

```bash
# Instalacja UFW (jeśli nie ma)
apt install -y ufw

# Podstawowe reguły
ufw default deny incoming
ufw default allow outgoing

# Zezwolenie na SSH, HTTP, HTTPS
ufw allow ssh
ufw allow 80
ufw allow 443

# Opcjonalnie: bezpośredni dostęp do API (dla debugowania)
ufw allow 2103

# Włączenie firewall
ufw enable

# Sprawdzenie statusu
ufw status
```

## Krok 11: Weryfikacja deploymentu

```bash
# Sprawdzenie statusów
systemctl status nginx
systemctl status aquaforest-backend

# Sprawdzenie portów
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :2103

# Test API bezpośrednio
curl http://localhost:2103/health

# Test przez HTTPS
curl https://afai.life/health

# Test certyfikatu
curl -I https://afai.life
```

## Krok 12: Logi i monitoring

```bash
# Logi backendu
journalctl -u aquaforest-backend -f

# Logi Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Sprawdzenie bazy danych
ls -la /var/www/aquaforest-rag/aquaforest_analytics.db
```

## Krok 13: Aktualizacja DNS

Upewnij się, że rekord DNS dla `afai.life` wskazuje na IP twojego VPS:
```
A    afai.life        YOUR_VPS_IP
A    www.afai.life    YOUR_VPS_IP
```

## Gotowe! 🎉

Aplikacja powinna być dostępna pod adresem `https://afai.life`

### Funkcjonalności:
- ✅ HTTPS z automatycznym przekierowaniem
- ✅ Frontend React z interfejsem chat
- ✅ Backend FastAPI z AI workflow
- ✅ Baza danych SQLite z analityką
- ✅ Automatyczne odnawianie certyfikatu SSL
- ✅ Systemd service dla backendu
- ✅ Nginx reverse proxy

### Następne kroki (opcjonalne):
1. **Backup**: Skonfiguruj automatyczne backupy bazy danych
2. **Monitoring**: Dodaj narzędzia monitoringu (htop, netdata)
3. **Updates**: Skonfiguruj skrypt do aktualizacji aplikacji
4. **Load Balancing**: W przypadku większego ruchu

### Rozwiązywanie problemów:
- Sprawdź logi: `journalctl -u aquaforest-backend`
- Restart serwisów: `systemctl restart aquaforest-backend nginx`
- Sprawdź porty: `netstat -tlnp`
- Test API: `curl https://afai.life/health`
- Test SSL: [SSL Labs Test](https://www.ssllabs.com/ssltest/)

### Struktura aplikacji:
```
/var/www/aquaforest-rag/
├── src/                    # Backend Python/FastAPI
├── frontend/              # Frontend React/TypeScript
│   └── dist/             # Built frontend files
├── data/                 # Product data JSON
├── .env                  # Backend environment variables
├── aquaforest_analytics.db # SQLite database
└── requirements.txt      # Python dependencies
```

### Użyte technologie:
- **Backend**: Python, FastAPI, LangGraph, OpenAI, Pinecone
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Database**: SQLite
- **Server**: Nginx, Certbot (Let's Encrypt)
- **Deployment**: systemd, UFW firewall

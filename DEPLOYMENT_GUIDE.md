# 🚀 Aquaforest RAG - Deployment od Zera na VPS

Kompletny przewodnik deployment na VPS z dwoma domenami:
- **Backend**: `aiagent.aquaforest.eu` (port 2103)
- **Frontend**: `af.aquaforest.eu` (port 80/443)
- **External ENV**: `/var/aquaforest_env/.env`

## Krok 1: Przygotowanie VPS (Ubuntu/Debian)

```bash
# Aktualizacja systemu
apt update && apt upgrade -y

# Instalacja podstawowych narzędzi
apt install -y curl wget git vim nginx python3 python3-pip python3-venv nodejs npm build-essential certbot python3-certbot-nginx

# Instalacja Node.js 20.x LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Weryfikacja wersji
python3 --version
node --version
npm --version
```

## Krok 2: Tworzenie struktury katalogów

```bash
# Główny katalog aplikacji
mkdir -p /var/www/aquaforest-rag
cd /var/www/aquaforest-rag

# Katalog dla external env
mkdir -p /var/aquaforest_env
```

## Krok 3: Klonowanie repozytorium

```bash
# Klonowanie repozytorium
cd /var/www/
git clone https://github.com/desu777/aquaforest-rag.git
cd aquaforest-rag

# Sprawdzenie struktury
ls -la
```

## Krok 4: Konfiguracja External ENV

```bash
# Skopiuj plik .env.example do external lokalizacji
cp backend/.env.example /var/aquaforest_env/.env

# Edytuj plik env z właściwymi kluczami API
vim /var/aquaforest_env/.env
```

### Przykładowa konfiguracja `/var/aquaforest_env/.env`:

```env
# ==========================================
# 🔧 DEVELOPMENT CONFIGURATION
# ==========================================
TEST_ENV=false
DISABLE_BUSINESS_MAPPINGS=false
ENABLE_COMPETITORS_ONLY=false

# ==========================================
# 🗄️ PINECONE VECTOR DATABASE
# ==========================================
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=aquaforest
PINECONE_ENVIRONMENT=us-east-1

# ==========================================
# 🤖 OPENROUTER API CONFIGURATION (Per-Node)
# ==========================================
INTENT_DETECTOR_API=sk-or-v1-your_key_here
BUSINESS_REASONER_API=sk-or-v1-your_key_here
QUERY_OPTIMIZER_API=sk-or-v1-your_key_here
RESPONSE_FORMATTER_API=sk-or-v1-your_key_here
FOLLOW_UP_API=sk-or-v1-your_key_here

# Model Selection per Component
INTENT_DETECTOR_MODEL=google/gemini-2.5-flash-preview-05-20
BUSINESS_REASONER_MODEL=google/gemini-2.5-flash-preview-05-20
QUERY_OPTIMIZER_MODEL=google/gemini-2.5-flash-preview-05-20
RESPONSE_FORMATTER_MODEL=google/gemini-2.5-flash-preview-05-20
FOLLOW_UP_MODEL=google/gemini-2.0-flash-001

# ==========================================
# 🔑 OPENAI CONFIGURATION
# ==========================================
OPENAI_API_KEY=sk-proj-your_openai_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=16384

# ==========================================
# 🌐 CORS & SERVER CONFIGURATION
# ==========================================
CORS_ORIGINS=https://af.aquaforest.eu,https://aiagent.aquaforest.eu,http://localhost:3000

# ==========================================
# 🔒 RATE LIMITING & SECURITY
# ==========================================
ENABLE_RATE_LIMITING=true
RATE_LIMIT_STORAGE=memory://
TIER1_RATE_LIMIT=20/minute
TIER2_RATE_LIMIT=60/minute
TIER3_RATE_LIMIT=200/minute

# ==========================================
# 💬 FACEBOOK MESSENGER INTEGRATION
# ==========================================
MESSENGER_ON=false
```

## Krok 5: Konfiguracja Backendu

```bash
# Przejście do katalogu backend
cd /var/www/aquaforest-rag/backend

# Tworzenie virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności
pip install --upgrade pip
pip install -r requirements.txt

# Test backendu z external env
ENV_FILE_PATH="/var/aquaforest_env/.env" python src/server.py
```

## Krok 6: Konfiguracja Frontendu

```bash
# Przejście do katalogu frontend
cd /var/www/aquaforest-rag/frontend

# Instalacja zależności
npm install

# Tworzenie pliku środowiskowego dla production
cat > .env.production << 'EOF'
VITE_API_URL=https://aiagent.aquaforest.eu
VITE_API_BASE_URL=https://aiagent.aquaforest.eu
VITE_TEST_ENV=false
VITE_TEST_ACCESS=aqua18
VITE_ADMIN_ACCESS=admin18
EOF

# Build produkcyjny
npm run build

# Sprawdzenie czy build się udał
ls -la dist/
```

## Krok 7: Konfiguracja Nginx z SSL dla dwóch domen

```bash
# Backup domyślnej konfiguracji
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# Usunięcie domyślnej strony
rm /etc/nginx/sites-enabled/default

# Konfiguracja dla frontendu (af.aquaforest.eu)
cat > /etc/nginx/sites-available/af.aquaforest.eu << 'EOF'
# Frontend - af.aquaforest.eu
server {
    listen 80;
    server_name af.aquaforest.eu www.af.aquaforest.eu;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name af.aquaforest.eu www.af.aquaforest.eu;

    # SSL Configuration (będzie dodane przez certbot)
    
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
    
    # Statyczne pliki z cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/aquaforest-rag/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff always;
    }
}
EOF

# Konfiguracja dla backendu (aiagent.aquaforest.eu)
cat > /etc/nginx/sites-available/aiagent.aquaforest.eu << 'EOF'
# Backend API - aiagent.aquaforest.eu
server {
    listen 80;
    server_name aiagent.aquaforest.eu www.aiagent.aquaforest.eu;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aiagent.aquaforest.eu www.aiagent.aquaforest.eu;

    # SSL Configuration (będzie dodane przez certbot)
    
    # ========================================
    # 🚀 STREAMING ENDPOINT - NO BUFFERING
    # ========================================
    location /chat/stream {
        proxy_pass http://localhost:2103;
        proxy_http_version 1.1;
        
        # Wyłącz wszystkie buforowanie dla streaming
        proxy_buffering off;
        proxy_cache off;
        proxy_request_buffering off;
        
        # Zwiększ timeout dla długich połączeń
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
        
        # Headers dla SSE
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Wyłącz chunked transfer encoding dla SSE
        chunked_transfer_encoding off;
        
        # Flush output immediately
        proxy_no_cache 1;
        proxy_cache_bypass 1;
        add_header Cache-Control no-cache;
        add_header X-Accel-Buffering no;
    }
    
    # ========================================
    # 🔄 POZOSTAŁE ENDPOINTS - STANDARDOWE
    # ========================================
    location / {
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
    
    # CORS headers są obsługiwane przez FastAPI - nie dodajemy ich tutaj
}
EOF

# Aktywacja konfiguracji
ln -s /etc/nginx/sites-available/af.aquaforest.eu /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/aiagent.aquaforest.eu /etc/nginx/sites-enabled/

# Test konfiguracji
nginx -t

# Restart Nginx
systemctl restart nginx
systemctl enable nginx
```

## Krok 8: Generowanie certyfikatów SSL

```bash
# Generowanie certyfikatów dla obu domen
certbot --nginx -d af.aquaforest.eu -d www.af.aquaforest.eu
certbot --nginx -d aiagent.aquaforest.eu -d www.aiagent.aquaforest.eu

# Sprawdzenie automatycznego odnawiania
systemctl enable certbot.timer
systemctl start certbot.timer

# Test dry-run odnawiania
certbot renew --dry-run
```

## Krok 9: Systemd Service dla Backendu

```bash
# Tworzenie systemd service dla backendu
cat > /etc/systemd/system/aquaforest-backend.service << 'EOF'
[Unit]
Description=Aquaforest RAG Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/aquaforest-rag/backend
Environment=PATH=/var/www/aquaforest-rag/backend/venv/bin
Environment=ENV_FILE_PATH=/var/aquaforest_env/.env
ExecStart=/var/www/aquaforest-rag/backend/venv/bin/python src/server.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Włączenie i uruchomienie
systemctl enable aquaforest-backend
systemctl start aquaforest-backend

# Sprawdzenie statusu
systemctl status aquaforest-backend
```

## Krok 10: Konfiguracja Firewall

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

## Krok 11: Weryfikacja Deploymentu

```bash
# Sprawdzenie statusów serwisów
systemctl status nginx
systemctl status aquaforest-backend

# Sprawdzenie portów
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :2103

# Test API bezpośrednio
curl http://localhost:2103/health

# Test przez HTTPS
curl https://aiagent.aquaforest.eu/health

# Test frontendu
curl https://af.aquaforest.eu

# Test certyfikatów
curl -I https://af.aquaforest.eu
curl -I https://aiagent.aquaforest.eu
```

## Krok 12: Monitoring i Logi

```bash
# Logi backendu
journalctl -u aquaforest-backend -f

# Logi Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Sprawdzenie bazy danych
ls -la /var/www/aquaforest-rag/backend/aquaforest_analytics.db

# Sprawdzenie external env
ls -la /var/aquaforest_env/
```

## Krok 13: Aktualizacja DNS

Upewnij się, że rekordy DNS wskazują na IP twojego VPS:

```
A    af.aquaforest.eu           YOUR_VPS_IP
A    www.af.aquaforest.eu       YOUR_VPS_IP
A    aiagent.aquaforest.eu      YOUR_VPS_IP
A    www.aiagent.aquaforest.eu  YOUR_VPS_IP
```

## 🎉 Gotowe!

### Funkcjonalności:
✅ **Frontend**: `https://af.aquaforest.eu` - React interface  
✅ **Backend API**: `https://aiagent.aquaforest.eu` - FastAPI z AI workflow  
✅ **External ENV**: `/var/aquaforest_env/.env` - Bezpieczna konfiguracja  
✅ **HTTPS**: Automatyczne certyfikaty SSL  
✅ **Systemd**: Automatyczne uruchamianie backendu  
✅ **Firewall**: Konfiguracja UFW  
✅ **CORS**: Poprawne nagłówki między domenami  

### Struktura aplikacji:
```
/var/www/aquaforest-rag/
├── backend/
│   ├── src/                    # Backend Python/FastAPI
│   ├── venv/                   # Virtual environment
│   ├── requirements.txt        # Python dependencies
│   └── aquaforest_analytics.db # SQLite database
├── frontend/
│   ├── src/                    # Frontend React/TypeScript
│   ├── dist/                   # Built frontend files
│   └── package.json            # Node.js dependencies
└── data/                       # Product data JSON

/var/aquaforest_env/
└── .env                        # External environment variables
```

### Użyte technologie:
- **Backend**: Python, FastAPI, LangGraph, OpenAI, Pinecone
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Database**: SQLite
- **Server**: Nginx, Certbot (Let's Encrypt)
- **Deployment**: systemd, UFW firewall

## 🔧 Rozwiązywanie problemów

### Restart serwisów
```bash
# Restart backendu
systemctl restart aquaforest-backend

# Restart Nginx
systemctl restart nginx

# Restart całego systemu (jeśli konieczne)
reboot
```

### Sprawdzenie logów
```bash
# Logi backendu (ostatnie 100 linii)
journalctl -u aquaforest-backend -n 100

# Logi backendu (ostatnie 10 minut)
journalctl -u aquaforest-backend --since "10 minutes ago"

# Logi Nginx błędów
tail -f /var/log/nginx/error.log

# Logi Nginx dostępu
tail -f /var/log/nginx/access.log
```

### Test SSL
```bash
# Test certyfikatu SSL
openssl s_client -connect af.aquaforest.eu:443 -servername af.aquaforest.eu

# Test certyfikatu API
openssl s_client -connect aiagent.aquaforest.eu:443 -servername aiagent.aquaforest.eu

# Test automatycznego odnawiania
certbot renew --dry-run
```

### Problemy z CORS
```bash
# Sprawdzenie nagłówków CORS
curl -H "Origin: https://af.aquaforest.eu" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://aiagent.aquaforest.eu/chat

# Sprawdzenie czy nie ma duplikowanych nagłówków
curl -I https://aiagent.aquaforest.eu/health

# Jeśli występuje błąd duplikowanych nagłówków CORS:
# 1. Sprawdź czy Nginx nie dodaje nagłówków CORS (powinny być tylko w FastAPI)
# 2. FastAPI ma już skonfigurowane CORS w app_factory.py
# 3. Nginx powinien mieć tylko: "# CORS headers są obsługiwane przez FastAPI"
```

### Problemy z bazą danych
```bash
# Sprawdzenie uprawnień do bazy
ls -la /var/www/aquaforest-rag/backend/aquaforest_analytics.db

# Sprawdzenie miejsca na dysku
df -h

# Sprawdzenie logów SQLite
journalctl -u aquaforest-backend | grep -i sqlite
```

## 📈 Aktualizacja aplikacji

### Aktualizacja z Git
```bash
# Przejście do katalogu aplikacji
cd /var/www/aquaforest-rag

# Pull najnowszej wersji
git pull origin master

# Aktualizacja backendu
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Aktualizacja frontendu
cd ../frontend
npm install
npm run build

# Restart backendu
systemctl restart aquaforest-backend
```

### Backup przed aktualizacją
```bash
# Backup bazy danych
cp /var/www/aquaforest-rag/backend/aquaforest_analytics.db /var/backups/aquaforest_analytics_$(date +%Y%m%d_%H%M%S).db

# Backup konfiguracji Nginx
cp /etc/nginx/sites-available/af.aquaforest.eu /var/backups/
cp /etc/nginx/sites-available/aiagent.aquaforest.eu /var/backups/

# Backup external env
cp /var/aquaforest_env/.env /var/backups/aquaforest_env_$(date +%Y%m%d_%H%M%S).env
```

## 🚨 Monitorowanie produkcyjne

### Sprawdzenie statusu systemu
```bash
# Status wszystkich serwisów
systemctl status nginx aquaforest-backend

# Wykorzystanie zasobów
htop

# Miejsce na dysku
df -h

# Pamięć RAM
free -h

# Obciążenie sieci
netstat -i
```

### Automatyczne monitorowanie
```bash
# Dodaj do crontab (crontab -e)
# Sprawdzanie co 5 minut czy backend działa
*/5 * * * * systemctl is-active --quiet aquaforest-backend || systemctl restart aquaforest-backend

# Backup bazy danych codziennie o 2:00
0 2 * * * cp /var/www/aquaforest-rag/backend/aquaforest_analytics.db /var/backups/aquaforest_analytics_$(date +\%Y\%m\%d).db

# Czyszczenie starych backupów (starsze niż 7 dni)
0 3 * * * find /var/backups -name "aquaforest_analytics_*" -mtime +7 -delete
```

## 🚀 Podsumowanie

Ten deployment guide jest kompletny i gotowy do użycia na produkcyjnym VPS! Wykonując te kroki krok po kroku uzyskasz:

1. **Kompletny system AI** z separacją frontend/backend
2. **Bezpieczne SSL** dla obu domen
3. **External ENV** configuration dla bezpieczeństwa
4. **Automatyczne backupy** i monitoring
5. **Firewall** i security headers
6. **Systemd services** dla stabilności
7. **CORS** poprawnie skonfigurowane

### Domeny po deployment:
- **Frontend**: https://af.aquaforest.eu
- **Backend API**: https://aiagent.aquaforest.eu
- **External ENV**: /var/aquaforest_env/.env

### Gotowe do użycia! 🎯

## 🔧 Streaming Workflow Steps - Troubleshooting

### Problem: Streaming nie działa w czasie rzeczywistym
Jeśli workflow steps nie są wyświetlane na bieżąco, ale wszystkie aktualizacje przychodzą naraz na końcu:

**Przyczyna**: Nginx domyślnie buforuje odpowiedzi, co uniemożliwia Server-Sent Events (SSE) streaming w czasie rzeczywistym.

**Rozwiązanie**: Specjalna konfiguracja dla `/chat/stream` endpoint (już zawarta w powyższej konfiguracji nginx):

```nginx
location /chat/stream {
    proxy_pass http://localhost:2103;
    proxy_http_version 1.1;
    
    # Wyłącz wszystkie buforowanie dla streaming
    proxy_buffering off;
    proxy_cache off;
    proxy_request_buffering off;
    
    # Zwiększ timeout dla długich połączeń
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_send_timeout 300s;
    
    # Headers dla SSE
    proxy_set_header Connection '';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    
    # Wyłącz chunked transfer encoding dla SSE
    chunked_transfer_encoding off;
    
    # Flush output immediately
    proxy_no_cache 1;
    proxy_cache_bypass 1;
    add_header Cache-Control no-cache;
    add_header X-Accel-Buffering no;
}
```

### Test streaming po deployment:

```bash
# Test czy streaming działa
curl -N -H "Accept: text/event-stream" \
     -H "Content-Type: application/json" \
     -d '{"message":"test","chat_history":[],"debug":true}' \
     https://aiagent.aquaforest.eu/chat/stream

# Sprawdzenie logów streaming
journalctl -u aquaforest-backend | grep -i stream
```

### Oczekiwane rezultaty:
- ✅ Workflow steps wyświetlają się na bieżąco
- ✅ Progress bar aktualizuje się płynnie  
- ✅ Brak opóźnień w SSE stream
- ✅ Końcowa odpowiedź płynnie się wyświetla

### Jeśli streaming nadal nie działa:

1. **Sprawdź logi nginx**:
   ```bash
   tail -f /var/log/nginx/error.log
   ```

2. **Sprawdź czy konfiguracja się załadowała**:
   ```bash
   nginx -t
   systemctl reload nginx
   ```

3. **Test bezpośrednio na porcie 2103**:
   ```bash
   curl -N -H "Accept: text/event-stream" \
        -H "Content-Type: application/json" \
        -d '{"message":"test","chat_history":[],"debug":true}' \
        http://localhost:2103/chat/stream
   ```

Jeśli test bezpośrednio na porcie 2103 działa, ale przez nginx nie - problem jest w konfiguracji nginx.
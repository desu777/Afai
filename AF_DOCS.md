# AF_DOCS.md

# Jak Działa Nasz Asystent AI? Przewodnik dla Zespołu

## Konkretny Przykład: Droga Pytania Przez System

**Pytanie klienta:** *"Moje korały się bieleją, co robić?"*

Zobaczmy krok po kroku, co dzieje się w systemie od momentu wysłania pytania do otrzymania odpowiedzi:

### Krok 1: Pytanie dociera przez Internet
**Plik: `server.py` + `core/app_factory.py`**
- Klient wysyła pytanie przez POST na `https://api.aquaforest.eu/chat`
- System bezpieczeństwa sprawdza IP i rate limiting (max 20 pytań/minutę)
- FastAPI server odbiera JSON: `{"message": "Moje korały się bieleją, co robić?"}`
- **Czas: ~5ms**

### Krok 2: Przekazanie do Systemu Chat
**Plik: `endpoints/chat_endpoints.py`**
- Endpoint `/chat` przetwarza żądanie HTTP
- Tworzy nową sesję rozmowy lub używa istniejącej
- Uruchamia workflow i opcjonalnie streaming dla real-time updates
- **Czas: ~10ms**

### Krok 3: Główny Orkiestrator Rusza do Pracy
**Plik: `workflow.py`**
- Tworzy `ConversationState` - "teczkę" z danymi o rozmowie
- Uruchamia sekwencję 6 ekspertów AI w kolejności
- Śledzi timing każdego kroku dla analityki
- **Czas: ~5ms setup**

### Krok 4: Recepcjonista Analizuje Pytanie
**Plik: `intent_detector.py`**
- **Ekspert AI #1** (Gemini Flash 2.5 Thinking) analizuje tekst: "Moje korały się bieleją, co robić?"
- Wykrywa: język = "polski", intencja = "problem_query"
- Nie ma zdjęcia ani pliku PDF
- Wynik: `{"detected_language": "pl", "intent": "product_query"}`
- **Czas: ~3-5 sekund** (zaawansowana analiza thinking model)

### Krok 5: Główny Konsultant Biznesowy
**Pliki: `business_reasoner.py` + `business_reasoning/llm_analyzer.py` + `business_reasoning/decision_applier.py`**
- **Ekspert AI #2** (Gemini Flash 2.5 Thinking - najinteligentniejszy) analizuje problem:
  - Ładuje wiedzę: produkty, konkurenci, scenariusze (`business_reasoning/data_loader.py`)
  - Diagnoza: "Bielenie korali = niedobór składników odżywczych/aminokwasów"
  - Rekomendacja produktów: `["AF Amino Mix", "AF Build", "AF Energy"]`
  - Analiza biznesowa: zapisuje pełną strategię rozwiązania
- **Czas: ~15-20 sekund** (najskomplikowana analiza biznesowa z thinking)

### Krok 6: Bibliotekarz Optymalizuje Wyszukiwanie
**Plik: `query_optimizer.py`**
- **Ekspert AI #3** (Gemini Flash 2.5 Thinking) tworzy smart zapytania wyszukiwania:
  - Z rekomendacji: `"AF Amino Mix coral nutrition"`
  - Dodatkowe: `"coral color enhancement"`, `"amino acids reef"`
  - Warianty: `"coral health supplements"`
- Lista zapytań: `["AF Amino Mix", "coral amino acids", "coral color"]`
- **Czas: ~3-4 sekundy** (inteligentna optymalizacja z thinking)

### Krok 7: Magazynier Przeszukuje Bazę Produktów
**Plik: `pinecone_client.py`**
- Wyszukiwanie semantyczne w bazie 1000+ produktów Aquaforest
- Dla każdego zapytania znajduje top wyniki:
  - "AF Amino Mix" → 98% match z pełną metadatą produktu
  - "coral amino acids" → znajduje także AF Build (95% match)
  - "coral color" → znajduje AF Energy (92% match)
- Zwraca: `[{metadata: product_data, score: 0.98}, ...]`
- **Czas: ~300ms** (bardzo szybka baza wektorowa)

### Krok 8: Konsultant Przygotowuje Odpowiedź
**Pliki: `response_formatter.py` + `response_formatting/prompt_builder.py` + `response_formatting/dosage_calculator.py`**
- **Ekspert AI #4** (Gemini Flash 2.5 Thinking) komponuje końcową odpowiedź:
  - Używa znalezionych produktów + metadanych
  - Kalkuluje dawkowanie (jeśli klient podał objętość)
  - Formatuje w języku polskim, przyjazny ton
  - Dodaje linki do produktów i instrukcje
- Przykład odpowiedzi: *"Bielenie korali to częsty problem spowodowany niedoborem aminokwasów. Polecam: AF Amino Mix (2 krople/100L dziennie), AF Build (2 krople/100L)..."*
- **Czas: ~5-8 sekund** (wysokiej jakości formatowanie z thinking)

### Krok 9: Asystent Pamięci Zapisuje Kontekst
**Plik: `session_manager.py`**
- Zapisuje pełny kontekst rozmowy na 10 minut:
  - Pytanie użytkownika i odpowiedź
  - Znalezione produkty i ich metadane  
  - Analizę biznesową i rekomendacje
  - ID sesji dla kolejnych pytań
- Przygotowuje cache dla pytań followup typu: "a ile tego na 250L?"
- **Czas: ~50ms**

### Krok 10: Odpowiedź Wraca do Klienta
**Pliki: `endpoints/chat_endpoints.py` → `server.py`**
- System pakuje odpowiedź w JSON
- Dodaje metadane (czas, session_id, confidence)
- Zapisuje analitykę do bazy (`analytics/workflow_analytics.py`)
- Klient otrzymuje gotową odpowiedź przez HTTP
- **Czas: ~20ms**

### PODSUMOWANIE CZASÓW:

**PRODUCT QUERY (jak w przykładzie powyżej):**
- **Łączny czas:** 30-50 sekund
- **Najwolniejsze:** Business Reasoner (15-20s) - najgłębsza analiza z Gemini Thinking
- **Najszybsze:** Pinecone search (0.3s) - zoptymalizowana baza wektorowa  
- **Jakość:** Klient otrzymuje odpowiedź na poziomie eksperta z 20-letnim doświadczeniem

**FOLLOW-UP PYTANIA:** do 10 sekund (używa cache z poprzedniej rozmowy)

**INNE TYPY PYTAŃ:** do 10 sekund (greeting, support, business inquiry)

**Strategia jakości:** Wykorzystujemy najlepsze dostępne modele AI (Gemini Flash 2.5 Thinking) dla najwyższej jakości analizy i rekomendacji, nawet kosztem dłuższego czasu odpowiedzi.

---

## Jak To Działa: Analogia z Najlepszym Sklepem Akwarystycznym

**Wyobraź sobie futurystyczny sklep akwarystyczny z 6 super-ekspertami:**

### **Zespół Ekspertów AI:**
1. **Recepcjonista** (`intent_detector.py`) - rozpoznaje język i typ problemu
2. **Główny Konsultant** (`business_reasoner.py`) - 20 lat doświadczenia, zna wszystkie produkty
3. **Bibliotekarz** (`query_optimizer.py`) - wie jak przeszukać ogromną bazę wiedzy
4. **Magazynier** (`pinecone_client.py`) - zna na pamięć wszystkie 1000+ produktów  
5. **Konsultant Sprzedaży** (`response_formatter.py`) - tłumaczy wszystko w prosty sposób
6. **Asystent Pamięci** (`session_manager.py`) - pamięta każdą rozmowę przez 10 minut

### **Sklep Internetowy:**
- **Recepcja Online** (`server.py`) - odbiera zamówienia przez internet 24/7
- **System Obsługi** (`chat_endpoints.py`) - kieruje klientów do ekspertów
- **Orkiestrator** (`workflow.py`) - zarządza kolejnością ekspertów
- **System Bezpieczeństwa** (`security_middleware.py`) - chroni przed spamem

### **Parametry Wydajności:**
- **Product Query:** 30-50 sekund (najwyższa jakość analizy)
- **Follow-up:** do 10 sekund (cache z poprzedniej rozmowy)
- **Inne pytania:** do 10 sekund (greeting, support, business)
- **Dostępność:** 24/7/365  
- **Pojemność:** setki klientów jednocześnie
- **Języki:** 6 języków europejskich
- **Jakość:** Gemini Flash 2.5 Thinking - najlepsze dostępne modele AI

---

## Szczegółowy Opis Komponentów Systemu

### `backend/src/server.py`

**Cel:** Główna brama internetowa - odbiera wszystkie pytania z zewnątrz.

**Analogia:** To jest jak główne wejście do nowoczesnego centrum handlowego z recepcją, ochroną i systemem kierowania klientów do odpowiednich sklepów.

**Co robi?**
* Uruchamia serwer FastAPI na porcie 2103 dostępny przez internet
* Odbiera pytania z aplikacji webowej, widgetu na stronie i aplikacji mobilnej
* Zarządza middleware bezpieczeństwa (rate limiting, IP filtering, CORS)
* Przekazuje zapytania do systemu chat endpoints i zwraca odpowiedzi

**Dlaczego jest ważny?** To jedyny punkt kontaktu klientów z naszym systemem przez internet. Bez tego nasi eksperci AI byliby niedostępni dla świata zewnętrznego.

---

### `backend/src/core/app_factory.py`

**Cel:** Budowniczy całej infrastruktury aplikacji.

**Analogia:** To jest jak główny architekt i kierownik budowy centrum handlowego, który projektuje i buduje całą infrastrukturę: systemy bezpieczeństwa, wentylację, oświetlenie, komunikację między działami.

**Co robi?**
* Tworzy i konfiguruje główną aplikację FastAPI
* Ustawia middleware: CORS, bezpieczeństwo, rate limiting, uwierzytelnianie
* Inicjalizuje bazy danych i systemy analityczne przy starcie
* Konfiguruje wszystkie endpointy API i routing

**Dlaczego jest ważny?** To fundament całego systemu. Bez tego wszystkie komponenty byłyby rozproszone i nie mogłyby ze sobą współpracować jako spójna aplikacja.

---

### `backend/src/endpoints/chat_endpoints.py`

**Cel:** Główne API do rozmów - przetwarza żądania chat i uruchamia workflow.

**Analogia:** To jest jak główne biuro obsługi klienta w centrum handlowym, które przyjmuje zgłoszenia, tworzy "teczkę sprawy" dla każdego klienta i kieruje ją do odpowiedního zespołu ekspertów.

**Co robi?**
* Obsługuje endpointy `/chat` i `/chat/stream` 
* Przetwarza żądania HTTP na obiekty ConversationState
* Uruchamia główny workflow z team ekspertów
* Zarządza streaming real-time dla klientów którzy chcą widzieć postęp
* Zwraca sformatowane odpowiedzi JSON z metadanymi

**Dlaczego jest ważny?** To most między światem HTTP/JSON a wewnętrznym systemem ekspertów AI. Przekłada "język internetu" na "język naszego zespołu".

---

### `backend/src/workflow.py`

**Cel:** Główny orkiestrator - zarządza sekwencją pracy wszystkich ekspertów.

**Analogia:** To jest jak doświadczony manager w centrum obsługi, który zna dokładną procedurę: "najpierw klient idzie do recepcjonisty, potem do konsultanta, następnie do magazyniera..." i pilnuje żeby wszystko przebiegało sprawnie.

**Co robi?**
* Definiuje sekwencję 6 węzłów (ekspertów): intent_detector → business_reasoner → query_optimizer → pinecone_search → response_formatter → session_cache
* Zarządza przepływem danych między ekspertami (ConversationState)
* Mierzy timing każdego kroku do analiz wydajności
* Obsługuje follow-up routing (pytania kontynuacyjne)
* Integruje z systemem analitycznym i streamingiem

**Dlaczego jest ważny?** To "mózg operacyjny" całego systemu. Bez niego eksperci nie wiedzieliby, kiedy i jak ze sobą współpracować. Zapewnia, że każde pytanie przechodzi przez wszystkie niezbędne etapy w odpowiedniej kolejności.

---

### `backend/src/intent_detector.py`

**Cel:** Pierwszy ekspert - recepcjonista rozpoznający język i typ pytania.

**Analogia:** To jest jak wielojęzyczny recepcjonista w międzynarodowym hotelu, który od pierwszego zdania rozpoznaje: "Aha, to Niemiec z problemem technicznym" lub "To Polak, który chce kupić konkretny produkt" lub "To Amerykanin z pytaniem o cenę".

**Co robi?**
* Rozpoznaje język z 6 obsługiwanych (polski, angielski, niemiecki, francuski, hiszpański, włoski)  
* Klasyfikuje intencję: problem_query, purchase_inquiry, greeting, business, competitor, support, other
* Analizuje załączone obrazy akwarium (jeśli są) używając vision AI
* Przetwarza pliki PDF z wynikami testów ICP laboratoryjnych
* Zwraca strukturalny wynik dla kolejnych ekspertów

**Dlaczego jest ważny?** Prawidłowa klasyfikacja na początku oszczędza czas całego zespołu. To jak dobry triage w szpitalu - kieruje każdy przypadek na właściwą ścieżkę obsługi, zapobiegając marnowaniu zasobów.

---

### `backend/src/business_reasoner.py` + `backend/src/business_reasoning/`

**Cel:** Najinteligentniejszy ekspert - główny konsultant biznesowy z pełną wiedzą firmy.

**Analogia:** To jest jak senior konsultant z 20-letnim doświadczeniem, który zna wszystkie nasze produkty, całą konkurencję, typowe problemy klientów i potrafi jednym "spojrzeniem" na opis problemu zaproponować idealne rozwiązanie.

**Co robi?**
* **Ładuje pełną wiedzę biznesową:** produkty, konkurenci, scenariusze, use cases (`data_loader.py`)
* **Przeprowadza analizę AI:** używa najinteligentniejszego modelu do zrozumienia problemu (`llm_analyzer.py`) 
* **Podejmuje decyzje biznesowe:** identyfikuje najlepsze produkty, rozpoznaje konkurentów, dopasowuje scenariusze (`decision_applier.py`)
* **Specjalizacje:** problemy akwarystyczne, zamieiniki konkurentów, systemy balling, korekty parametrów wody
* **Wyniki:** lista konkretnych produktów Aquaforest + strategia biznesowa + uzasadnienie

**Dlaczego jest ważny?** To "mózg biznesowy" całego systemu. Bez niego asystent potrafiłby tylko mechanicznie wyszukiwać produkty, ale nie rozumiałby problemów klientów ani nie doradzał jak prawdziwy ekspert z wieloletnim doświadczeniem.

---

### `backend/src/query_optimizer.py`

**Cel:** Ekspert od wyszukiwania - bibliotekarz tworzący idealne zapytania.

**Analogia:** To jest jak genialny bibliotekarz w gigantycznej bibliotece, który słysząc problem od razu wie, pod jakimi 5-10 różnymi hasłami szukać, żeby znaleźć wszystkie przydatne informacje, w tym te które klient nie pomyślał wspomnieć.

**Co robi?**
* Bierze rekomendacje z business reasoner i tworzy smart zapytania wyszukiwania
* Generuje warianty: nazwy produktów, synonimy, terminy techniczne, nazwy angielskie/polskie
* Uwzględnia kontekst: typ akwarium (słodkowodne/morskie), poziom zaawansowania klienta
* Optymalizuje dla wyszukiwania semantycznego (Pinecone vector search)
* Zwraca listę zoptymalizowanych zapytań uporządkowanych według priorytetu

**Dlaczego jest ważny?** Nawet z najlepszą bazą produktów, bez inteligentnego wyszukiwania moglibyśmy przegapić idealne rozwiązania. To różnica między szukaniem "ręcznym" a używaniem profesjonalnego wyszukiwarka który rozumie kontekst.

---

### `backend/src/pinecone_client.py`

**Cel:** Błyskawiczny magazynier z fotograficzną pamięcią - przeszukuje bazę 1000+ produktów.

**Analogia:** To jest jak magazynier z super-mocami, który w ułamku sekundy przeszukuje pamięcią gigantyczny magazyn z wszystkimi produktami Aquaforest i znajduje dokładnie te, które rozwiążą problem klienta - nawet jeśli klient użył innych słów.

**Co robi?**
* Przeszukuje bazę wektorową Pinecone z embeddings wszystkich produktów Aquaforest
* Dla każdego zapytania znajduje najlepsze dopasowania semantyczne (nie tylko keyword matching)
* Filtruje wyniki według kontekstu: domain (słodkowodne/morskie), język, kategoria  
* Zwraca top wyniki z metadata: pełne opisy, dawkowanie, URLs, ceny
* Wykorzystuje AI embeddings dla inteligentnego rozumienia znaczenia zapytań

**Dlaczego jest ważny?** To "długoterminowa pamięć" całego systemu. Przechowuje wiedzę o wszystkich produktach w sposób, który rozumie znaczenie i kontekst, nie tylko słowa kluczowe. Dzięki temu znajduje idealne produkty nawet gdy klient opisuje problem innymi słowami.

---

### `backend/src/response_formatter.py` + `backend/src/response_formatting/`

**Cel:** Mistrz komunikacji - tłumaczy wiedzę eksperta na język zrozumiały dla klienta.

**Analogia:** To jest jak najlepszy konsultant sprzedaży, który potrafi wziąć skomplikowane analizy od zespołu ekspertów i przetłumaczyć to na prosty, przyjazny język z konkretnymi instrukcjami, dawkowaniem i praktycznymi poradami.

**Co robi?**
* **Główne komponenty:**
  - `prompt_builder.py` - tworzy spersonalizowane instrukcje dla AI na podstawie wszystkich zebranych danych
  - `dosage_calculator.py` - kalkuluje precyzyjne dawkowanie na konkretne objętości akwarium  
  - `cache_manager.py` - zarządza pamięcią rozmów dla szybkich odpowiedzi followup
* **Funkcje:** komponuje końcową odpowiedź, dostosowuje język i ton, dodaje instrukcje i linki, kalkuluje dawki
* **Specjalizacje:** odpowiedzi ICP, analizy obrazów, różne poziomy zaawansowania klienta

**Dlaczego jest ważny?** Możemy mieć najlepszych ekspertów i produkty na świecie, ale jeśli nie umiemy tego wytłumaczyć klientowi w zrozumiały i praktyczny sposób, cała wiedza pójdzie na marne. To "głos" marki Aquaforest.

---

### `backend/src/session_manager.py`

**Cel:** Asystent pamięci - zarządza kontekstem rozmów dla naturalnej konwersacji.

**Analogia:** To jest jak osobisty asystent każdego eksperta, który przez 10 minut po rozmowie pamięta każdy szczegół: jakie produkty polecił, jakiej objętości było akwarium, jakie problemy zidentyfikował - żeby na pytanie "a ile tego na moje akwarium?" nie musieć wszystkiego powtarzać.

**Co robi?**
* Tworzy unikalne ID sesji dla każdej rozmowy i przechowuje pełny kontekst
* Zapisuje: pytania użytkownika, odpowiedzi, znalezione produkty, analizy biznesowe, metadane
* Automatyczne czyszczenie po 10 minutach (TTL - Time To Live)
* Przygotowuje "extended cache" dla inteligentnych odpowiedzi followup  
* Zarządza pamięcią systemu (cleanup starych sesji)

**Dlaczego jest ważny?** Umożliwia naturalną konwersację jak z prawdziwym ekspertem. Klient może zapytać "a co z dawkowaniem?", "a ile to kosztuje?", "a mam 250L, ile potrzebuję?" bez powtarzania całego kontekstu swojej sytuacji.

---

### `backend/src/follow_up_evaluator.py`

**Cel:** Inteligentny decydent - ocenia czy może odpowiedzieć z pamięci czy musi szukać nowo.

**Analogia:** To jest jak super-doświadczony konsultant, który słysząc nowe pytanie od klienta błyskawicznie ocenia: "Czy mogę odpowiedzieć na podstawie naszej wcześniejszej rozmowy, czy muszę przeprowadzić nową analizę?" Oszczędza czas wszystkim.

**Co robi?**
* Analizuje nowe pytanie w kontekście poprzedniej rozmowy
* Ocenia czy cached dane są wystarczające do odpowiedzi (confidence scoring)
* Decyzja: używa cache (szybko) vs. pełny workflow (dokładnie)
* Przygotowuje inteligentne prompty dla innych ekspertów jeśli potrzeba nowych danych
* Wykorzystuje zaawansowany AI do rozumienia similariności pytań

**Dlaczego jest ważny?** Drastycznie przyspiesza odpowiedzi followup (z 4s do <1s). Zamiast za każdym razem angażować całý zespół ekspertów, inteligentnie rozpoznaje kiedy wystarczy zapamiętana wiedza z rozmowy.

---

### `backend/src/config.py`

**Cel:** Centrum sterowania - wszystkie ustawienia i konfiguracja systemu.

**Analogia:** To jest jak główny panel kontrolny centrum handlowego, gdzie ustawia się wszystkie parametry: które firmy AI obsługują poszczególnych ekspertów, jak szybko mają pracować, jakie mają budżety, limity bezpieczeństwa, itp.

**Co robi?**
* **Konfiguracja per-ekspert:** każdy z 6 ekspertów ma swojego dostawcę AI, model i parametry
* **Multi-provider setup:** Google Vertex AI (primary) + OpenRouter (fallback) dla każdego węzła
* **Parametry wydajności:** temperatury AI, thinking budgets, timeouty, rate limity
* **Bezpieczeństwo:** klucze API, CORS origins, auth tokeny, IP filtering
* **Analityka:** włączenie/wyłączenie logów, debugging, metrics

**Dlaczego jest ważny?** To "centrum dowodzenia" całego systemu. Jedna zmiana tutaj może wpłynąć na wydajność, koszty i jakość całego zespołu ekspertów. Pozwala na fine-tuning każdego komponenta osobno.

---

### `backend/src/llm_client_factory.py`

**Cel:** HR dla ekspertów AI - rekrutuje i konfiguruje najlepsze "mózgi" dla każdego eksperta.

**Analogia:** To jest jak wyspecjalizowany HR-owiec, który dla każdego stanowiska (recepcjonista, konsultant, bibliotekarz) wybiera najlepszego kandydata AI, negocjuje warunki, konfiguruje go i dba o backup na wypadek choroby/awarii.

**Co robi?**
* **Per-node specialization:** każdy ekspert ma dedykowany model AI dopasowany do zadania
* **Multi-provider management:** zarządza dostawcami (Google Vertex AI, OpenRouter) z automatic fallback
* **Quality assurance:** configura parametry jakości, thinking budgets, temperatury
* **Resilience:** automatic failover między dostawcami, monitoring dostępności
* **Cost optimization:** balansuje quality vs cost dla każdego typu zadania

**Dlaczego jest ważny?** Zapewnia że każdy ekspert ma "mózg" optymalnie dobrany do swojej roli: recepcjonista - szybki i tani, główny konsultant - najinteligentniejszy i most capable, formatter - kreatywny i komunikatywny.

---

### `backend/src/security_middleware.py`

**Cel:** System ochrony - chroni przed atakami i nadużyciami.

**Analogia:** To jest jak kompleksowy system bezpieczeństwa centrum handlowego: kamery, alarmy, ochroniarze, systemy kontroli dostępu, automatyczne blokady dla podejrzanych osób, monitoring ruchu i przewidywanie zagrożeń.

**Co robi?**
* **Multi-tier rate limiting:** różne limity dla różnych endpoints (chat: 20/min, analytics: 60/min)
* **Automatic IP blacklisting:** po 2 przekroczeniach → blokada na 24h
* **Authentication:** X-Aquaforest-Auth header validation
* **Security headers:** XSS protection, CSRF, content sniffing prevention  
* **IP filtering:** whitelist/blacklist functionality
* **Attack monitoring:** logging wszystkich prób ataków i nietypowej aktywności

**Dlaczego jest ważny?** Chroni nasze zasoby AI (które kosztują) przed abuse, zapewnia fair usage dla wszystkich klientów i chroni przed DDoS, botami i innymi zagrożeniami cyber-security.

---

### `backend/src/endpoints/analytics_endpoints.py`

**Cel:** System business intelligence - zbiera i analizuje dane o użytkowaniu.

**Analogia:** To jest jak zaawansowany dział analityki biznesowej, który monitoruje wszystkie aspekty działania centrum: ruch klientów, popularność produktów, efektywność ekspertów, satysfakcję klientów, trendy i predykcje.

**Co robi?**
* **Comprehensive tracking:** każda rozmowa → pełny record z timingami, decyzjami, rezultatami
* **Performance monitoring:** speed każdego eksperta, bottlenecks, quality metrics
* **Business insights:** najpopularniejsze produkty, trending problemy, seasonal patterns  
* **Expert performance:** który AI model działa best, optymalizacje parametrów
* **ROI tracking:** cost per conversation, conversion rates, customer satisfaction

**Dlaczego jest ważny?** Dostarcza data-driven insights dla optymalizacji systemu i biznesu. Bez tego działalibyśmy "na ślepo" nie wiedząc co działa, co trzeba poprawić i jak inwestować w rozwój.

---

### `backend/src/endpoints/feedback_endpoints.py`

**Cel:** System jakości - zbiera opinie klientów i mierzy satysfakcję.

**Analogia:** To jest jak zaawansowany system ankiet zadowolenia w centrum handlowym, który po każdej wizycie pyta o ocenę, zbiera sugestie, identyfikuje problemy i mierzy trend satysfakcji w czasie.

**Co robi?**
* **Rating system:** klienci oceniają odpowiedzi 1-5 gwiazdek + komentarze tekstowe
* **Response linking:** każda opinia jest powiązana z konkretną odpowiedzią i sessionem
* **Sentiment analysis:** automatically kategoryzuje feedback (positive, negative, suggestions)
* **Quality alerts:** notyfikuje gdy satisfaction score spadnie poniżej threshold
* **Improvement tracking:** monitoruje czy zmiany w systemie poprawiają ratings

**Dlaczego jest ważny?** Feedback od klientów to najważniejszy źródło informacji o jakości naszego systemu. Bez tego nie wiemy czy rzeczywiście pomagamy ludziom i jak możemy się poprawić.

---

### `backend/src/endpoints/session_endpoints.py`

**Cel:** API do zarządzania sesjami i monitoringu aktywnych rozmów.

**Analogia:** To jest jak system monitoringu recepcji, który pokazuje ilu klientów jest aktualnie obsługiwanych, jak długo trwają rozmowy, które stoły są zajęte i kiedy można spodziewać się zwolnienia miejsca.

**Co robi?**
* **Session monitoring:** real-time view aktywnych sesji, timings, memory usage
* **Management API:** manual session cleanup, statistics, debugging tools
* **Capacity planning:** monitoring czy system radzi sobie z load
* **Debugging support:** inspection sesji dla troubleshootingu problems
* **Performance metrics:** average session duration, memory per session, cleanup efficiency

**Dlaczego jest ważny?** Pomaga administratorom monitorować zdrowie systemu, optymalizować memory usage i quickly diagnose issues related do session management.

---

### `backend/src/endpoints/export_endpoints.py`

**Cel:** Generator raportów - eksportuje dane do analizy biznesowej.

**Analogia:** To jest jak dział raportów w firmie, który potrafi wygenerować dowolne zestawienie sprzedaży, ruchu klientów, popularności produktów w formacie Excel/CSV dla zespołu biznesowego, marketingu i zarządu.

**Co robi?**
* **Data export:** CSV exports rozmów, analytics, feedback z flexible filtering
* **Business reports:** ready-made raporty dla marketing, sales, product teams
* **Custom queries:** API do tworzenia custom raportów według potrzeb
* **Automated reporting:** scheduled exports dla regular business reviews
* **Data privacy:** anonymizacja wrażliwych danych w exportach

**Dlaczego jest ważny?** Umożliwia głęboką analizę biznesową w external tools (Excel, PowerBI, Tableau), co jest essential dla strategic decision making i business optimization.

---

### `backend/src/endpoints/security_endpoints.py`

**Cel:** Centrum dowodzenia bezpieczeństwem - monitoring i active defense.

**Analogia:** To jest jak centrum dowodzenia ochrony budynku z monitorami pokazującymi wszystkie kamery, alerty bezpieczeństwa, logi prób włamania i panelem do active response (blokowanie dostępu, wzywanie pomocy).

**Co robi?**
* **Attack monitoring:** real-time view wszystkich prób ataków, blocked IPs, violation patterns
* **Active defense management:** manual IP blocking/unblocking, whitelist management
* **Security analytics:** trendy w atakach, most common attack vectors, geographic analysis
* **Incident response:** tools do quick response na security incidents
* **Threat intelligence:** analysis patterns do predictive security

**Dlaczego jest ważny?** Daje security team pełną visibility i kontrolę nad bezpieczeństwem systemu, umożliwia proactive defense i quick response na nowe zagrożenia.

---

### `backend/src/database/connection.py`

**Cel:** Zarządca bazy danych - bezpieczne połączenia i transakcje.

**Analogia:** To jest jak kierownik archiwum firmy, który zarządza dostępem do wszystkich dokumentów, dba o bezpieczeństwo, backup, szybkość dostępu i organizację wszystkich zapisanych danych.

**Co robi?**
* **Connection management:** pool połączeń do SQLite database, connection reuse
* **Transaction safety:** automatic commit/rollback, ACID compliance
* **Performance optimization:** query optimization, indexing, cleanup starych danych  
* **Data integrity:** validation, constraints, foreign keys
* **Backup/recovery:** automated backup procedures, disaster recovery

**Dlaczego jest ważny?** Wszystkie dane analytics, feedback, sessions muszą być safely stored i quickly accessible. Bez tego tracimy valuable business intelligence i user experience suffers.

---

### `backend/src/database/analytics_operations.py`

**Cel:** Specjalista od operacji analitycznych - zapisuje i agreguje metryki.

**Analogia:** To jest jak główny księgowy firmy, który precyzyjnie rejestruje każdą transakcję, organizuje dane w sposób umożliwiający różne analizy i przygotowuje agregowane raporty dla zarządu.

**Co robi?**
* **Detailed logging:** każda conversation → comprehensive record z wszystkimi metrykami
* **Data aggregation:** daily/monthly summaries, trends, performance metrics
* **Gemini API tracking:** monitoring usage i costs per-node z daily limits
* **Query optimization:** efficient data storage i retrieval dla large datasets
* **Data cleanup:** automated removal starych danych według retention policies

**Dlaczego jest ważny?** To foundation całego systemu business intelligence. Bez proper data storage i organization nie możemy analyzować performance, optimize costs czy understand user behavior.

---

### `backend/src/calculation_helper.py`

**Cel:** Precyzyjny kalkulator akwarystyczny - ekspert od obliczeń chemicznych.

**Analogia:** To jest jak wykwalifikowany chemik laboratoryjny, który potrafi błyskawicznie i precyzyjnie przeliczyć dawkowanie na każdą objętość akwarium, przewidzieć wpływ na parametry wody i sprawdzić czy dawka jest bezpieczna dla żywych organizmów.

**Co robi?**
* **Dosage calculations:** precise dawkowanie produktów na różne volumes (50L, 100L, 250L, etc.)
* **Parameter predictions:** kalkulacja wpływu dawek na Ca, Mg, KH, PO4, NO3
* **Safety validation:** sprawdzanie czy calculated doses są within safe limits
* **Schedule optimization:** podział dawek na multiple daily doses dla lepszej absorpcji
* **Volume extraction:** automatic detection objętości akwarium z user queries

**Dlaczego jest ważny?** Precyzyjne dawkowanie to podstawa sukcesu w akwarystyce. Błędne calculations mogą harm marine life, więc ten moduł zapewnia laboratory-grade accuracy w all calculations.

---

### `backend/src/analytics/workflow_analytics.py`

**Cel:** Performance profiler - mierzy wydajność każdego eksperta w real-time.

**Analogia:** To jest jak konsultant efektywności z stopwatchem, który śledzi jak długo każdy ekspert potrzebuje na swoją część pracy, identyfikuje bottlenecks i dostarcza danych do optimization całego procesu.

**Co robi?**
* **Real-time timing:** precise measurement każdego workflow step
* **Performance metrics:** throughput, latency, success rates per expert
* **Bottleneck detection:** identification najwolniejszych komponentów  
* **Quality correlation:** linking performance metrics z user satisfaction
* **Streaming integration:** real-time updates dla client-side progress indicators

**Dlaczego jest ważny?** Performance optimization requires precise measurement. Bez detailed timings nie wiemy gdzie system można speed up, który AI model potrzebuje upgrade i jak allocated budgets między experts.

---

### `backend/src/response_formatting/dosage_calculator.py`

**Cel:** Specialized chemist w zespole response formatingu - ekspert od instructions.

**Analogia:** To jest jak chemik-specialist, który pracuje closely z sales consultantem i pomaga mu prepare precise dosage instructions dostosowane do konkretnego akwarium klienta.

**Co robi?**
* **Query recognition:** identifies gdy user pyta o dosage ("ile na 200L?")
* **Metadata extraction:** wyciąga dosage info z product descriptions i metadanych
* **Volume-based calculation:** precise scaling dla user's specific akwarium size
* **Instruction formatting:** creates clear, actionable dosing instructions
* **Safety considerations:** warns o potential overdosing czy interactions

**Dlaczego jest ważny?** Users bardzo często ask "how much do I need for my tank". Ten moduł zapewnia że każda odpowiedź contains accurate, safe i practical dosing guidance.

---

### `backend/src/response_formatting/cache_manager.py`

**Cel:** Memory specialist - optymalizuje followup responses używając cached context.

**Analogia:** To jest jak super-efficient personal assistant konsultanta, który maintains detailed notes z każdej rozmowy i potrafi instantly prepare odpowiedzi na followup questions without re-doing całą analizę.

**Co robi?**
* **Extended cache creation:** stores comprehensive conversation context z rich metadata
* **Followup response generation:** creates answers using cached data instead of full workflow
* **Context preservation:** maintains conversation flow i continuity
* **Performance optimization:** reduces followup response time z 4s do <1s
* **Memory management:** balances cache size z system memory constraints

**Dlaczego jest ważny?** Dramatically improves user experience dla conversational interactions. Users can ask "what about dosing?" czy "how much does it cost?" without repeating context.

---

### `backend/src/response_formatting/prompt_builder.py`

**Cel:** Instruction architect - tworzy perfect prompts dla response formatter AI.

**Analogia:** To jest jak master trainer, który prepares detailed, personalized instruction manuals dla sales consultant, adjusted do każdej specific situation (customer level, problem type, language, context).

**Co robi?**
* **Context integration:** combines wszystkie gathered info (business analysis, products, user context) into coherent instructions
* **Personalization:** adjusts tone, complexity i approach według user level i preferences  
* **Special scenarios:** handles unique cases (ICP analysis, image analysis, competitor questions)
* **Template management:** uses external prompt templates z fallbacks
* **Quality assurance:** ensures consistency z Aquaforest brand voice i standards

**Dlaczego jest ważny?** Even najlepszy AI needs good instructions. Ten moduł ensures że response formatter consistently delivers high-quality, brand-appropriate responses dostosowane do każdej unique situation.

---

### `backend/src/business_reasoning/data_loader.py`

**Cel:** Librarian master wiedzy biznesowej - ładuje complete knowledge base dla business expert.

**Analogia:** To jest jak główny bibliotekarz uniwersytecki, który każdego ranka loads complete business knowledge z wszystkich działów firmy into "mózg" main consultant: produkty, konkurencja, scenarios, best practices, customer cases.

**Co robi?**
* **Product knowledge loading:** complete Aquaforest catalog z descriptions, applications, compatibilities
* **Competitor mapping:** comprehensive database konkurentów z our equivalent products
* **Scenario databases:** typical aquarium setups, problems i their solutions
* **Use case libraries:** real customer scenarios i successful resolution patterns
* **Business rules:** product groupings, bundling logic, cross-selling opportunities

**Dlaczego jest ważny?** Business reasoner potrzebuje access do complete company knowledge żeby function jak real expert z years of experience. Ten moduł is jego "business education".

---

### `backend/src/business_reasoning/llm_analyzer.py`

**Cel:** Analytical brain głównego business consultant - przeprowadza deep analysis.

**Analogia:** To jest jak "neural processor" najbardziej doświadczonego sales consultant, który takes customer problem i runs it through years of accumulated wisdom, product knowledge i business logic do produce perfect recommendation.

**Co robi?**
* **Deep problem analysis:** understanding root causes za customer issues
* **Product matching:** intelligent selection najlepszych solutions z catalog
* **Business logic application:** considers bundling, compatibility, customer level
* **Confidence scoring:** ocenia pewność own recommendations
* **Structured output:** produces organized business intelligence dla innych components

**Dlaczego jest ważny?** To jest thinking engine business reasoner. Bez tego consultant miałby knowledge ale couldn't effectively apply it do solving customer problems i making intelligent recommendations.

---

### `backend/src/business_reasoning/decision_applier.py`

**Cel:** Implementation specialist - przekłada business analysis na actionable decisions.

**Analogia:** To jest jak implementation manager, który takes strategic recommendations od senior consultant i translates them into specific, actionable tasks dla reszty team (what products to search, what context to provide, what strategy to use).

**Co robi?**
* **Decision translation:** converts business analysis into specific actions dla other workflow components  
* **Product list preparation:** creates prioritized lists produktów dla search team
* **Context formatting:** prepares business context dla response formatter
* **Strategy application:** applies appropriate response strategies (direct recommendations, educational, competitive)
* **Workflow coordination:** ensures business decisions are properly implemented przez całe workflow

**Dlaczego jest ważny?** Bridge między strategic thinking i operational execution. Zapewnia że intelligent business decisions are effectively translated into concrete actions throughout system.

---

### `backend/src/utils/logger.py`

**Cel:** Advanced monitoring system - comprehensive logging dla debugging i optimization.

**Analogia:** To jest jak sophisticated monitoring system w modern data center z multiple camera types, sensors, performance meters i alert systems - wszystko zapisywane dla analysis, troubleshooting i optimization.

**Co robi?**
* **Hierarchical logging:** main events, sub-processes, detailed steps z proper indentation
* **Category-based organization:** different log types (workflow, streaming, security, performance, errors)
* **Developer-friendly formatting:** elegant, readable output z timestamps i context
* **Performance tracking:** timing integration dla performance analysis
* **Debug support:** detailed tracing dla troubleshooting complex issues

**Dlaczego jest ważny?** High-quality logging is essential dla maintaining complex AI system. Gdy coś goes wrong, to jedyny way to understand what happened i fix issues efficiently.

---

### `backend/src/icp_scraper.py`

**Cel:** Laboratory specialist - expert w reading i analyzing ICP water test results.

**Analogia:** To jest jak advanced lab technician który specializes w interpreting complex water chemistry reports z professional laboratories i translating scientific data into practical aquarium management advice.

**Co robi?**
* **PDF processing:** reads ICP test result files z various lab formats
* **Parameter extraction:** identifies wszystkie measured water parameters i values  
* **Problem identification:** spots dangerous levels, imbalances i deficiencies
* **Solution mapping:** recommends specific Aquaforest products dla parameter corrections
* **Professional communication:** explains results w language appropriate dla user level

**Dlaczego jest ważny?** ICP tests represent most advanced water analysis available dla aquarists. Ten moduł enables our assistant to provide professional-grade advice based on laboratory data.

---

### `backend/src/resilient_client.py`

**Cel:** Reliability engineer - zapewnia continuous operation poprzez automatic failover.

**Analogia:** To jest jak backup system dla ekspertów - jeśli primary AI expert ma problems (server overload, network issues), automatically switches do backup expert tak żeby customer never notices interruption w service.

**Co robi?**
* **Automatic failover:** seamless switching między AI providers (Google → OpenRouter)
* **Health monitoring:** continuous checking availability i performance każdego provider
* **Transparent operation:** clients don't experience service interruption during failover
* **Error recovery:** intelligent retry logic z exponential backoff
* **Provider optimization:** learns which providers work best dla which tasks

**Dlaczego jest ważny?** Zapewnia 99.9% system availability. Customers always get answers nawet when individual AI providers experience technical difficulties.

---

### `backend/src/gemini_client_factory.py`

**Cel:** Specialized recruiter dla Google's advanced AI experts - configures premium AI models.

**Analogia:** To jest jak executive recruiter specializing w hiring top-tier talent od Google, który knows exactly how to onboard, configure i optimize their most advanced AI specialists dla our specific business needs.

**Co robi?**
* **Vertex AI integration:** connects z Google's most advanced AI models przez cloud infrastructure
* **Advanced configuration:** sets up thinking budgets, reasoning parameters, quality settings
* **Authentication management:** handles Google Cloud credentials i project setup
* **Performance optimization:** tunes models dla our specific use cases i response patterns
* **Enterprise-grade reliability:** leverages Google's enterprise AI infrastructure

**Dlaczego jest ważny?** Google provides some of the most advanced AI models available. Ten moduł enables us to leverage their cutting-edge technology optimally configured dla aquarium expertise.

---

### `backend/src/models.py`

**Cel:** System architect's blueprint - defines wszystkie data structures i communication protocols.

**Analogia:** To jest jak detailed architectural drawings dla building, które specify exactly how każdy room should look, what information każdy department needs to share, i how communication flows between all części systemu.

**Co robi?**
* **Data structure definitions:** ConversationState, Intent types, Response formats
* **API contracts:** specifies exactly what data każdy component expects i provides
* **Type safety:** ensures wszystkie components "speak same language"
* **Documentation:** defines wszystkie possible states i transitions w conversation flow
* **Validation:** enforces data integrity throughout system

**Dlaczego jest ważny?** Foundation for all system communication. Bez clear data structures, components couldn't reliably exchange information i system would be fragile i error-prone.

---

### `backend/src/prompts/`

**Cel:** Instruction library - comprehensive training materials dla wszystkich AI experts.

**Analogia:** To jest jak corporate university training center z detailed curriculum dla każdej role w company: customer service, sales, technical support - wszystko w multiple languages i dla different experience levels.

**Co robi?**
* **Role-specific instructions:** detailed prompts dla każdego type of expert (intent detection, business reasoning, response formatting)
* **Scenario coverage:** templates dla wszystkie common situations (greetings, technical problems, competitor questions, ICP analysis)
* **Multi-language support:** consistent brand voice across wszystkie supported languages  
* **Access level customization:** different instruction sets dla basic vs professional users
* **Brand consistency:** ensures wszystkie AI experts represent Aquaforest professionally

**Dlaczego jest ważny?** AI experts need excellent training to represent our brand consistently. Ten directory ensures każdy AI interaction maintains high quality i brand standards regardless of situation.

---

### `backend/src/mapping/`

**Cel:** Business intelligence database - strategic knowledge dla competitive advantage.

**Analogia:** To jest jak strategic planning department z comprehensive market intelligence: competitor analysis, product positioning, customer segmentation, use case studies, market scenarios - wszystko organized dla quick decision making.

**Co robi?**
* **Competitor intelligence:** maps competitive products do our alternatives z positioning strategies
* **Product scenarios:** defines ideal product combinations dla different aquarium setups
* **Use case libraries:** documented customer success stories z product recommendations
* **Business rules:** automated logic dla product selection, bundling, cross-selling
* **Market positioning:** strategic guidance dla presenting our products effectively

**Dlaczego jest ważny?** This is company's strategic brain encoded jako structured data. Enables business reasoner to make decisions z same sophistication jako senior sales manager z years of market experience.

---

### `backend/src/env_loader.py`

**Cel:** Security vault manager - handles wszystkie sensitive configuration data.

**Analogia:** To jest jak corporate security officer który manages company's sensitive information (passwords, keys, certificates) w secure vault outside main office i provides them securely do authorized systems only when needed.

**Co robi?**
* **Secure configuration loading:** loads sensitive data z external, secure locations
* **API key management:** safely distributes API keys do various system components
* **Environment separation:** different configs dla development, staging, production
* **Fallback mechanisms:** local development configs when external vault unavailable
* **Security enforcement:** prevents accidental exposure of sensitive data

**Dlaczego jest ważny?** Security of API keys i credentials jest fundamental. Bez proper secret management, sensitive data could leak do code repositories czy be accessible by unauthorized parties.
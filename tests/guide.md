📚 DOKŁADNE OPOWIADANIE O KAŻDYM PLIKU - AQUAFOREST RAG SYSTEM
🗂️ KATALOG src/ - GŁÓWNY KOD BACKENDU
1. __init__.py - Inicjalizator Pakietu
Opowiadanie: To jest bardzo prosty plik, który mówi Pythonowi: "Hej, ten katalog src/ to jest pakiet Python!". Ma tylko dwa wiersze - komentarz o nazwie systemu i numer wersji "1.0.0". To jak wizytówka całego projektu - pierwszy plik który Python czyta, żeby zrozumieć że to jest pakiet, a nie zwykły folder.
2. config.py - Centrum Sterowania Całej Aplikacji
Opowiadanie: To jest jak "panel sterowania" całej aplikacji! Ten plik jest odpowiedzialny za wszystkie ustawienia systemowe. Na samym początku ładuje zmienne środowiskowe z pliku .env przy pomocy load_dotenv().
Co się tu dzieje krok po kroku:
Tryb Debug: Definiuje TEST_ENV - gdy jest true, aplikacja pokazuje szczegółowe logi o wszystkim co robi
Funkcja debug_print(): Specjalna funkcja, która drukuje informacje debug tylko gdy tryb TEST_ENV jest włączony
Konfiguracja Pinecone: Ustala klucze API do bazy wektorowej Pinecone
Konfiguracja OpenAI: Ustawienia dla ChatGPT - model (domyślnie gpt-4o-mini), temperatura (0.3 dla konsystentnych odpowiedzi)
Parametry Wyszukiwania: DEFAULT_K_VALUE=12 (ile wyników wyszukiwać), CONFIDENCE_THRESHOLD=0.5 (obniżony z 0.6!)
Lista Konkurentów: Hardkodowana lista firm konkurencyjnych jak Red Sea, Seachem
Walidacja: Sprawdza czy wszystkie wymagane klucze API są ustawione
Najważniejsze: Gdy aplikacja startuje w trybie debug, wypisuje piękny banner z wszystkimi ustawieniami!
3. models.py - Definicje Wszystkich Struktur Danych
Opowiadanie: To jest "słownik" całej aplikacji - definiuje wszystkie typy danych których system używa. To jak instrukcje budowania różnych "pudełek" na dane.
Kluczowe struktury:
Intent (Enum): 9 różnych intencji użytkownika - od powitania po zapytania o produkty
Domain (Enum): 3 typy akwarium - słodkowodne, morskie, uniwersalne
ConversationState (TypedDict): NAJWAŻNIEJSZA struktura! To jest jak "plecak" który nosi wszystkie informacje podczas przetwarzania zapytania:
Zapytanie użytkownika
Wykryty język i intencję
Wyniki wyszukiwania
Historię czatu
Metryki czasowe każdego kroku
I dziesiątki innych pól!
Przykład życia ConversationState: Jak użytkownik pyta "Co to jest Ca Plus?", ten obiekt zaczyna pusty, potem każdy moduł (intent_detector, business_reasoner, itd.) dodaje do niego swoje informacje, aż na końcu ma kompletną odpowiedź!
4. main.py - Punkt Wejścia i Interaktywny Tryb
Opowiadanie: To jest "główne wejście" do aplikacji - jak drzwi frontowe do domu! Ten plik odpowiada za dwie rzeczy:
Klasa AquaforestAssistant:
Ma metodę process_query_sync() która bierze zapytanie użytkownika i przepuszcza przez cały workflow
Obsługuje tryb debug (gdy debug=True, pokazuje dokładnie każdy krok workflow)
Mierzy czas wykonania całego procesu
Obsługuje błędy elegancko
Funkcja main() - Interaktywny Chat:
To jest jak rozmowa na żywo z botem! Uruchamia konsolowy interfejs gdzie możesz:
Pisać zapytania i dostać odpowiedzi
Wpisać 'debug' żeby włączyć/wyłączyć tryb szczegółowy
Wpisać 'new' żeby zacząć nową konwersację
Wpisać 'quit' żeby wyjść
Przykład pracy: Gdy wpiszesz "Co to jest Ca Plus?" w trybie debug, zobaczyście każdy węzeł workflow jak wykrywa intencję, optymalizuje zapytanie, szuka w Pinecone, ocenia confidence, formatuje odpowiedź!
5. intent_detector.py - Detektyw Intencji Użytkownika
Opowiadanie: To jest jak "detektyw" który analizuje co naprawdę chce użytkownik! Ten moduł używa ChatGPT żeby zrozumieć intencję w zapytaniu.
Klasa IntentDetector:
_create_intent_prompt(): Tworzy zapytanie do ChatGPT z kontekstem konwersacji
detect(): Wysyła zapytanie do OpenAI i analizuje odpowiedź
Kluczowe cechy:
Analizuje historię konwersacji żeby wykryć follow-up questions
Używa zewnętrznego template'u promptu z pliku prompts/intent_detection.txt
Gdy confidence jest poniżej 0.5, domyślnie ustawia "product_query"
W trybie debug pokazuje każdy krok analizy
Przykład: Gdy użytkownik pisze "ile tego dodawać?" po wcześniejszym pytaniu o Ca Plus, detektuje że to follow-up, nie nowe pytanie o produkt!
6. business_reasoner.py - Mózg Biznesowy Systemu
Opowiadanie: To jest najbardziej inteligentny moduł! To jak doświadczony sprzedawca akwarystyki, który rozumie produkty, problemy klientów i potrafi doradzić.
Klasa BusinessReasoner zawiera:
Mapowanie Kategorii Produktów: 15+ kategorii jak "salts", "bacteria", "test_kits" z przypisanymi produktami
Mapowanie Problem-Rozwiązanie: Gdy klient ma problem z algami, wie że polecić AF NitraPhos Minus
Wykrywanie Konkurentów: Lista 15 firm konkurencyjnych
Logika Biznesowa: Rozumie różnicę między produktami do korekty (Ca Plus) a do maintenance (Component 1+2+3+)
Główne funkcje:
analyze(): Główna metoda która analizuje zapytanie przez pryzmat biznesowy
_check_competitors(): Sprawdza czy zapytanie dotyczy konkurencji
_find_category_for_query(): Wykrywa gdy klient pyta o całą kategorię produktów
_create_business_context(): Buduje kontekst biznesowy dla dalszej analizy
Przykład magii: Gdy klient pisze "mam niski wapń", business reasoner:
Wykrywa problem: low_calcium
Sugeruje korekty: Ca Plus, Calcium
Sugeruje maintenance: Component 1+2+3+
Dodaje notatkę że produkty Balling zawierają wiele elementów!
7. query_optimizer.py - Mistrz Optymalizacji Zapytań
Opowiadanie: To jest jak tłumacz który przekłada "ludzkie" pytania na "język wyszukiwarki"! Bierze pytanie użytkownika i tworzy 4-10 różnych zapytań które najlepiej znajdą odpowiedzi w bazie wektorowej.
Klasa QueryOptimizer:
Kluczowe metody:
_detect_comparison(): Wykrywa gdy użytkownik porównuje produkty ("Ca Plus vs Calcium")
_extract_mentioned_products(): Wyciąga nazwy produktów z zapytania
optimize(): Główna metoda która generuje zoptymalizowane zapytania
Zaawansowane funkcje:
Guaranteed Products: Produkty które na pewno zostanu znalezione (z business reasoner)
Category Support: Gdy user pyta o kategorię, tworzy zapytania dla każdego produktu
Problem-based Queries: Zamiast "AF NitraPhos Minus" tworzy "algae control methods"
Smart Fallback: Gdy AI zawiedzie, ma backup logikę
Przykład pracy:
Zapytanie: "Co masz na algi?"
Business reasoner wykrywa problem: algae
Query optimizer tworzy: ["algae control methods", "nitrate reduction", "phosphate removal", "AF NitraPhos Minus", "probiotic bacteria benefits"]
8. pinecone_client.py - Połączenie z Bazą Wektorową
Opowiadanie: To jest "bibliotekarz" który szuka w gigantycznej bazie wiedzy! Łączy się z Pinecone (baza wektorowa) i używa OpenAI embeddings żeby znaleźć najbardziej podobne treści.
Klasa PineconeSearchClient:
Główne metody:
_get_embedding(): Zamienia tekst na wektor liczb używając OpenAI
_detect_domain_from_context(): Auto-wykrywa czy to akwarium słodko czy morskie
search(): GŁÓWNA metoda hybrydowego wyszukiwania
_guaranteed_product_search(): Bezpośrednie wyszukiwanie konkretnych produktów
Hybrydowe wyszukiwanie (najważniejsza innowacja!):
Guaranteed Search: Bezpośrednio szuka produktów z business reasoner
Vector Search: Semantyczne wyszukiwanie dla każdego zoptymalizowanego zapytania
Merge Results: Łączy wyniki, guaranteed mają priorytet
Domain Filtering: Filtruje po typie akwarium
Przykład magii: Gdy szukasz "Ca Plus", guaranteed search znajdzie dokładnie "Ca Plus", a vector search znajdzie dodatkowo artykuły o wapniu, problemach z koralami, itp.
9. results_filter.py - Inteligentny Filtr Wyników
Opowiadanie: To jest jak "kontroler jakości" który przesyła tylko najlepsze wyniki! Używa ThreadPoolExecutor (zamiast AsyncIO) do równoległego przetwarzania chunków wyników.
Klasa DynamicParallelResultsFilter:
Główne cechy:
Chunk Processing: Dzieli wyniki na kawałki (domyślnie 6 per chunk)
Conservative Filtering: Lepiej zostawić za dużo niż za mało
Metadata Analysis: Analizuje PEŁNE metadata każdego wyniku
ThreadPoolExecutor: Przetwarza chunks równolegle dla szybkości
Filtrowanie Rules:
Direct Product Match - ZAWSZE zachowaj produkty wymienione przez użytkownika
Problem Solvers - Zachowaj produkty rozwiązujące problem
Educational Content - Zachowaj artykuły edukacyjne
No Duplicates - NIGDY nie usuwaj produktów o tej samej nazwie ale różnych URL!
Przykład: Gdy znajdzie 24 wyniki, dzieli na 4 chunki po 6, każdy chunk jest analizowany równolegle przez AI, potem wyniki są mergowane z uzasadnieniem.
10. confidence_scorer.py - Oceniacz Pewności Odpowiedzi
Opowiadanie: To jest jak "nauczyciel" który wystawia ocenę za odpowiedź! Analizuje wyniki wyszukiwania i stwierdza czy są wystarczająco dobre dla użytkownika.
Klasa ConfidenceScorer:
Główne metody:
_calculate_category_bonus(): Bonus points gdy znajdzie produkty z requested category
_create_evaluation_prompt(): Tworzy prompt z PEŁNYMI metadata do oceny
calculate_confidence(): Główna metoda obliczająca confidence 0.0-1.0
Kryteria oceny:
Category Match: Czy znalazł produkty z żądanej kategorii?
Business Intelligence: Czy wyniki pasują do business analysis?
Problem-Solution Fit: Czy znalazł rozwiązania dla wykrytego problemu?
Context Coherence: Czy wyniki pasują do kontekstu rozmowy?
Przykład: Gdy user pyta "jakie sole macie?", a system znajdzie Sea Salt, Reef Salt, Reef Salt Plus - confidence będzie wysokie bo pokrył całą kategorię!
11. response_formatter.py - Mistrz Pięknych Odpowiedzi
Opowiadanie: To jest jak "pisarz" który zamienia suche dane w piękne, pomocne odpowiedzi dla użytkowników! Najdłuższy plik (575 linii) bo musi obsłużyć wszystkie typy zapytań.
Klasa ResponseFormatter:
Główne funkcje:
_detect_dosage_query(): Wykrywa pytania o dawkowanie
_extract_dosage_info(): Wyciąga informacje o dawkowaniu z metadata
_get_product_URL(): Dobiera odpowiedni link (PL vs EN)
_has_mixed_domains(): Sprawdza czy są produkty dla różnych typów akwarium
Specjalne obsługi:
Special Intents: Osobne prompty dla greeting, business, competitor, etc.
Dosage Calculations: Integracja z calculation_helper dla obliczeń dawkowania
Mixed Domains: Oddzielne sekcje dla produktów słodko/morskich
Category Requests: Listuje WSZYSTKIE produkty z kategorii
Balling Method Warning: Ostrzega że Component produkty to maintenance, nie korekta
Przykład magii: Gdy user pyta "ile Ca Plus na 200L?", formatter:
Wykrywa że to dosage query
Wyciąga dawkowanie z metadata
Wywołuje calculation_helper
Formatuje odpowiedź: "Dla Twojego 200L akwarium: 4ml Ca Plus dziennie"
12. calculation_helper.py - Matematyk Akwarystyczny
Opowiadanie: To jest "kalkulator akwarystyczny"! Bezpieczne i dokładne obliczenia dawkowania, zmian parametrów, wymian wody.
Klasa CalculationHelper (wszystkie metody statyczne):
Główne funkcje:
extract_volume_from_query(): Wyciąga pojemność akwarium z tekstu ("200L tank" → 200)
calculate_dosage(): Proporcjonalne dawkowanie (10ml/100L × 200L = 20ml)
calculate_parameter_change(): Oblicza zmianę parametrów (Ca, Mg, KH)
validate_dosage_safety(): Sprawdza czy dawka nie jest za duża
format_dosing_schedule(): Formatuje harmonogram dawkowania
Przykład obliczeń:
Base: 5ml Ca Plus na 100L podnie
Target: 250L akwarium
Wynik: (5 ÷ 100) × 250 = 12.5ml dziennie
+ safety check czy nie za dużo
+ formatowanie: "12.5ml dziennie, można podzielić na 2 dawki po 6.25ml"
13. server.py - Serce API Serwera
Opowiadanie: To jest "główny serwer" całej aplikacji! FastAPI serwer który obsługuje wszystkie żądania z frontendu, zapisuje analytics do SQLite, eksportuje CSV.
Główne komponenty:
1. Pydantic Models: Definicje API (ChatRequest, ChatResponse, FeedbackRequest)
2. SQLite Database:
feedback table: oceny użytkowników
analyze table: szczegółowa analityka workflow
3. WorkflowAnalytics Class: Przechwytuje wszystkie dane z workflow
4. Główne Endpoints:
POST /chat: Główny endpoint czatu
POST /feedback: Przyjmuje feedback od użytkowników
GET /analytics/summary: Statystyki zbiorcze
GET /analytics/export/csv: Eksport analytics do CSV
GET /feedback/export/csv: Eksport feedback do CSV
Przykład życia zapytania:
Frontend wysyła POST /chat z message
Serwer tworzy ConversationState
Wywołuje assistant.process_query_sync()
Analytics przechwytuje wszystkie dane
Zapisuje do SQLite
Zwraca response do frontendu
14. workflow.py - Orkiestra LangGraph
Opowiadanie: To jest "dyrygent orkiestry"! Używa LangGraph do stworzenia workflow z węzłów i połączeń. Każdy węzeł ma timing wrapper do Analytics.
Główne komponenty:
1. Timing Wrapper: Dekorator który mierzy czas każdego węzła
2. Workflow Nodes:
load_product_names: Ładuje listę produktów
detect_intent_and_language: Wykrywa intencję
business_reasoner: Analiza biznesowa
optimize_query: Optymalizacja zapytań
search_products: Wyszukiwanie w Pinecone
intelligent_filter: Filtrowanie wyników
evaluate_confidence: Ocena confidence
format_response: Formatowanie odpowiedzi
3. Routing Logic:
route_intent(): Decyduje dokąd iść po wykryciu intencji
route_follow_up(): Specjalna logika dla follow-up questions
route_based_on_confidence(): Routing na podstawie confidence
4. Analytics Integration: Global workflow_analytics przechwytuje timing każdego węzła
Przykład przepływu:
Apply to .env
🗂️ KATALOG src/prompts/ - SZABLONY PROMPTÓW DLA AI
15. prompts/__init__.py - Loader Szablonów
Opowiadanie: To jest "bibliotekarz szablonów"! Funkcja load_prompt_template() ładuje zewnętrzne pliki .txt z promptami i podstawia zmienne.
Jak działa:
Bierze nazwę template'u ("intent_detection")
Otwiera plik intent_detection.txt
Podstawia zmienne: {user_query}, {chat_history}, etc.
Zwraca gotowy prompt dla OpenAI
Korzyści: Prompty są oddzielone od kodu, łatwo je edytować bez dotykania Python!
16. prompts/intent_detection.txt - Detektyw Intencji
Opowiadanie: To jest "instrukcja dla detektywa"! Dokładny prompt który tłumaczy ChatGPT jak wykrywać intencje użytkowników.
Kluczowe sekcje:
Context Analysis Rules: Zasady analizy kontekstu (np. "buy aiptasia" po rozmowie o "Aiptasia Shot" = chce kupić produkt, nie szkodnika!)
Intents Definition: 9 dokładnie zdefiniowanych intencji
Language Detection: Jak wykrywać język zapytania
Analysis Process: Krok-po-kroku proces analizy
Przykład magii: Prompt uczy AI że gdy ktoś po rozmowie o produkcie przeciw szkodnikom pisze "kup aiptasia", to chce kupić PRODUKT, nie szkodnika!
17. prompts/query_optimization.txt - Mistrz Optymalizacji
Opowiadanie: To jest "instrukcja dla tłumacza zapytań"! Uczy ChatGPT jak przekłuić ludzkie pytania na efektywne zapytania wyszukiwarki.
Kluczowe strategie:
Guaranteed Products Logic: Nie duplikuj produktów które już są gwarantowane
Smart Problem-Solution: Gdy produkt jest gwarantowany, szukaj problemów i metod
Category Support: Dla kategorii twórz zapytanie per produkt
No Numbers Rule: NIGDY nie wstawiaj konkretnych liczb do zapytań
Przykład strategii:
Guaranteed: ["AF NitraPhos Minus"]
Zamiast: "AF NitraPhos Minus for algae"
Twórz: "algae control methods", "nitrate reduction strategies"
18. prompts/results_filtering.txt - Selekcjoner Wyników
Opowiadanie: To jest "instrukcja dla kontrolera jakości"! Uczy AI jak wybierać najlepsze wyniki z wyszukiwania.
Główne zasady:
Direct Product Match: ZAWSZE zachowaj produkty wymienione przez użytkownika
Conservative Approach: Lepiej za dużo niż za mało
No Merging Rule: NIGDY nie łącz produktów o tej samej nazwie ale różnych URL
Educational Value: Zachowuj artykuły edukacyjne
Przykład: Gdy znajdzie 2x "Mg Plus" z różnymi URL, to są RÓŻNE produkty (może jeden to instrukcja, drugi to opis produktu) - zachowaj OBA!
19. prompts/confidence_evaluation.txt - Egzaminator Odpowiedzi
Opowiadanie: To jest "instrukcja dla nauczyciela"! Uczy AI jak oceniać czy znalezione wyniki odpowiadają na pytanie użytkownika.
Kryteria oceny:
Category Match: Najwyższy priorytet dla zapytań o kategorie
Business Intelligence Alignment: Czy pasuje do business analysis
Problem-Solution Fit: Czy ma rozwiązania dla wykrytych problemów
Context Coherence: Czy pasuje do kontekstu rozmowy
Przykład logiki: Gdy user pyta "jakie sole macie?" i znajdzie Sea Salt, Reef Salt, Reef Salt Plus → confidence HIGH bo pokrył całą kategorię!
20. prompts/response_formatting.txt - Mistrz Eleganckich Odpowiedzi
Opowiadanie: To jest "instrukcja dla pisarza odpowiedzi"! Najdłuższy prompt (105 linii) bo musi obsłużyć wszystkie możliwe scenariusze odpowiedzi.
Kluczowe sekcje:
Critical No-Merge Rule: Products z tą samą nazwą ale różnymi URL to RÓŻNE produkty
Category Requests: Pokaż WSZYSTKIE produkty z kategorii
Dosage Calculations: Użyj dokładnie tych obliczeń które dostałeś
Mixed Domain Handling: Rozdziel produkty słodko/morskie
Support Contact Rule: NIGDY automatycznie nie dodawaj kontaktu support
Językowe wersje: Różne formatowanie dla PL ("Polecamy:") vs EN ("We recommend:")
21. prompts/response_followup.txt - Ekspert od Kontynuacji
Opowiadanie: To jest "instrukcja dla eksperta follow-up"! Krótki ale precyzyjny prompt dla pytań kontynuujących rozmowę.
Główne zadania:
Analizuj follow-up w kontekście poprzedniej rozmowy
Używaj cached metadata do szczegółowych informacji
Obliczaj dawkowanie gdy podana jest pojemność
Sugeruj jakie dodatkowe info jest potrzebne
Przykład: Gdy po rozmowie o Ca Plus user pyta "ile na 300L?", używa cached info + calculation_helper.
📊 PLIKI DOKUMENTACYJNE
22. analytics-readme.md - Przewodnik po Analytics
Opowiadanie: To jest "podręcznik analytics"! Szczegółowe instrukcje jak używać systemu analitycznego - od bazy SQLite po API endpoints i przykłady SQL queries.
23. csv-export-docs.md - Przewodnik po Eksporcie
Opowiadanie: To jest "instrukcja eksportu"! Jak eksportować dane do CSV, jakie kolumny, przykłady curl i integracja z React.
🎯 PODSUMOWANIE DZIAŁANIA CAŁEGO SYSTEMU
Życie jednego zapytania "Co to jest Ca Plus?" krok po kroku:
Frontend → POST /chat → server.py
server.py → tworzy ConversationState → workflow.py
workflow.py → load_product_names → ładuje listę produktów
workflow.py → intent_detector.py → wykrywa "product_query", język "pl"
workflow.py → business_reasoner.py → analizuje czy Ca Plus to korekta/maintenance
workflow.py → query_optimizer.py → tworzy ["Ca Plus", "calcium supplement", "coral calcium"]
workflow.py → pinecone_client.py → wyszukuje w bazie wektorowej
workflow.py → results_filter.py → filtruje najlepsze wyniki
workflow.py → confidence_scorer.py → ocenia confidence na 0.85
workflow.py → response_formatter.py → tworzy piękną odpowiedź
server.py → zapisuje analytics do SQLite → zwraca response
Frontend → pokazuje odpowiedź użytkownikowi
Cały proces zajmuje ~2-3 sekundy i jest rejestrowany w bazie dla analytics!
To jest naprawdę zaawansowany, produkcyjny system RAG z inteligentnym workflow, analytics w czasie rzeczywistym i przemyślaną architekturą! 🚀
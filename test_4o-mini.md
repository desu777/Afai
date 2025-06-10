
You: jakbyś miał polecić jeden to który?

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'jakbyś miał polecić jeden to który?'
💬 [DEBUG IntentDetector] Historia konwersacji: 2 wiadomości
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'follow_up', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks for a single product recommendation for SPS coral growth, following previous detailed product suggestions.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.FOLLOW_UP', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User asks for a single product recommendation for SPS coral growth, following previous detailed product suggestions.
⏱️  [detect_intent_and_language] Node execution time: 2.003s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'jakbyś miał polecić jeden to który?'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 📦 [BusinessReasoner] Category 'wzrost_korali' with 3 products
🔍 🔧 [BusinessReasoner] Problem: supporting SPS coral growth → 3 solutions
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.FOLLOW_UP
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 🔍 [BusinessReasoner] Search enhancement: SPS coral growth supplements...
🔍 💡 [BusinessReasoner] Interpretation: User asks for a single product recommendation for SPS coral growth support....
⏱️  [business_reasoner] Node execution time: 4.563s
🔍 🚦 [Router] Routing for intent='Intent.FOLLOW_UP'
🔍 ➡️ [Router] Routing to: follow_up_router (follow-up question)

📍 Executing node: 'business_reasoner'
----------------------------------------
🔍 🔄 [Follow-up Router] Checking if can handle follow-up with cache
⏱️  [follow_up_router] Node execution time: 0.000s
⏱️  [follow_up_router] Node execution time: 0.000s
🔍 ✅ [Follow-up Router] Found reference to cached content, using cache

📍 Executing node: 'follow_up_router'
----------------------------------------

🔄 [DEBUG Follow-up Handler] Handling follow-up question with cache

🔄 [DEBUG Follow-up] Creating prompt for follow-up in language: pl
📦 [DEBUG Follow-up] Cache contains 5 items
✅ [DEBUG Follow-up Handler] Response generated using cache
⏱️  [handle_follow_up] Node execution time: 8.208s

📍 Executing node: 'handle_follow_up'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 14.774 seconds
------------------------------------------------------------

Jeśli miałbym polecić tylko jeden produkt na wzrost koralowców SPS, to byłby to **AF Power Elixir**.

Dlaczego?
- Jest to zaawansowany suplement płynny, który kompleksowo wspiera wzrost tkanek, intensywną kolorystykę oraz rozciąganie polipów.
- Zawiera idealnie zbilansowany zestaw aminokwasów i witamin, które wzmacniają symbiozę z zooxanthellae i poprawiają fotosyntezę.
- Działa na wiele aspektów zdrowia korali jednocześnie, co przekłada się na szybszy i zdrowszy wzrost.
- Można go dawkować codziennie, co pozwala na stałe i systematyczne wspieranie koralowców.
- Produkt jest gotowy do użycia, nie wymaga rozcieńczania ani specjalnego przygotowania.

**Dawkowanie:** 4 ml na 100 l wody codziennie.

Więcej informacji i zakup:
[AF Power Elixir – szczegóły produktu](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-power-elixir/)

Jeśli chcesz, mogę pomóc dobrać dawkowanie do Twojego akwarium lub zaproponować uzupełnienie o inne suplementy dla jeszcze lepszych efektów.

------------------------------------------------------------

You: quit

👋 Goodbye! Thank you for using Aquaforest AI Assistant.
PS C:\Users\kubas\Desktop\aquaforest-rag> python src/main.py

============================================================
🔧 CONFIGURATION LOADED
============================================================
📍 Debug Mode: ENABLED
📍 OpenAI Model: gpt-4o-mini
📍 Embedding Model: text-embedding-3-small
📍 Pinecone Index: aquaforestv2
📍 Default K Value: 12
📍 Enhanced K Value: 12
📍 Confidence Threshold: 0.5 (🆕 LOWERED)
📍 Supported Languages: pl, en, de, fr, es, it
📍 Competitors tracked: 15
============================================================

🔍 🏗️ [Workflow] Creating enhanced LangGraph workflow...
🔍 🔧 [Workflow] Using ENHANCED_K_VALUE=12
🔍    ➕ Added node: detect_intent
🔍    ➕ Added node: load_products
🔍    ➕ Added node: business_reasoner
🔍    ➕ Added node: optimize_query
🔍    ➕ Added node: search_pinecone
🔍    ➕ Added node: intelligent_filter
🔍    ➕ Added node: evaluate_confidence
🔍    ➕ Added node: format_response
🔍    ➕ Added node: escalate_support
🔍    ➕ Added node: handle_follow_up
🔍    ➕ Added node: follow_up_router
🔍 ✅ [Workflow] Enhanced workflow created and compiled

============================================================
🐠 Aquaforest AI Assistant - Interactive Mode
============================================================

Commands:
  • 'quit' or 'exit' - Exit the program
  • 'debug' - Toggle debug mode
  • 'new' - Start a new conversation
  • 'help' - Show this help message

============================================================

You: moje rybki są blade, co mogę zrobić?

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'moje rybki są blade, co mogę zrobić?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.9, 'context_note': 'The user is asking about their fish being pale, indicating a potential problem that may require a product solution.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.9
🧠 [DEBUG IntentDetector] Context note: The user is asking about their fish being pale, indicating a potential problem that may require a product solution.
⏱️  [detect_intent_and_language] Node execution time: 13.807s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 20.064s
⏱️  [optimize_product_query] Node execution time: 13.687s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.587s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 4 of 6 results
   Best match: AF Color Up – Color-Boosting Pellet Fish Food with Natural Carotenoids
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 3 of 6 results
   Best match: AF Amino Mix
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 6 results
💭 [DynamicFilter] Chunk 1: kept 4/6, quality: high. Chunk 2: kept 2/6, quality: high. Total knowledge articles: 0
⏱️  [intelligent_results_filter] Node execution time: 20.499s

📊 [DEBUG ConfidenceScorer] Evaluating 6 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'moje rybki są blade, co mogę zrobić?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.8
   - Category bonus: +0.0
   - Final confidence: 0.8
   - Best matches: ['AF Marine Mix S', 'AF Protein Power', 'AF Marine Flakes']
   - Category coverage: The results cover the category of fish food and supplementation well, providing multiple options that can contribute to fish health and coloration.
   - Knowledge value: The results contain valuable information about the nutritional content and benefits of the products, which can help the user make informed decisions about their fish care.
   - Domain consistency: All products listed are suitable for marine fish, aligning with the user's likely aquarium type based on the context of the query.
   - Context mismatch: There is no significant context mismatch; the results are relevant to the user's query about pale fish.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.8000
⏱️  [evaluate_confidence] Node execution time: 25.868s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.80 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 6 results
🎯 [DEBUG ResponseFormatter] Mixed domains detected, will present both
✅ [DEBUG ResponseFormatter] Response generated (1918 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 50.743s
Twoje rybki mogą być blade z kilku powodów, w tym z niedoboru składników odżywczych lub stresu. Oto kilka kroków, które możesz podjąć, aby poprawić ich kondycję:

### Dla akwarium morskiego:

1. **AF Marine Mix S**
   **Opis:** Zrównoważona, wysokiej jakości granulatowa karma dla małych ryb mięsożernych i wszystkożernych.
   **Korzyści:** Bogata w białko zwierzęce, wspiera zdrowy wzrost tkanek, mięśni i skóry ryb.
   **Dawkowanie:** Karm kilka razy dziennie w małych porcjach.
   **Dostępne rozmiary:** 120g
   **Więcej informacji:** [AF Marine Mix S](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-marine-mix-s/)

2. **AF Protein Power**
   **Opis:** Wysokiej jakości, miękka karma w granulkach dla młodych ryb morskich.
   **Korzyści:** Wspiera szybki i zdrowy wzrost, poprawia kolorację.
   **Dawkowanie:** Karm kilka razy dziennie w małych porcjach.
   **Dostępne rozmiary:** 120g
   **Więcej informacji:** [AF Protein Power](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-protein-power/)

3. **AF Marine Flakes**
   **Opis:** Flake food z dodatkiem alg nori, idealny dla ryb roślinożernych i wszystkożernych.
   **Korzyści:** Wspiera zdrowy rozwój i naturalną kolorację ryb.
   **Dawkowanie:** Karm 1-2 razy dziennie w porcjach, które ryby mogą zjeść w kilka minut.
   **Dostępne rozmiary:** 50g
   **Więcej informacji:** [AF Marine Flakes](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-marine-flakes/)

### Dodatkowe zasoby:
- Zadbaj o odpowiednie warunki w akwarium, takie jak temperatura, pH i twardość wody, ponieważ mogą one wpływać na zdrowie ryb.
- Regularne testowanie parametrów wody pomoże w identyfikacji ewentualnych problemów.

Jeśli potrzebujesz więcej informacji lub masz dodatkowe pytania, skontaktuj się z nami pod adresem support@aquaforest.eu lub telefonicznie pod numerem +48 14 691 79 79.

------------------------------------------------------------
 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'mam problem z pH, ciągle spada'
💬 [DEBUG IntentDetector] Historia konwersacji: 2 wiadomości
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'follow_up', 'language': 'pl', 'confidence': 0.95, 'context_note': 'The user is continuing the conversation about their aquarium issues, specifically addressing a problem with pH levels, which is related to the previous discussion about the health of their fish.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.FOLLOW_UP', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: The user is continuing the conversation about their aquarium issues, specifically addressing a problem with pH levels, which is related to the previous discussion about the health of their fish.
⏱️  [detect_intent_and_language] Node execution time: 9.093s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 19.127s
⏱️  [follow_up_router] Node execution time: 0.000s
⏱️  [follow_up_router] Node execution time: 0.000s
⏱️  [optimize_product_query] Node execution time: 17.553s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.672s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 6 of 6 results
   Best match: How to Raise Low pH in Aquarium – Causes, Symptoms & Effective Methods
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 4 of 6 results
   Best match: KH Plus – Liquid KH Booster for Rapid Carbonate Hardness Correction
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 9 results
💭 [DynamicFilter] Chunk 1: kept 6/6, quality: high. Chunk 2: kept 3/6, quality: high. Total knowledge articles: 2
⏱️  [intelligent_results_filter] Node execution time: 24.605s

📊 [DEBUG ConfidenceScorer] Evaluating 9 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'mam problem z pH, ciągle spada'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.6
   - Category bonus: +0.0
   - Final confidence: 0.6
   - Best matches: ['How to Raise Low pH in Aquarium – Causes, Symptoms & Effective Methods', 'AF Air Scrubber - CO2 Reactor for pH Stabilization in Reef Aquarium', 'KH Buffer – Carbonate Hardness Buffer for Stable Reef Aquarium Parameters']
   - Category coverage: The results include products related to pH stabilization and water treatment, but do not cover a broad range of pH control solutions or specific products that might be more directly applicable to the user's situation.
   - Knowledge value: The educational content is valuable, particularly the article on raising low pH, as it provides insights into causes and solutions, which could help the user understand their issue better.
   - Domain consistency: The domain of the products and information is consistent with marine aquariums, which aligns with the user's context.
   - Context mismatch: There is a slight mismatch in context as the user is specifically concerned about a continuous drop in pH, while the results provide more general information about raising pH and maintaining stability.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.6000
⏱️  [evaluate_confidence] Node execution time: 28.164s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.60 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.FOLLOW_UP', language='pl'
📊 [DEBUG ResponseFormatter] Processing 9 results
✅ [DEBUG ResponseFormatter] Response generated (2381 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 65.147s
Twoje problemy z pH w akwarium mogą być spowodowane różnymi czynnikami, takimi jak zanieczyszczenia, niewłaściwe warunki wody lub nadmiar CO2. Oto kilka kroków, które możesz podjąć, aby podnieść i ustabilizować pH w swoim akwarium:

### Dla akwarium morskiego:

1. **AF Air Scrubber**
   **Opis:** Reaktor do usuwania CO2, który stabilizuje pH w akwarium morskim.
   **Korzyści:** Redukuje poziom CO2, co przyczynia się do podniesienia pH oraz stabilizacji jego poziomów w ciągu dnia i nocy.
   **Dawkowanie:** Używaj zgodnie z instrukcją producenta.
   **Dostępne rozmiary:** 1 szt.
   **Więcej informacji:** [AF Air Scrubber](https://aquaforest.eu/pl/produkty/seawater/wyposazenie-akwarium/af-air-scrubber/)

2. **KH Buffer**
   **Opis:** Wysokiej jakości preparat do utrzymywania stabilnej twardości węglanowej (KH) w akwariach morskich.
   **Korzyści:** Stabilizuje pH, co jest kluczowe dla zdrowia koralowców i innych organizmów morskich.
   **Dawkowanie:** 100 ml roztworu podnosi KH o 2.6 dKH w 100 l wody.
   **Dostępne rozmiary:** 1200 g, 5000 g
   **Więcej informacji:** [KH Buffer](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-buffer/)

3. **KH Plus**
   **Opis:** Skoncentrowany płyn do szybkiego podnoszenia twardości węglanowej (KH) w akwariach morskich.
   **Korzyści:** Szybko przywraca równowagę jonową i wspiera wzrost koralowców.
   **Dawkowanie:** 10 ml podnosi KH o 0.5 dKH w 100 l wody.
   **Dostępne rozmiary:** 1000 ml, 2000 ml
   **Więcej informacji:** [KH Plus](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-plus/)

4. **KH Pro**
   **Opis:** Ultra skoncentrowany preparat do szybkiego podnoszenia twardości węglanowej (KH) oraz poziomu potasu w akwariach morskich.     
   **Korzyści:** Stabilizuje pH i wspiera rozwój koralowców.
   **Dawkowanie:** 5 ml podnosi KH o 0.5 dKH w 100 l wody.
   **Dostępne rozmiary:** 1000 ml, 2000 ml
   **Więcej informacji:** [KH Pro](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-pro/)

### Dodatkowe zasoby:
- Regularnie testuj pH oraz inne parametry wody, aby zidentyfikować ewentualne problemy.
- Utrzymuj odpowiednią wentylację akwarium, aby zredukować nadmiar CO2.

Jeśli potrzebujesz więcej informacji lub masz dodatkowe pytania, skontaktuj się z nami pod adresem support@aquaforest.eu lub telefonicznie pod numerem +48 14 691 79 79.

------------------------------------------------------------




🆕 Starting new conversation...
----------------------------------------
You: my corals are turning brown, help!

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'my corals are turning brown, help!'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'en', 'confidence': 0.9, 'context_note': 'The user is expressing a problem with their corals turning brown, indicating a need for assistance or a solution related to aquarium care.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='en', Confidence=0.9
🧠 [DEBUG IntentDetector] Context note: The user is expressing a problem with their corals turning brown, indicating a need for assistance or a solution related to aquarium care.
⏱️  [detect_intent_and_language] Node execution time: 14.201s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 19.732s
⏱️  [optimize_product_query] Node execution time: 16.029s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 5.615s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 6 of 6 results
   Best match: AF Vitality – Vitamin Supplement for Coral Coloration & Health
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 4 of 6 results
   Best match: AF Pure Food – 100% Natural Powdered Supplement for Coral Growth and Calcification
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 9 results
💭 [DynamicFilter] Chunk 1: kept 6/6, quality: high. Chunk 2: kept 3/6, quality: high. Total knowledge articles: 0
⏱️  [intelligent_results_filter] Node execution time: 21.655s

📊 [DEBUG ConfidenceScorer] Evaluating 9 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'my corals are turning brown, help!'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.85
   - Category bonus: +0.0
   - Final confidence: 0.85
   - Best matches: ['AF Vitality – Vitamin Supplement for Coral Coloration & Health', 'AF Energy – High-Nutrition Concentrate for SPS Corals', 'AF Power Elixir – Advanced Amino Acid and Vitamin Blend for Coral Growth and Coloration', 'AF Growth Boost – Rapid Growth Supplement for All Corals']
   - Category coverage: The results include several products from the coral supplements and foods categories, which are relevant to the user's query about coral health. However, there is a lack of specific anti-phosphate products or targeted solutions for browning corals.        
   - Knowledge value: The results provide valuable information about various coral supplements and their benefits, which can help the user understand how to improve their coral's condition.
   - Domain consistency: All products listed are appropriate for marine aquariums, aligning well with the user's context of caring for corals.
   - Context mismatch: There are no significant context mismatches; the results are generally aligned with the user's concern about coral health and coloration.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.8500
⏱️  [evaluate_confidence] Node execution time: 33.330s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.85 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='en'
📊 [DEBUG ResponseFormatter] Processing 9 results
✅ [DEBUG ResponseFormatter] Response generated (3244 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 45.548s
I'm sorry to hear that your corals are turning brown! This can be a sign of stress or nutrient deficiency. Here are some solutions that may help improve their health and coloration:

### Recommended Products

1. **AF Energy**
   - **Description**: A highly nutritious food concentrate designed specifically for all types of corals, especially SPS corals. It enhances vibrant coral coloration and promotes proper development.
   - **Key Benefits**: Contains natural extracts and Omega fatty acids that limit the growth of zooxanthellae, which can help improve coral coloration.
   - **Dosage**: 1 drop per 100L every other day after lights out.
   - **Available Sizes**: 10ml, 50ml
   - **Learn more**: [AF Energy](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-energy/)

2. **AF Vitality**
   - **Description**: A concentrated vitamin supplement designed to support coral health, immunity, and vibrant coloration.
   - **Key Benefits**: Replenishes vitamins lost during filtration, improving coral condition and enhancing colors.
   - **Dosage**: 1 drop per 100L every other day after lights out.
   - **Available Sizes**: 10ml, 50ml
   - **Learn more**: [AF Vitality](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-vitality/)

3. **AF Power Elixir**
   - **Description**: An advanced liquid supplement for marine aquariums that supports coral growth and vivid coloration.
   - **Key Benefits**: Enhances zooxanthellae coloration and strengthens the symbiotic relationship between corals and their algae.
   - **Dosage**: 4 ml per 100L daily for average coral stocking.
   - **Available Sizes**: 200ml, 1000ml, 2000ml
   - **Learn more**: [AF Power Elixir](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-power-elixir/)

4. **AF Growth Boost**
   - **Description**: A coral supplement that supports rapid growth and healthy metabolism in all types of corals.
   - **Key Benefits**: Improves polyp extension and accelerates adaptation of frags to new conditions.
   - **Dosage**: 1 measuring spoon per 100L after lights out.
   - **Available Sizes**: 35g
   - **Learn more**: [AF Growth Boost](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-growth-boost/)

5. **AF Power Food**
   - **Description**: A highly nutritious powdered food formulated for all types of corals, focusing on SPS and demanding species.
   - **Key Benefits**: Provides essential nutrients and supports rapid coral growth and coloration.
   - **Dosage**: 1 measuring spoon per 100L, minimum once a week.
   - **Available Sizes**: 20g
   - **Learn more**: [AF Power Food](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-power-food/)

### Additional Tips
- Ensure your water parameters (salinity, pH, nitrate, phosphate, etc.) are within the ideal range for your corals.
- Consider reducing light intensity or duration if your corals are experiencing stress from lighting conditions.
- Regular water changes can help maintain a stable environment.

If you continue to have issues or need further assistance, feel free to reach out to our support team at support@aquaforest.eu or call +48 14 691 79 79.

I hope this helps your corals recover and thrive!

------------------------------------------------------------


 Starting new conversation...
----------------------------------------
You: jak stosować amino mixa?

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'jak stosować amino mixa?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.9, 'context_note': "The user is asking how to use 'amino mix', which indicates a specific inquiry about the product's application."}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.9
🧠 [DEBUG IntentDetector] Context note: The user is asking how to use 'amino mix', which indicates a specific inquiry about the product's application.
⏱️  [detect_intent_and_language] Node execution time: 20.602s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 28.503s
⏱️  [optimize_product_query] Node execution time: 15.800s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.369s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 2: keeping 2 of 6 results
   Best match: Aquaforest Probiotic Method – How to Maintain Ultra-Low Nutrients and Healthy Corals with Probiotic Bacteria
   Quality: high
✅ [DynamicFilter] Chunk 1: keeping 1 of 6 results
   🎯 Found mentioned products: ['AF Amino Mix']
   Best match: AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 3 results
💭 [DynamicFilter] Chunk 1: kept 1/6, quality: high. Chunk 2: kept 2/6, quality: high. Found mentioned products: ['AF Amino Mix']. Total knowledge articles: 1
⏱️  [intelligent_results_filter] Node execution time: 24.122s

📊 [DEBUG ConfidenceScorer] Evaluating 3 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'jak stosować amino mixa?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.9
   - Category bonus: +0.0
   - Final confidence: 0.9
   - Best matches: ['AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition', 'Aquaforest Probiotic Method – How to Maintain Ultra-Low Nutrients and Healthy Corals with Probiotic Bacteria']
   - Category coverage: The results effectively cover the category of amino acid supplements for aquariums, specifically focusing on AF Amino Mix, which is the primary product of interest.
   - Knowledge value: The educational content is valuable as it provides insights into the benefits of amino acids for coral health and the overall aquarium ecosystem, which can enhance the user's understanding of the product's importance.
   - Domain consistency: The domain is consistent with the user's query, focusing on seawater aquariums and coral health, which is appropriate given the context of using AF Amino Mix.
   - Context mismatch: There are no significant context mismatches; the results are relevant to the user's query about using amino mixes in aquariums.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.9000
⏱️  [evaluate_confidence] Node execution time: 31.098s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.90 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 3 results
✅ [DEBUG ResponseFormatter] Response generated (1360 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 3 results
⏱️  [format_final_response] Node execution time: 29.726s
**AF Amino Mix** to kompleksowy suplement aminokwasowy, który zawiera skoncentrowane aminokwasy niezbędne do zdrowego wzrostu koralowców. Stosowanie mocnych skimmerów w akwariach morskich często prowadzi do niedoborów aminokwasów i sterylizacji wody, co może powodować blaknięcie koralowców. AF Amino Mix uzupełnia wodę we wszystkie niezbędne aminokwasy, zapobiega blaknięciu koralowców i poprawia ich kolory.

### Jak stosować AF Amino Mix?

- **Dawkowanie:** 1 kropla na 100L wody
- **Częstotliwość:** co drugi dzień
- **Czas podawania:** po zgaszeniu świateł

**Dostępne rozmiary:** 10ml, 50ml
**Więcej informacji:** [AF Amino Mix](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-amino-mix/)

### Kluczowe korzyści:
- Zwiększa ilość zooxanthellae, co wspiera produkcję pigmentów fotosyntetycznych, takich jak chlorofil.
- Poprawia jakość fotosyntezy, co pozwala koralowcom czerpać więcej energii ze światła.
- Regularne stosowanie poprawia odporność i przyspiesza wzrost koralowców.

**Polecamy:** Użycie AF Amino Mix w połączeniu z innymi produktami, takimi jak AF Energy, AF Build i AF Vitality, aby maksymalizować zdrowie koralowców i ich intensywność kolorów.

Jeśli masz dodatkowe pytania lub potrzebujesz więcej informacji, skontaktuj się z nami pod adresem support@aquaforest.eu lub telefonicznie pod numerem +48 14 691 79 79.




🆕 Starting new conversation...
----------------------------------------
You: prowadzę Balling, zużycie Ca 20ppm/dzień, jaka dawka Components Pro?

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'prowadzę Balling, zużycie Ca 20ppm/dzień, jaka dawka Components Pro?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.9, 'context_note': 'The user is asking about the dosage of Components Pro in relation to their calcium consumption, which indicates a specific inquiry about a product.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.9
🧠 [DEBUG IntentDetector] Context note: The user is asking about the dosage of Components Pro in relation to their calcium consumption, which indicates a specific inquiry about a product.
⏱️  [detect_intent_and_language] Node execution time: 13.887s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 17.154s
⏱️  [optimize_product_query] Node execution time: 14.147s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.404s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 4 of 6 results
   🎯 Found mentioned products: ['Components Pro']
   Best match: Components Pro – Highly Efficient Set of Micro and Macro Elements for Marine Aquariums
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 1 of 6 results
   Best match: Component 1+2+3+ Concentrate – Compact Balling Method Set for Marine Aquariums
   Quality: medium
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 5 results
💭 [DynamicFilter] Chunk 1: kept 4/6, quality: high. Chunk 2: kept 1/6, quality: medium. Found mentioned products: ['Components Pro']. Total knowledge articles: 1
⏱️  [intelligent_results_filter] Node execution time: 21.883s

📊 [DEBUG ConfidenceScorer] Evaluating 5 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'prowadzę Balling, zużycie Ca 20ppm/dzień, jaka dawka Components Pro?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.85
   - Category bonus: +0.0
   - Final confidence: 0.85
   - Best matches: ['Components Pro – Highly Efficient Set of Micro and Macro Elements for Marine Aquariums', 'Balling Method in Reef Aquarium']
   - Category coverage: The results cover the relevant category of reef supplementation and provide information on the specific product (Components Pro) that the user is inquiring about.
   - Knowledge value: The educational content provided in the results is valuable, as it explains the Balling method and the importance of stable water parameters for coral health, which is beneficial for the user.
   - Domain consistency: The domain of the results is consistent with the user's interest in marine aquariums and reef care, ensuring that the information is applicable to their context.
   - Context mismatch: There are no significant context mismatches; the results are relevant to the user's query about the Balling method and calcium consumption.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.8500
⏱️  [evaluate_confidence] Node execution time: 26.354s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.85 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 5 results
✅ [DEBUG ResponseFormatter] Response generated (1265 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 27.935s
Aby obliczyć dawkowanie dla Twojego akwarium, które zużywa 20 ppm Ca dziennie, możesz skorzystać z systemu **Components Pro**. Zgodnie z zaleceniami, dla średniego obciążenia SPS w akwarium, sugerowane dawkowanie wynosi 12 ml na 100 litrów wody dziennie, podzielone na jak najwięcej małych dawek w ciągu dnia.

**Dawkowanie dla Twojego akwarium:**
- Jeśli Twoje akwarium ma np. 100 litrów, powinieneś podać 12 ml każdego z trzech komponentów dziennie.
- W przypadku 200 litrów, dawkowanie wzrasta do 24 ml każdego komponentu dziennie.

**Polecamy:**
- **Components Pro** – Zestaw wysoko skoncentrowanych suplementów mikro i makroelementów, zaprojektowany dla zaawansowanej opieki nad akwarium morskim. Umożliwia utrzymanie optymalnych poziomów KH, Ca i Mg.
  - **Dawkowanie:** 12 ml na 100 l wody dziennie, podzielone na małe dawki.
  - **Dostępne rozmiary:** 3x5L
  - **Więcej informacji:** [Components Pro](https://aquaforest.eu/pl/produkty/lab/makroelementy/components-pro/)

Pamiętaj, aby regularnie testować parametry wody, aby dostosować dawkowanie do rzeczywistego zużycia przez koralowce.

Jeśli masz dodatkowe pytania lub potrzebujesz dalszej pomocy, skontaktuj się z nami pod adresem support@aquaforest.eu lub telefonicznie pod numerem +48 14 691 79 79.

------------------------------------------------------------

You: co to jest metoda Balinga

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'co to jest metoda Balinga'
💬 [DEBUG IntentDetector] Historia konwersacji: 2 wiadomości
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'follow_up', 'language': 'pl', 'confidence': 0.9, 'context_note': 'User is asking for clarification about the Balling method, which relates to the previous discussion about dosing Components Pro.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.FOLLOW_UP', Language='pl', Confidence=0.9
🧠 [DEBUG IntentDetector] Context note: User is asking for clarification about the Balling method, which relates to the previous discussion about dosing Components Pro.
⏱️  [detect_intent_and_language] Node execution time: 20.962s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 18.253s
⏱️  [follow_up_router] Node execution time: 0.000s
⏱️  [follow_up_router] Node execution time: 0.001s

🔄 [DEBUG Follow-up Handler] Handling follow-up question with cache

🔄 [DEBUG Follow-up] Creating prompt for follow-up in language: pl
📦 [DEBUG Follow-up] Cache contains 5 items
✅ [DEBUG Follow-up Handler] Response generated using cache
⏱️  [handle_follow_up] Node execution time: 48.558s
Metoda Ballinga to popularna technika stosowana w akwarystyce morskiej, która ma na celu utrzymanie stabilnych parametrów wody, co jest kluczowe dla zdrowego wzrostu koralowców. Została opracowana w latach 90. przez Hansa-Wernera Ballinga i skupia się na codziennym mikro-dawkowaniu trzech oddzielnych roztworów, które uzupełniają niezbędne pierwiastki: twardość węglanową (KH), wapń (Ca), magnez (Mg) oraz mikroelementy.

**Kluczowe kroki w implementacji metody Ballinga:**
1. Zmierz podstawowe wartości KH, Ca i Mg przez kilka dni bez wcześniejszej suplementacji, aby określić dzienne zużycie.
2. Oblicz i rozpocznij dawkowanie wybranych roztworów Ballinga, dzieląc dzienną ilość na jak najwięcej małych dawek (najlepiej z użyciem pompy dozującej), aby uniknąć skoków parametrów.
3. Kontynuuj regularne testowanie wody, wprowadzając stopniowe korekty dawkowania w zależności od zużycia przez koralowce i obciążenia akwarium.

**Zalety metody Ballinga:**
- Utrzymuje stabilne KH, Ca, Mg i mikroelementy, co sprzyja zdrowym i kolorowym koralowcom.
- Zapobiega wahaniom i niedoborom, które mogą stresować organizmy rafowe.
- Można dostosować do wszystkich rozmiarów zbiorników i gęstości koralowców.

Więcej informacji na temat metody Ballinga znajdziesz w artykule na stronie Aquaforest: [Metoda Ballinga w akwarium morskim](https://aquaforest.eu/pl/baza-wiedzy/metoda-ballinga-w-akwarium-morskim-blog-o-akwarystyce-zasoby-aquaforest/).

Jeśli masz dodatkowe pytania dotyczące konkretnego aspektu metody Ballinga lub potrzebujesz więcej informacji, daj znać!

------------------------------------------------------------


🤖 Assistant:
You: moje rybki są blade, co mogę zrobić?

🤖 Assistant:

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'moje rybki są blade, co mogę zrobić?'
🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'moje rybki są blade, co mogę zrobić?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks about pale fish and what can be done, indicating a new question about aquariu🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'moje rybki są blade, co mogę zrobić?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks about pale fish and what can be done, indicating a new question about aquariu🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks about pale fish and what can be done, indicating a new question about aquarium fish health.'}
m fish health.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User asks about pale fish and what can be done, indicating a new question about aquarium fish health.
⏱️  [detect_intent_and_language] Node execution time: 2.225s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 5.716s
⏱️  [optimize_product_query] Node execution time: 4.051s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.517s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 4 of 6 results
   Best match: Fish V – Multivitamin Immunity Booster for All Aquarium Fish
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 5 of 6 results
   Best match: Garlic Essence – Natural Garlic and Omega-3 Supplement for Aquarium Fish Immunity
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 8 results
💭 [DynamicFilter] Chunk 1: kept 4/6, quality: high. Chunk 2: kept 4/6, quality: high. Total knowledge articles: 5
⏱️  [intelligent_results_filter] Node execution time: 11.659s

📊 [DEBUG ConfidenceScorer] Evaluating 8 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'moje rybki są blade, co mogę zrobić?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.7
   - Category bonus: +0.0
   - Final confidence: 0.7
   - Best matches: ['Fish V – Multivitamin Immunity Booster for All Aquarium Fish', 'Garlic Essence – Natural Garlic and Omega-3 Supplement for Aquarium Fish Immunity', 'AF Vege Strength – High-Fiber Vegetable Pellets with Spirulina and Krill for Herbivorous & Omnivorous Fish', 'AF Vege Clip – Complete Herbivore & Omnivore Fish Food with Glass Clip']
   - Category coverage: The query is a problem/solution type rather than a category request. The results cover relevant product categories (fish vitamins, supplements, and foods) that can help with fish vitality and coloration but do not cover all possible causes or treatments for pale fish comprehensively.
   - Knowledge value: Moderate. The knowledge articles provide useful background on aquarium water clarity, lighting, and pH, which can indirectly affect fish health and coloration, but they do not directly address pale fish causes or solutions.
   - Domain consistency: High. All products and knowledge content are relevant to ornamental aquarium fish, both freshwater and marine, matching the user's likely aquarium context.
   - Context mismatch: No significant context mismatch. The results are consistent with aquarium fish health and nutrition, which fits the user's concern about pale fish.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.7000
⏱️  [evaluate_confidence] Node execution time: 19.603s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.70 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 8 results
✅ [DEBUG ResponseFormatter] Response generated (3083 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 26.531s
Jeśli Twoje rybki są blade, może to świadczyć o osłabieniu ich kondycji, stresie lub niedoborach witamin. Polecam kilka kroków, które pomogą poprawić ich zdrowie i kolor:

**1. Suplementacja witaminowa – Fish V**
**Fish V** to specjalistyczny suplement wielowitaminowy dla wszystkich ryb akwariowych, zarówno słodkowodnych, jak i morskich. Zawiera witaminy z grupy B, które wspierają witalność, odporność na stres i regulują układ nerwowy. Dodatkowo witamina C przyspiesza gojenie ran, a witaminy K i E wspierają krzepliwość krwi i poprawiają ogólną kondycję.
- Polecamy stosować szczególnie podczas chorób, rekonwalescencji, transportu czy aklimatyzacji.
- Dawkowanie: 1 kropla na kostkę mrożonego pokarmu lub 1 kropla na 100 litrów wody.
- Dostępne opakowania: 10 ml i 50 ml.
- Więcej informacji: [Fish V – Aquaforest](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/fish-v/)

**2. Naturalne wsparcie odporności – Garlic Essence**
**Garlic Essence** to naturalny suplement na bazie ekstraktu z czosnku, kwasów omega-3 i witamin, który wzmacnia odporność ryb, poprawia regenerację i apetyt. Działa także antybakteryjnie i przeciwpasożytniczo.

- Szczególnie polecany podczas kwarantanny, po transporcie oraz w okresach stresu.
- Dawkowanie: dodawać do pokarmu (mrożonego, płatkowego lub granulatu) według potrzeb.
- Dostępne opakowania: 10 ml i 50 ml.
- Więcej informacji: [Garlic Essence – Aquaforest](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/garlic-essence/)

**3. Urozmaicona i wartościowa dieta**
Upewnij się, że ryby otrzymują zróżnicowany pokarm bogaty w składniki odżywcze. Możesz stosować m.in.:
- **AF Vege Strength** – roślinne granulaty z wysoką zawartością błonnika, spiruliną, krillem i witaminami, wspierające zdrowie i intensyfikujące barwy u ryb roślinożernych i wszystkożernych.
- Dawkowanie: kilka małych porcji dziennie, dostosowane do liczby i wielkości ryb.
- Więcej informacji: [AF Vege Strength – Aquaforest](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-vege-strength/)

**Dodatkowo warto zwrócić uwagę na:**
- Jakość i parametry wody – nieprawidłowe wartości pH, twardość czy zanieczyszczenia mogą wpływać na kondycję ryb.
- Oświetlenie akwarium – odpowiednie światło wspiera naturalne zachowanie i kolor ryb.
- Regularne czyszczenie i utrzymanie akwarium w czystości.

---

### Dodatkowe materiały, które mogą Ci pomóc:
- [Krystalicznie czysta woda w akwarium – jak to osiągnąć?](https://aquaforest.eu/pl/baza-wiedzy/krystalicznie-czysta-woda-w-akwarium-jak-to-osiagnac/)
- [Przewodnik po oświetleniu akwarium – odpowiadamy na najczęstsze pytania](https://aquaforest.eu/pl/baza-wiedzy/przewodnik-po-oswietleniu-akwarium-odpowiadamy-na-najczestsze-pytania/)
- [Jak obniżyć pH wody w akwarium?](https://aquaforest.eu/pl/baza-wiedzy/jak-obnizyc-ph-wody-w-akwarium/)

Jeśli problem z bladymi rybkami będzie się utrzymywał lub masz dodatkowe pytania, zachęcam do kontaktu z naszym wsparciem: support@aquaforest.eu lub +48 14 691 79 79. Chętnie pomożemy!

------------------------------------------------------------


🆕 Starting new conversation...
----------------------------------------
You: mam problem z pH, ciągle spada

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'mam problem z pH, ciągle spada'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User reports a problem with pH dropping continuously, likely seeking advice or product-related solution.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User reports a problem with pH dropping continuously, likely seeking advice or product-related solution.
⏱️  [detect_intent_and_language] Node execution time: 4.133s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 6.798s
⏱️  [optimize_product_query] Node execution time: 4.281s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 6.250s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 5 of 6 results
   Best match: AF Minus pH – Professional pH Lowering Conditioner for Amazon Biotopes
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 3 of 6 results
   Best match: KH Plus – Liquid KH Booster for Rapid Carbonate Hardness Correction
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 7 results
💭 [DynamicFilter] Chunk 1: kept 5/6, quality: high. Chunk 2: kept 2/6, quality: high. Total knowledge articles: 4
⏱️  [intelligent_results_filter] Node execution time: 22.602s

📊 [DEBUG ConfidenceScorer] Evaluating 7 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'mam problem z pH, ciągle spada'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.9
   - Category bonus: +0.0
   - Final confidence: 0.9
   - Best matches: ['How to Raise Low pH in Aquarium – Causes, Symptoms & Effective Methods', 'AF Air Scrubber - CO2 Reactor for pH Stabilization in Reef Aquarium', 'KH Buffer – Carbonate Hardness Buffer for Stable Reef Aquarium Parameters', 'The Most Common Mistakes When Setting Up a Marine Aquarium', 'Water Change in a Reef Aquarium – How to Do It Safely?']
   - Category coverage: Not a category query, but problem-solution coverage is strong with multiple relevant products and knowledge articles addressing pH drop and stabilization.
   - Knowledge value: High educational value with detailed explanations of causes, symptoms, and practical methods to raise and stabilize pH, including equipment and chemical supplements.
   - Domain consistency: Good domain match with both freshwater and marine aquarium contexts covered appropriately.
   - Context mismatch: Result 1 (AF Minus pH) is about lowering pH, which is contrary to the user's issue of pH dropping continuously.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.9000
⏱️  [evaluate_confidence] Node execution time: 27.411s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.90 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 7 results
🎯 [DEBUG ResponseFormatter] Mixed domains detected, will present both
✅ [DEBUG ResponseFormatter] Response generated (3211 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 31.217s
Jeśli masz problem z ciągle spadającym pH w akwarium, oto kilka wskazówek i produktów, które mogą pomóc ustabilizować i podnieść pH, a także wyjaśnienie przyczyn takiego stanu.

---

### Dla akwarium słodkowodnego:

**1. Stabilizacja i podniesienie pH:**

- **AF Air Scrubber**
  To reaktor CO2, który pomaga usuwać nadmiar dwutlenku węgla z wody, co często jest przyczyną spadku pH. Dzięki niemu pH może się podnieść i ustabilizować w zakresie 8.0–8.4.
  *Zalety:* stabilizacja pH, redukcja CO2, zapobieganie nagłym wahaniom pH i KH.
  *Dostępny w opakowaniu:* 1 sztuka
  Więcej informacji: [AF Air Scrubber](https://aquaforest.eu/pl/produkty/seawater/wyposazenie-akwarium/af-air-scrubber/)

- **Podnoszenie KH (twardości węglanowej)**
  Niski poziom KH powoduje brak buforowania pH, co skutkuje jego spadkami. Możesz użyć preparatu do podnoszenia KH, np. **KH Buffer** (choć jest dedykowany do akwarium morskiego, zasada stabilizacji KH jest uniwersalna).
  Więcej informacji: [KH Buffer](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-buffer/)

**2. Naturalne metody podnoszenia pH:**

- Zwiększ częstotliwość podmian wody (np. 10% co 1–3 tygodnie).
- Zadbaj o dobrą aerację akwarium, aby usunąć nadmiar CO2 (np. filtry, pompy, napowietrzacze).
- Usuń lub wyparz korzenie/driftwood, które mogą uwalniać kwasy obniżające pH.
- Dodaj do akwarium podłoże wapienne (np. aragonit, kruszony koral), które podnosi twardość i pH.

---

### Dla akwarium morskiego:

- **KH Buffer** – preparat do stabilizacji twardości węglanowej (KH), co jest kluczowe dla utrzymania stabilnego pH i zdrowia koralowców.
  *Dawkowanie:* 100 ml roztworu na 100 l wody podnosi KH o 2,6 dKH.
  *Dostępne rozmiary:* 1200 g, 5000 g
  Więcej informacji: [KH Buffer](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-buffer/)

- **AF Air Scrubber** – reaktor CO2, który stabilizuje pH i zapobiega jego spadkom w akwariach rafowych.
  Więcej informacji: [AF Air Scrubber](https://aquaforest.eu/pl/produkty/seawater/wyposazenie-akwarium/af-air-scrubber/)

---

### Dodatkowe wskazówki:

- Unikaj gwałtownych zmian pH – zmiany większe niż 0,5 na dobę mogą stresować ryby i bezkręgowce.
- Regularnie testuj pH i KH, aby monitorować parametry i reagować na zmiany.
- Jeśli pH spada, sprawdź czy nie masz nadmiaru CO2 w akwarium lub czy nie ma zbyt kwaśnej wody kranowej.
- Używaj preparatów do kondycjonowania wody, np. **AF Water Conditioner**, który neutralizuje szkodliwe substancje, choć nie obniża pH bezpośrednio.

---

### Polecane artykuły do nauki i pogłębienia wiedzy:

- [Jak podnieść zbyt niskie pH w akwarium? – przyczyny, objawy i skuteczne metody](https://aquaforest.eu/pl/baza-wiedzy/jak-podniesc-zbyt-niskie-ph-wody-w-akwarium/)
- [Jak obniżyć pH w akwarium? Przyczyny, metody, różnice (słodkowodne/morskie)](https://aquaforest.eu/pl/baza-wiedzy/jak-obnizyc-ph-wody-w-akwarium/)

---

Jeśli problem będzie się utrzymywał lub masz dodatkowe pytania, zapraszamy do kontaktu z naszym działem wsparcia:
📧 support@aquaforest.eu
📞 +48 14 691 79 79

---

Mam nadzieję, że te wskazówki pomogą Ci ustabilizować pH w akwarium i zapewnić zdrowe warunki dla Twoich ryb i roślin!


 Starting new conversation...
----------------------------------------
You: my corals are turning brown, help!

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'my corals are turning brown, help!'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'en', 'confidence': 0.95, 'context_note': 'User is reporting a problem with corals turning brown and asking for help, indicating a new topic about coral health and potential solutions.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='en', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User is reporting a problem with corals turning brown and asking for help, indicating a new topic about coral health and potential solutions.
⏱️  [detect_intent_and_language] Node execution time: 2.665s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 4.241s
⏱️  [optimize_product_query] Node execution time: 3.796s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 15.398s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 5 of 6 results
   Best match: AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 5 of 6 results
   Best match: Coral Bleaching in Marine Aquariums – Causes & Prevention
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 10 results
💭 [DynamicFilter] Chunk 1: kept 5/6, quality: high. Chunk 2: kept 5/6, quality: high. Total knowledge articles: 2
⏱️  [intelligent_results_filter] Node execution time: 14.520s

📊 [DEBUG ConfidenceScorer] Evaluating 10 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'my corals are turning brown, help!'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.85
   - Category bonus: +0.0
   - Final confidence: 0.85
   - Best matches: ['Coral Bleaching in Marine Aquariums – Causes & Prevention', 'AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition', 'AF NitraPhos Minus – Biological Nitrate, Nitrite & Phosphate Remover for Reef Aquariums', 'AF Vitality – Vitamin Supplement for Coral Coloration & Health', 'AF Power Elixir – Advanced Amino Acid and Vitamin Blend for Coral Growth and Coloration', 'AF Growth Boost – Rapid Growth Supplement for All Corals', 'Aquaforest Probiotic Method – How to Maintain Ultra-Low Nutrients and Healthy Corals with Probiotic Bacteria']
   - Category coverage: Not applicable as the user query is a problem statement, not a category request. However, product categories relevant to coral health and supplementation are well represented.
   - Knowledge value: High. The coral bleaching knowledge article and probiotic method guide provide valuable educational insights into causes, prevention, and holistic care strategies for coral browning and bleaching.
   - Domain consistency: Excellent. All results are from the marine aquarium domain, specifically reef tanks, which is consistent with the user's coral health issue.
   - Context mismatch: No significant context mismatches. All results pertain to marine reef aquariums and coral health, matching the user's implied context.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.8500
⏱️  [evaluate_confidence] Node execution time: 19.476s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.85 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='en'
📊 [DEBUG ResponseFormatter] Processing 10 results
✅ [DEBUG ResponseFormatter] Response generated (5125 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 26.508s
If your corals are turning brown, it often indicates stress or suboptimal conditions affecting their symbiotic algae (zooxanthellae) or coral health. Here are some key steps and products from Aquaforest that can help you improve coral coloration and overall vitality:

### We recommend:

**1. AF Amino Mix**
A complex amino acid supplement that replenishes essential amino acids often lost due to strong skimming or filtration. It supports healthy coral growth, prevents bleaching, and boosts coloration by improving photosynthesis and increasing zooxanthellae density.
- Dosage: 1 drop per 100L every other day after lights out
- Suitable for SPS, LPS, Zoanthus, Ricordea, and mushroom corals
- Available sizes: 10ml, 50ml
- Learn more: [AF Amino Mix](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-amino-mix/)

**2. AF Vitality**
A vitamin supplement rich in B vitamins and other essential vitamins (A, C, D3, E, K3) that supports coral immunity, health, and vibrant coloration. It replenishes vitamins lost during filtration and helps corals resist stress.
- Dosage: 1 drop per 100L every other day after lights out
- Available sizes: 10ml, 50ml
- Learn more: [AF Vitality](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-vitality/)

**3. AF Power Elixir**
An advanced liquid supplement with amino acids and vitamins designed for continuous dosing. It enhances coral growth, tissue building, polyp extension, and coloration by strengthening the symbiotic relationship with zooxanthellae.
- Dosage: 4 ml per 100L daily (start with half dose and observe coral response)
- Available sizes: 200ml, 1000ml, 2000ml
- Learn more: [AF Power Elixir](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-power-elixir/)

**4. AF Power Food**
Highly nutritious powdered coral food providing essential nutrients, vitamins, and minerals to support strong skeletons, growth, and intense coloration. Ideal for SPS, LPS, and non-photosynthetic corals.       
- Dosage: 1 measuring spoon per 100L at least once per week (can increase for dense mature tanks)
- Learn more: [AF Power Food](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-power-food/)

**5. AF Growth Boost**
A coral supplement that promotes rapid growth, polyp extension, and metabolism with amino acids and calcium carbonate to strengthen skeleton formation. Helps corals adapt to stress and fragging.
- Dosage: 1 measuring spoon per 100L after lights out (start with half dose)
- Learn more: [AF Growth Boost](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-growth-boost/)

**6. AF NitraPhos Minus**
If nutrient imbalance (excess nitrates or phosphates) is causing stress and browning, this biological remover helps reduce nitrate, nitrite, and phosphate levels, improving coral health and color by restoring chemical balance.
- Dosage depends on nitrate and phosphate levels; typically 1–3 ml per 100L daily
- Learn more: [AF NitraPhos Minus](https://aquaforest.eu/en/products/seawater/probiotic-method/af-nitraphos-minus/)

**7. Kalium (Potassium Supplement)**
Potassium deficiency can cause browning and faded coloration. Kalium replenishes potassium, essential for coral metabolism and vivid colors, especially reds and pinks.
- Dosage: 10 ml per 100L raises potassium by 10 mg/l (do not exceed 20 ml/100L daily)
- Learn more: [Kalium](https://aquaforest.eu/en/products/lab/microelements/kalium/)

---

### Important Tips to Prevent and Reverse Browning:

- **Check water parameters:** Maintain stable temperature (24–27°C), proper salinity, and balanced nutrients (nitrate, phosphate, potassium).
- **Avoid rapid changes:** Acclimate corals slowly to new tanks or lighting.
- **Ensure proper lighting:** Too intense or inappropriate spectrum can stress corals.
- **Maintain good water quality:** Regular water changes, efficient filtration, and skimming help.
- **Feed corals appropriately:** Use targeted supplements and foods to provide missing nutrients.
- **Monitor for disease or pests:** Stress can make corals vulnerable.

---

### Additional resources:

- **Coral Bleaching in Marine Aquariums – Causes & Prevention**
  Learn about common causes of coral browning and bleaching, how to detect early signs, and best practices to maintain healthy, colorful corals.
  [Read more](https://aquaforest.eu/en/knowledge-base/coral-bleaching-in-marine-aquarium-how-to-safe-the-reef-tank-blog-about-aquariums-resources-aquaforest/)

- **Aquaforest Probiotic Method – Complete Guide**
  A holistic approach to maintaining ultra-low nutrients and vibrant coral health using probiotic bacteria and targeted supplementation.
  [Read more](https://aquaforest.eu/en/knowledge-base/aquaforest-probiotic-method-buyers-guide/)

---

If you need personalized advice or further assistance, feel free to contact Aquaforest support at support@aquaforest.eu or call +48 14 691 79 79.

Taking these steps and using the recommended supplements should help restore your corals’ natural coloration and vitality.

------------------------------------------------------------

🆕 Starting new conversation...
----------------------------------------
You: jak stosować amino mixa?

🤖 Assistant:
🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'jak stosować amino mixa?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks how to use Amino Mix, a specific product, indicating a product usage/dosage question.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User asks how to use Amino Mix, a specific product, indicating a product usage/dosage question.
⏱️  [detect_intent_and_language] Node execution time: 1.980s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [business_reasoner] Node execution time: 5.739s
⏱️  [optimize_product_query] Node execution time: 2.666s
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.546s
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 1 of 6 results
   🎯 Found mentioned products: ['AF Amino Mix']
   Best match: AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 1 of 6 results
   🎯 Found mentioned products: ['AF Amino Mix']
   Best match: Aquaforest Probiotic Method – How to Maintain Ultra-Low Nutrients and Healthy Corals with Probiotic Bacteria
   Quality: medium
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 2 results
💭 [DynamicFilter] Chunk 1: kept 1/6, quality: high. Chunk 2: kept 1/6, quality: medium. Found mentioned products: ['AF Amino Mix']. Total knowledge articles: 2
⏱️  [intelligent_results_filter] Node execution time: 6.421s

📊 [DEBUG ConfidenceScorer] Evaluating 2 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'jak stosować amino mixa?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.95
   - Category bonus: +0.0
   - Final confidence: 0.95
   - Best matches: ['AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition']
   - Category coverage: Excellent coverage for the specific product usage query; detailed instructions and product information provided.
   - Knowledge value: High; detailed explanation of product composition, benefits, dosing, and application timing enhances user understanding.
   - Domain consistency: Perfect match; both results pertain to marine reef aquarium supplementation and coral health.
   - Context mismatch: None; results align well with the user's query about amino mix usage in reef aquariums.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.9500
⏱️  [evaluate_confidence] Node execution time: 7.522s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.95 >= 0.5)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 2 results
✅ [DEBUG ResponseFormatter] Response generated (1497 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 2 results
⏱️  [format_final_response] Node execution time: 13.985s
AF Amino Mix to kompleksowy suplement aminokwasowy przeznaczony do wspierania zdrowego wzrostu i intensywnego wybarwienia koralowców w akwariach morskich. Aminokwasy zawarte w preparacie uzupełniają niedobory powstające często na skutek stosowania silnych odpieniaczy i sterylizacji wody, które mogą prowadzić do blaknięcia i osłabienia koralowców.

**Jak stosować AF Amino Mix?**

- **Dawkowanie:** 1 kropla na 100 litrów wody
- **Częstotliwość:** co drugi dzień
- **Moment podawania:** po zgaszeniu światła dla koralowców SPS i LPS; w ciągu dnia dla koralowców grzybkowatych (mushroom corals)

Regularne stosowanie Amino Mix poprawia fotosyntezę, zwiększa ilość zooxanthellae, co przekłada się na lepsze wybarwienie, szybszy wzrost oraz wzmocnioną odporność koralowców. Preparat jest odpowiedni dla koralowców SPS, LPS, Zoanthus, Ricordea oraz grzybków.

Polecamy stosować AF Amino Mix jako element codziennej suplementacji w akwariach rafowych, szczególnie przy intensywnym odpienianiu i filtracji.

**Więcej informacji i zakup:**
[AF Amino Mix – Aquaforest](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-amino-mix/)

---

Jeśli chcesz dowiedzieć się więcej o kompleksowej metodzie pielęgnacji rafy z wykorzystaniem probiotyków i suplementów Aquaforest, polecamy również zapoznać się z przewodnikiem:

[Aquaforest Probiotic Method – Przewodnik](https://aquaforest.eu/pl/baza-wiedzy/metoda-probiotyczna-aquaforest-przewodnik/)

W razie dodatkowych pytań służymy pomocą!

------------------------------------------------------------

You:
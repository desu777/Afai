ou: moje rybki są blade, co mogę zrobić?

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'moje rybki są blade, co mogę zrobić?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks about pale fish and what can be done, indicating a question about aquarium fish health or treatment.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User asks about pale fish and what can be done, indicating a question about aquarium fish health or treatment.
⏱️  [detect_intent_and_language] Node execution time: 2.506s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'moje rybki są blade, co mogę zrobić?'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 🔧 [BusinessReasoner] Problem: blade, niewyraźne barwy ryb → 1 solutions
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.PRODUCT_QUERY
🔍 🎯 [BusinessReasoner] Domain: freshwater
🔍 🔍 [BusinessReasoner] Search enhancement: suplementy na wybarwienie ryb, intensyfikacja kolo...
🔍 💡 [BusinessReasoner] Interpretation: Użytkownik zauważa, że jego rybki są blade, co może wskazywać na problem z wybarwieniem spowodowany ...
⏱️  [business_reasoner] Node execution time: 10.602s
🔍 🚦 [Router] Routing for intent='Intent.PRODUCT_QUERY'
🔍 ➡️ [Router] Routing to: optimize_query (product query)

📍 Executing node: 'business_reasoner'
----------------------------------------
🔍 🕵️ [QueryOptimizer] Original query: 'moje rybki są blade, co mogę zrobić?'
🔍 ✅ [QueryOptimizer] Optimized queries for Pinecone: ['pale fish color causes and solutions', 'how to improve fish coloration in aquarium', 'AF Color Up benefits for pale fish', 'AF Amino Mix for enhancing fish color and health', 'AF Marine Flakes to improve fish vitality and color', 'treating pale fish with AF Life Essence', 'best Aquaforest products for restoring fish color']
⏱️  [optimize_product_query] Node execution time: 3.065s

📍 Executing node: 'optimize_query'
----------------------------------------
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🔍 🎯 [PineconeSearch] Auto-detected domain filter: freshwater
🔍 🌲 [PineconeSearch] Zwrócono 12 wyników (K=12). Top 5:
🔍    1. 'AF Micro' [Domain: freshwater] (Score: 0.5530)
🔍    2. 'Aquaforest News – Discover Innovative Aquarium Care Products' [Domain: universal] (Score: 0.5518)
🔍    3. 'AF Red Boost' [Domain: freshwater] (Score: 0.5496)
🔍    4. 'Fertilizers for Freshwater Aquariums – Products and Best Practices from Aquaforest' [Domain: freshwater] (Score: 0.5452)
🔍    5. 'AF Macro' [Domain: freshwater] (Score: 0.5429)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 7.835s

📍 Executing node: 'search_pinecone'
----------------------------------------
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 2: keeping 2 of 6 results
   Best match: Fish V – Multivitamin Immunity Booster for All Aquarium Fish
   Quality: medium
✅ [DynamicFilter] Chunk 1: keeping 2 of 6 results
   Best match: Fertilizers for Freshwater Aquariums – What Your Aquarium Plants Need
   Quality: medium
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 4 results
💭 [DynamicFilter] Chunk 1: kept 2/6, quality: medium. Chunk 2: kept 2/6, quality: medium. Total knowledge articles: 3
⏱️  [intelligent_results_filter] Node execution time: 15.313s

📍 Executing node: 'intelligent_filter'
----------------------------------------

📊 [DEBUG ConfidenceScorer] Evaluating 4 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'moje rybki są blade, co mogę zrobić?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.3
   - Category bonus: +0.0
   - Final confidence: 0.3
   - Best matches: ['Fish V – Multivitamin Immunity Booster for All Aquarium Fish']
   - Category coverage: Low - no direct category or product set addressing pale fish coloration or treatment was found.
   - Knowledge value: Limited - only general aquarium care and plant fertilization knowledge; no direct advice on pale fish causes or solutions.
   - Domain consistency: Good - results pertain to freshwater and marine aquarium care, matching the likely domain of the user's fish.      
   - Context mismatch: No major context mismatches; all results relate to aquarium care but do not specifically address pale fish.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.3000
⏱️  [evaluate_confidence] Node execution time: 15.922s
🗺️ [DEBUG] Routing decision: 'escalate_support' (confidence 0.30 < 0.5)

📍 Executing node: 'evaluate_confidence'
----------------------------------------

🚨 [DEBUG Escalate] Escalating to support (confidence < threshold)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 4 results
✅ [DEBUG ResponseFormatter] Response generated (1973 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 4 results
⏱️  [escalate_to_human] Node execution time: 27.343s

📍 Executing node: 'escalate_support'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 82.599 seconds
------------------------------------------------------------

Twoje rybki są blade – może to oznaczać, że mają niedobory witamin lub są osłabione stresem. Aby poprawić ich kondycję, polecam zastosowanie suplementu witaminowego **Fish V** od Aquaforest.

**Fish V** to specjalistyczny, wielowitaminowy preparat dla ryb ozdobnych (zarówno słodkowodnych, jak i morskich). Zawiera witaminy z grupy B, witaminę C, K i E, które wspierają odporność, regenerację, poprawiają apetyt i ogólną witalność ryb. Preparat pomaga zapobiegać utracie łusek i blaknięciu skóry, a także wzmacnia układ nerwowy i odpornościowy.

**Dawkowanie:**
- Dodaj 1 kroplę na kostkę mrożonego pokarmu lub 1 kroplę na 100 litrów wody w akwarium.
- Stosuj codziennie lub w sytuacjach stresowych, chorobowych, podczas transportu lub rekonwalescencji.

**Dostępne pojemności:** 10 ml i 50 ml.

Więcej informacji i zakup:
[Fish V – suplement witaminowy dla ryb](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/fish-v/)

---

Dodatkowo warto zwrócić uwagę na ogólne warunki w akwarium, które mogą wpływać na wygląd ryb:
- Jakość wody (regularne podmiany i filtracja)
- Odpowiednie parametry wody (pH, twardość)
- Zbilansowane karmienie i unikanie przekarmiania
- Stabilne warunki środowiskowe bez nagłych zmian

Jeśli problem bladości ryb utrzymuje się, warto wykonać testy jakości wody i skonsultować się z naszym zespołem wsparcia: support@aquaforest.eu lub +48 14 691 79 79.

---

**Dodatkowe materiały, które mogą pomóc:**
- [Krystalicznie czysta woda w akwarium – jak to osiągnąć](https://aquaforest.eu/pl/baza-wiedzy/krystalicznie-czysta-woda-w-akwarium-jak-to-osiagnac/) – czysta woda to podstawa zdrowia ryb.
- [Nawozy do akwariów słodkowodnych – produkty i porady](https://aquaforest.eu/pl/baza-wiedzy/nawozy-do-akwariow-slodkowodnych-produkty-i-porady-od-aquaforest-dla-twoich-roslin/) – zdrowe rośliny wspierają dobre samopoczucie ryb.

Jeśli masz dodatkowe pytania lub potrzebujesz indywidualnej porady, chętnie pomożemy!

------------------------------------------------------------


🆕 Starting new conversation...
----------------------------------------
You: mam problem z pH, ciągle spada

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'mam problem z pH, ciągle spada'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User reports a problem with pH dropping continuously, likely seeking advice or product-related solution.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User reports a problem with pH dropping continuously, likely seeking advice or product-related solution.
⏱️  [detect_intent_and_language] Node execution time: 7.193s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'mam problem z pH, ciągle spada'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 🔧 [BusinessReasoner] Problem: pH dropping → 4 solutions
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.PRODUCT_QUERY
🔍 🔍 [BusinessReasoner] Search enhancement: pH stabilizers, KH buffer, alkalinity supplements ...
🔍 💡 [BusinessReasoner] Interpretation: User has a problem with pH continuously dropping in their aquarium and is seeking advice or products...
⏱️  [business_reasoner] Node execution time: 10.480s
🔍 🚦 [Router] Routing for intent='Intent.PRODUCT_QUERY'
🔍 ➡️ [Router] Routing to: optimize_query (product query)

📍 Executing node: 'business_reasoner'
----------------------------------------
🔍 🕵️ [QueryOptimizer] Original query: 'mam problem z pH, ciągle spada'
🔍 ✅ [QueryOptimizer] Optimized queries for Pinecone: ['AF Minus pH product for lowering aquarium pH', 'how to stabilize dropping pH in aquarium with AF Minus pH', 'solutions for continuously falling aquarium pH', 'AF Minus pH usage instructions and benefits', 'best products to control and maintain aquarium pH levels', 'aquarium pH keeps dropping how to fix with Aquaforest products', 'AF Minus pH vs other pH control methods for aquariums']
⏱️  [optimize_product_query] Node execution time: 3.478s

📍 Executing node: 'optimize_query'
----------------------------------------
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🔍 🔍 [PineconeSearch] Freshwater score: 0, Marine score: 0
🔍 🌲 [PineconeSearch] Zwrócono 12 wyników (K=12). Top 5:
🔍    1. 'AF Minus pH' [Domain: freshwater] (Score: 0.6946)
🔍    2. 'How to Raise Low pH in Aquarium – Causes, Symptoms & Effective Methods' [Domain: universal] (Score: 0.6850)
🔍    3. 'Lowering pH in Aquarium – Causes, Methods, Differences (FW/SW)' [Domain: universal] (Score: 0.6723)
🔍    4. 'AF Air Scrubber' [Domain: seawater] (Score: 0.6509)
🔍    5. 'KH Plus' [Domain: seawater] (Score: 0.6063)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.037s

📍 Executing node: 'search_pinecone'
----------------------------------------
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 2: keeping 3 of 6 results
   Best match: KH Plus – Liquid KH Booster for Rapid Carbonate Hardness Correction
   Quality: high
✅ [DynamicFilter] Chunk 1: keeping 3 of 6 results
   🎯 Found mentioned products: ['AF Minus pH']
   Best match: AF Minus pH – Professional pH Lowering Conditioner for Amazon Biotopes
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 6 results
💭 [DynamicFilter] Chunk 1: kept 3/6, quality: high. Chunk 2: kept 3/6, quality: high. Found mentioned products: ['AF Minus pH']. Total knowledge articles: 2
⏱️  [intelligent_results_filter] Node execution time: 8.299s

📍 Executing node: 'intelligent_filter'
----------------------------------------

📊 [DEBUG ConfidenceScorer] Evaluating 6 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'mam problem z pH, ciągle spada'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.9
   - Category bonus: +0.0
   - Final confidence: 0.9
   - Best matches: ['AF Minus pH – Professional pH Lowering Conditioner for Amazon Biotopes', 'How to Raise Low pH in Aquarium – Causes, Symptoms & Effective Methods', 'How to Lower pH in Aquarium & What Causes High pH in Fish Tank?']
   - Category coverage: Excellent coverage of pH management products and knowledge for freshwater aquariums; includes a professional pH lowering product and detailed educational articles on causes and solutions for pH fluctuations.
   - Knowledge value: High educational value from Results 2 and 3, providing causes, symptoms, and practical methods to stabilize pH, which complements the product solution in Result 1.
   - Domain consistency: Good domain match for freshwater aquarium pH issues in Results 1-3; marine domain products and tests in Results 4-6 are less relevant but not contradictory.
   - Context mismatch: Results 4, 5, and 6 focus on marine aquarium alkalinity and KH testing, which is less relevant to the user's likely freshwater pH dropping problem but do not conflict with the main context.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.9000
⏱️  [evaluate_confidence] Node execution time: 21.350s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.90 >= 0.5)

📍 Executing node: 'evaluate_confidence'
----------------------------------------

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 6 results
🎯 [DEBUG ResponseFormatter] Mixed domains detected, will present both
✅ [DEBUG ResponseFormatter] Response generated (3269 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 28.439s

📍 Executing node: 'format_response'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 83.285 seconds
------------------------------------------------------------

Jeśli masz problem z ciągle spadającym pH w akwarium, warto zwrócić uwagę na kilka aspektów i zastosować odpowiednie metody stabilizacji pH.

---

### Dla akwarium słodkowodnego:

**Przyczyny spadku pH mogą być następujące:**
- Zbyt rzadkie podmiany wody,
- Obecność drewna lub liści (tzw. taniny) barwiących wodę i obniżających pH,
- Nagromadzenie CO2 z powodu słabej aeracji,
- Zbyt miękka woda o niskiej twardości węglanowej (KH).

---

### Polecamy następujące działania i produkty:

**1. Stabilizacja i podniesienie KH (twardości węglanowej):**
KH jest naturalnym buforem pH, który zapobiega jego gwałtownym spadkom. Jeśli KH jest zbyt niskie, pH będzie niestabilne i spada.
- **KH Plus** – skoncentrowany preparat do szybkiego podniesienia KH w akwariach morskich (można stosować także w słodkowodnych z odpowiednią ostrożnością).
  Dawkowanie: 10 ml na 100 l podnosi KH o 0,25 dKH.
  Więcej informacji: [KH Plus](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-plus/)

- **KH Pro** – ultra skoncentrowany preparat do szybkiej korekty KH i stabilizacji pH, zawiera również potas.
  Dawkowanie: 5 ml na 100 l podnosi KH o 0,5 dKH.
  Więcej informacji: [KH Pro](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-pro/)

**2. Zwiększenie napowietrzania:**
Poprawa cyrkulacji i napowietrzania usuwa nadmiar CO2, który obniża pH. Możesz użyć dodatkowych pomp powietrza lub filtrów z napowietrzaniem.

**3. Usunięcie lub obróbka drewna i liści:**
Jeśli masz w akwarium drewno lub liście, które uwalniają taniny, możesz je wyjąc lub wcześniej zagotować, aby zmniejszyć ich wpływ na pH.   

**4. Regularne podmiany wody:**
Częstsze podmiany (np. 10% co 1–2 tygodnie) pomagają utrzymać stabilne parametry.

---

### Produkt do obniżania pH (jeśli pH jest zbyt wysokie, a chcesz je kontrolować):

- **AF Minus pH** – profesjonalny preparat do bezpiecznego obniżania pH, szczególnie dla ryb z biotopów amazońskich i innych wymagających lekko kwaśnej wody.
  Dawkowanie: 1 ml na 1 litr wody obniża pH o 0,2 jednostki.
  Stosować ostrożnie, nie obniżać pH o więcej niż 0,5 dziennie.
  Więcej informacji: [AF Minus pH](https://aquaforest.eu/pl/produkty/freshwater/utrzymanie-parametrow-wody/af-minus-ph/)

---

### Dodatkowe zasoby i wiedza:

- [Jak podnieść zbyt niskie pH w akwarium?](https://aquaforest.eu/pl/baza-wiedzy/jak-podniesc-zbyt-niskie-ph-wody-w-akwarium/) – artykuł wyjaśniający przyczyny niskiego pH i metody jego podnoszenia.
- [Jak obniżyć pH w akwarium?](https://aquaforest.eu/pl/baza-wiedzy/jak-obnizyc-ph-wody-w-akwarium/) – porady dotyczące bezpiecznego obniżania pH.

---

### Podsumowanie:

1. Zmierz KH i jeśli jest niskie, podnieś je preparatem KH Plus lub KH Pro, aby ustabilizować pH.
2. Zwiększ napowietrzanie, aby usunąć nadmiar CO2.
3. Regularnie wykonuj podmiany wody i ogranicz źródła tanin.
4. Jeśli pH jest zbyt wysokie i chcesz je obniżyć, stosuj AF Minus pH z zachowaniem ostrożności.

Jeśli problem będzie się utrzymywał lub potrzebujesz indywidualnej pomocy, możesz skontaktować się z nami pod adresem: support@aquaforest.eu lub telefonicznie +48 14 691 79 79.

---

Mam nadzieję, że te wskazówki pomogą Ci ustabilizować pH w Twoim akwarium! Jeśli masz dodatkowe pytania, chętnie pomogę.

------------------------------------------------------------
ou: new

🆕 Starting new conversation...
----------------------------------------
You: my corals are turning brown, help!

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'my corals are turning brown, help!'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'en', 'confidence': 0.95, 'context_note': 'User is reporting a coral health issue (turning brown) and asking for help, indicating a request for advice or product-related solution.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='en', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User is reporting a coral health issue (turning brown) and asking for help, indicating a request for advice or product-related solution.
⏱️  [detect_intent_and_language] Node execution time: 2.229s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.001s
⏱️  [load_product_names] Node execution time: 0.001s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'my corals are turning brown, help!'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 🔧 [BusinessReasoner] Problem: corals turning brown → 5 solutions
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.PRODUCT_QUERY
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 🔍 [BusinessReasoner] Search enhancement: coral coloration improvement, coral amino acids, c...
🔍 💡 [BusinessReasoner] Interpretation: User's corals turning brown likely indicates coral stress or nutrient deficiency affecting coloratio...
⏱️  [business_reasoner] Node execution time: 4.715s
🔍 🚦 [Router] Routing for intent='Intent.PRODUCT_QUERY'
🔍 ➡️ [Router] Routing to: optimize_query (product query)

📍 Executing node: 'business_reasoner'
----------------------------------------
🔍 🕵️ [QueryOptimizer] Original query: 'my corals are turning brown, help!'
🔍 ✅ [QueryOptimizer] Optimized queries for Pinecone: ['corals turning brown causes and solutions', 'how to fix brown corals in reef aquarium', 'AF Color Up coral pigmentation enhancer', 'AF Amino Mix coral health booster', 'AF Growth Boost for coral color and vitality', 'AF Protect Dip coral stress relief treatment', 'best Aquaforest products for coral browning', 'improving coral color with Aquaforest supplements']
⏱️  [optimize_product_query] Node execution time: 3.142s

📍 Executing node: 'optimize_query'
----------------------------------------
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🔍 🎯 [PineconeSearch] Auto-detected domain filter: seawater
🔍 🌲 [PineconeSearch] Zwrócono 12 wyników (K=12). Top 5:
🔍    1. 'AF Energy' [Domain: seawater] (Score: 0.7509)
🔍    2. 'AF Power Elixir' [Domain: seawater] (Score: 0.7475)
🔍    3. 'AF Amino Mix' [Domain: seawater] (Score: 0.7247)
🔍    4. 'AF Growth Boost' [Domain: seawater] (Score: 0.7101)
🔍    5. 'Component C' [Domain: seawater] (Score: 0.7025)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 5.697s

📍 Executing node: 'search_pinecone'
----------------------------------------
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
   Best match: AF Vitality – Vitamin Supplement for Coral Coloration & Health
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 10 results
💭 [DynamicFilter] Chunk 1: kept 5/6, quality: high. Chunk 2: kept 5/6, quality: high. Total knowledge articles: 0
⏱️  [intelligent_results_filter] Node execution time: 11.201s

📍 Executing node: 'intelligent_filter'
----------------------------------------

📊 [DEBUG ConfidenceScorer] Evaluating 10 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'my corals are turning brown, help!'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.8
   - Category bonus: +0.0
   - Final confidence: 0.8
   - Best matches: ['AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition', 'AF Power Elixir – Advanced Amino Acid and Vitamin Blend for Coral Growth and Coloration', 'AF Energy – High-Nutrition Concentrate for SPS Corals', 'AF Growth Boost – Rapid Growth Supplement for All Corals', 'AF Vitality – Vitamin Supplement for Coral Coloration & Health', 'Polyp Up – Polyp Extension and Color Enhancer for Corals', 'Iron – Concentrated Iron Supplement for Marine Aquarium Color and Health', 'Kalium – Highly Concentrated Potassium Supplement for Marine Aquariums', 'AF Protect Dip – Preventive Coral Bath for Protection Against Parasites and Infections']
   - Category coverage: The query is not a direct category request but a problem statement. The results cover a broad range of coral supplements and treatments relevant to coral browning, effectively covering the product category related to coral health and coloration enhancement.
   - Knowledge value: Moderate. The results provide detailed product descriptions, dosing, and intended effects on coral health and coloration, which can help users understand how to improve coral browning. However, there is no explicit educational content on causes of browning or environmental troubleshooting.
   - Domain consistency: High. All results are from the marine aquarium domain, specifically reef aquariums, matching the user's coral-related query.
   - Context mismatch: No significant context mismatches found. All products and information are relevant to marine reef aquariums and coral care.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.8000
⏱️  [evaluate_confidence] Node execution time: 16.102s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.80 >= 0.5)

📍 Executing node: 'evaluate_confidence'
----------------------------------------

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='en'
📊 [DEBUG ResponseFormatter] Processing 10 results
✅ [DEBUG ResponseFormatter] Response generated (3766 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 32.001s

📍 Executing node: 'format_response'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 75.100 seconds
------------------------------------------------------------

If your corals are turning brown, it often indicates stress, poor nutrition, or an imbalance in their symbiotic algae (zooxanthellae). To help restore healthy coloration and vitality, I recommend supporting your corals with targeted nutritional supplements and proper care. Here are some Aquaforest products designed to improve coral health, coloration, and growth:

---

### We recommend:

**1. AF Energy – High-Nutrition Concentrate for SPS Corals**
A unique blend of natural extracts, Omega-3 and Omega-6 fatty acids, vitamins, and amino acids. It enhances vibrant, pastel coral coloration by limiting excessive zooxanthellae growth and promotes proper development.
- Dosage: 1 drop per 100L every other day after lights out
- Sizes: 10ml, 50ml
- [Learn more](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-energy/)

**2. AF Amino Mix – Complex Amino Acid Supplement for Coral Nutrition**
Contains essential amino acids that improve photosynthesis and boost coral coloration by increasing zooxanthellae pigment production. Helps prevent bleaching and supports faster growth.
- Dosage: 1 drop per 100L every other day after lights out
- Sizes: 10ml, 50ml
- [Learn more](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-amino-mix/)

**3. AF Power Elixir – Advanced Amino Acid and Vitamin Blend for Coral Growth and Coloration**
Supports optimal coral growth, vivid coloration, polyp extension, and strengthens coral immunity. Perfect for continuous dosing.
- Dosage: 4 ml per 100L daily
- Sizes: 200ml, 1000ml, 2000ml
- [Learn more](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-power-elixir/)

**4. AF Vitality – Vitamin Supplement for Coral Coloration & Health**
A concentrated vitamin formula (B vitamins, vitamins A, C, D3, E, K3) that replenishes nutrients lost during filtration and supports coral immunity and color intensity.
- Dosage: 1 drop per 100L every other day after lights out
- Sizes: 10ml, 50ml
- [Learn more](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/af-vitality/)

**5. Polyp Up – Polyp Extension and Color Enhancer for Corals**
Enhances polyp extension and coloration, especially yellow and orange tones. Contains Omega fatty acids, amino acids, vitamins, and microelements to boost coral feeding response and tissue growth.
- Dosage: 1 drop per 100L daily with lights on
- Size: 50ml
- [Learn more](https://aquaforest.eu/en/products/seawater/foods-and-supplementation/polyp-up/)

---

### Additional tips to help your corals recover from browning:

- **Check water parameters:** Ensure stable temperature, salinity, calcium, alkalinity, magnesium, and trace elements. Imbalances can stress corals and cause browning.
- **Avoid overexposure to strong light:** Sudden changes or excessive lighting can cause coral bleaching or browning. Gradually acclimate corals to light intensity.
- **Feed corals regularly:** Use products like **AF Power Food** or **AF Growth Boost** to provide essential nutrients and support skeleton formation and metabolism.
- **Maintain good water quality:** Use proper filtration and avoid excessive nutrient levels that can promote unwanted algae growth and stress corals.

---

If you want to start with a simple regimen, consider dosing **AF Energy** and **AF Amino Mix** every other day after lights out, combined with regular feeding using **AF Power Food** once or twice a week. Monitor your corals’ response and adjust accordingly.

If you need more personalized advice or suspect disease or parasites, feel free to contact our support team at support@aquaforest.eu or +48 14 691 79 79.

---

I hope this helps your corals regain their beautiful colors and health!





----------------------------------------
You: jak stosować amino mixa?

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'jak stosować amino mixa?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks how to use Amino Mix, a specific product, indicating a product usage/dosage question.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User asks how to use Amino Mix, a specific product, indicating a product usage/dosage question.     
⏱️  [detect_intent_and_language] Node execution time: 1.987s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'jak stosować amino mixa?'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 ✅ [BusinessReasoner] Product validated: AF Amino Mix
🔍 🔧 [BusinessReasoner] Problem: coral bleaching, pale coral coloration, amino acid deficiency → 5 solutions
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.PRODUCT_QUERY
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 🔍 [BusinessReasoner] Search enhancement: AF Amino Mix dosing instructions, how to use AF Am...
🔍 💡 [BusinessReasoner] Interpretation: User wants to know how to use the amino acid supplement AF Amino Mix for corals in marine aquariums....
⏱️  [business_reasoner] Node execution time: 5.072s
🔍 🚦 [Router] Routing for intent='Intent.PRODUCT_QUERY'
🔍 ➡️ [Router] Routing to: optimize_query (product query)

📍 Executing node: 'business_reasoner'
----------------------------------------
🔍 🕵️ [QueryOptimizer] Original query: 'jak stosować amino mixa?'
🔍 ✅ [QueryOptimizer] Optimized queries for Pinecone: ['how to use AF Amino Mix in reef aquariums', 'AF Amino Mix dosing instructions', 'best practices for AF Amino Mix application', 'AF Amino Mix coral growth benefits and usage', 'step-by-step guide to applying AF Amino Mix', 'AF Amino Mix aquarium supplement directions', 'tips for effective use of AF Amino Mix in marine tanks']
⏱️  [optimize_product_query] Node execution time: 3.080s

📍 Executing node: 'optimize_query'
----------------------------------------
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🔍 🎯 [PineconeSearch] Auto-detected domain filter: seawater
🔍 🌲 [PineconeSearch] Zwrócono 12 wyników (K=12). Top 5:
🔍    1. 'AF Amino Mix' [Domain: seawater] (Score: 0.6971)
🔍    2. 'AF Growth Boost' [Domain: seawater] (Score: 0.6848)
🔍    3. 'AF Power Elixir' [Domain: seawater] (Score: 0.6756)
🔍    4. 'AF Energy' [Domain: seawater] (Score: 0.6545)
🔍    5. 'AF Build' [Domain: seawater] (Score: 0.6192)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.314s

📍 Executing node: 'search_pinecone'
----------------------------------------
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 2: keeping 1 of 6 results
   🎯 Found mentioned products: ['AF Amino Mix']
   Best match: Aquaforest Probiotic Method – How to Maintain Ultra-Low Nutrients and Healthy Corals with Probiotic Bacteria
   Quality: medium
✅ [DynamicFilter] Chunk 1: keeping 1 of 6 results
   🎯 Found mentioned products: ['AF Amino Mix']
   Best match: AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 2 results
💭 [DynamicFilter] Chunk 1: kept 1/6, quality: high. Chunk 2: kept 1/6, quality: medium. Found mentioned products: ['AF Amino Mix']. Total knowledge articles: 1
⏱️  [intelligent_results_filter] Node execution time: 11.556s

📍 Executing node: 'intelligent_filter'
----------------------------------------

📊 [DEBUG ConfidenceScorer] Evaluating 2 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'jak stosować amino mixa?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.9
   - Category bonus: +0.0
   - Final confidence: 0.9
   - Best matches: ['AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition', 'Aquaforest Probiotic Method – How to Maintain Ultra-Low Nutrients and Healthy Corals with Probiotic Bacteria']
   - Category coverage: Excellent - the specific product AF Amino Mix is fully covered with detailed usage instructions.
   - Knowledge value: High - Result 1 provides direct dosing and usage instructions; Result 2 offers valuable broader reef-keeping context involving AF Amino Mix.
   - Domain consistency: High - both results pertain to seawater reef aquarium supplementation and coral health.
   - Context mismatch: None - both results are relevant to reef aquarium amino acid supplementation.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.9000
⏱️  [evaluate_confidence] Node execution time: 8.651s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.90 >= 0.5)

📍 Executing node: 'evaluate_confidence'
----------------------------------------

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 2 results
✅ [DEBUG ResponseFormatter] Response generated (1204 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 2 results
⏱️  [format_final_response] Node execution time: 7.617s

📍 Executing node: 'format_response'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 42.286 seconds
------------------------------------------------------------

AF Amino Mix to kompleksowy suplement aminokwasowy, który wspomaga zdrowy wzrost i intensywne wybarwienie korali w akwariach morskich. Aminokwasy są niezbędne dla korali, a ich niedobory mogą pojawić się np. przy silnym skimmerze, prowadząc do blaknięcia i osłabienia korali.     

**Jak stosować AF Amino Mix?**

- **Dawkowanie:** 1 kropla na każde 100 litrów wody w akwarium.
- **Częstotliwość:** co drugi dzień.
- **Czas podawania:** najlepiej po zgaszeniu światła dla korali SPS i LPS, natomiast dla grzybków (mushroom corals) w ciągu dnia.

Regularne stosowanie Amino Mixa:
- zapobiega blaknięciu korali,
- wzmacnia ich kolory,
- poprawia jakość fotosyntezy,
- przyspiesza wzrost i regenerację tkanek,
- zwiększa odporność korali.

Produkt jest odpowiedni dla korali SPS, LPS, Zoanthus, Ricordea oraz grzybków.

Polecamy stosować go jako element codziennej suplementacji w akwariach morskich, szczególnie tam, gdzie używany jest silny skimmer lub gdy obserwujesz blaknięcie korali.

Więcej informacji i zakup:
[AF Amino Mix - Aquaforest](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-amino-mix/)

Jeśli potrzebujesz dodatkowych wskazówek lub pomocy, chętnie służymy wsparciem!

------------------------------------------------------------


🆕 Starting new conversation...
----------------------------------------
You: moje testy pokazują Ca 350, KH 7, Mg 1200 - co dozować najpierw?

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'moje testy pokazują Ca 350, KH 7, Mg 1200 - co dozować najpierw?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'follow_up', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User provides water test results and asks which element to dose first, continuing a discussion about aquarium water parameters.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.FOLLOW_UP', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User provides water test results and asks which element to dose first, continuing a discussion about aquarium water parameters.
⏱️  [detect_intent_and_language] Node execution time: 2.343s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'moje testy pokazują Ca 350, KH 7, Mg 1200 - co dozować najpierw?'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 🔧 [BusinessReasoner] Problem: imbalanced calcium, magnesium, and KH levels → 3 solutions
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 🔍 [BusinessReasoner] Search enhancement: calcium dosing priority with Ca 350, KH 7, Mg 1200...
🔍 💡 [BusinessReasoner] Interpretation: User's test results show calcium (Ca) at 350 mg/L, carbonate hardness (KH) at 7 dKH, and magnesium (...
⏱️  [business_reasoner] Node execution time: 7.738s
🔍 🚦 [Router] Routing for intent='Intent.FOLLOW_UP'
🔍 ➡️ [Router] Routing to: follow_up_router (follow-up question)

📍 Executing node: 'business_reasoner'
----------------------------------------
🔍 🔄 [Follow-up Router] Checking if can handle follow-up with cache
⏱️  [follow_up_router] Node execution time: 0.000s
⏱️  [follow_up_router] Node execution time: 0.000s
🔍 ❌ [Follow-up Router] No cache, routing to optimize_query

📍 Executing node: 'follow_up_router'
----------------------------------------
🔍 🕵️ [QueryOptimizer] Original query: 'moje testy pokazują Ca 350, KH 7, Mg 1200 - co dozować najpierw?'
🔍 ✅ [QueryOptimizer] Optimized queries for Pinecone: ['how to dose calcium magnesium and alkalinity in reef aquarium', 'best order to dose Ca Mg KH in marine tank', 'AF Ca Plus dosing for calcium 350 mg/l', 'AF Mg Plus for high magnesium 1200 mg/l adjustment', 'adjusting KH 7 with AF KH Plus or KH Buffer', 'reef tank water parameter correction calcium magnesium alkalinity', 'calcium magnesium alkalinity dosing priority in saltwater aquarium']
⏱️  [optimize_product_query] Node execution time: 3.839s

📍 Executing node: 'optimize_query'
----------------------------------------
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🔍 🎯 [PineconeSearch] Auto-detected domain filter: seawater
🔍 🌲 [PineconeSearch] Zwrócono 12 wyników (K=12). Top 5:
🔍    1. 'KH Plus' [Domain: seawater] (Score: 0.6707)
🔍    2. 'Ca Plus' [Domain: seawater] (Score: 0.6687)
🔍    3. 'Components Pro' [Domain: seawater] (Score: 0.6655)
🔍    4. 'KH Buffer' [Domain: seawater] (Score: 0.6611)
🔍    5. 'Ca plus' [Domain: seawater] (Score: 0.6514)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.187s

📍 Executing node: 'search_pinecone'
----------------------------------------
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 2: keeping 3 of 6 results
   🎯 Found mentioned products: ['KH Plus', 'Calcium']
   Best match: Balling Method in Reef Aquarium
   Quality: high
✅ [DynamicFilter] Chunk 1: keeping 4 of 6 results
   Best match: Ca plus – Highly Concentrated Calcium Supplement for Marine Aquariums
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 7 results
💭 [DynamicFilter] Chunk 1: kept 4/6, quality: high. Chunk 2: kept 3/6, quality: high. Found mentioned products: ['KH Plus', 'Calcium']. Total knowledge articles: 2
⏱️  [intelligent_results_filter] Node execution time: 18.113s

📍 Executing node: 'intelligent_filter'
----------------------------------------

📊 [DEBUG ConfidenceScorer] Evaluating 7 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'moje testy pokazują Ca 350, KH 7, Mg 1200 - co dozować najpierw?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.9
   - Category bonus: +0.0
   - Final confidence: 0.9
   - Best matches: ['Mg Plus – Highly Concentrated Liquid Magnesium Supplement for Reef Aquariums', 'Ca Plus – Highly Concentrated Calcium Supplement for Marine Aquariums', 'KH Plus – Highly Concentrated Solution for Raising Alkalinity (KH) in Marine Aquariums', 'Balling Method in Reef Aquarium']
   - Category coverage: Excellent coverage of all three key macroelements (Ca, Mg, KH) with multiple product options and dosing instructions.
   - Knowledge value: High educational value, especially the Balling Method article explaining dosing strategy and parameter interdependence.
   - Domain consistency: All results are consistent with marine reef aquarium domain, matching the user's implied reef tank context.        
   - Context mismatch: No significant context mismatches; all results pertain to marine reef aquarium water parameter dosing.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.9000
⏱️  [evaluate_confidence] Node execution time: 14.618s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.90 >= 0.5)

📍 Executing node: 'evaluate_confidence'
----------------------------------------

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.FOLLOW_UP', language='pl'
📊 [DEBUG ResponseFormatter] Processing 7 results
✅ [DEBUG ResponseFormatter] Response generated (3004 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 32.583s

📍 Executing node: 'format_response'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 83.431 seconds
------------------------------------------------------------

Twoje wyniki testów pokazują:
- Ca (wapń) 350 mg/l (ppm) – lekko poniżej optymalnego zakresu dla akwarium morskiego (380–460 mg/l),
- KH (twardość węglanowa) 7 dKH – w normie (zalecane 6,5–8,5 dKH),
- Mg (magnez) 1200 mg/l – lekko poniżej dolnej granicy zalecanego zakresu (1180–1460 mg/l).

**Co dozować najpierw?**

1. **Magnez (Mg)** – ponieważ magnez jest kluczowy dla stabilizacji parametrów wapnia i KH, a jego niedobór może powodować trudności w utrzymaniu właściwych poziomów Ca i KH, zalecamy rozpocząć od uzupełnienia magnezu.
   Polecamy produkt:
   **Mg Plus** – skoncentrowany, gotowy do użycia suplement magnezu dla akwarium morskiego.
   - Dawkowanie: 10 ml na 100 l podnosi Mg o 7,5 mg/l.
   - Nie przekraczać 50 mg/l wzrostu magnezu na dobę.
   - Dostępne pojemności: 250 ml, 1000 ml, 2000 ml.
   Więcej informacji: [Mg Plus](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/mg-plus/)

2. **Wapń (Ca)** – po ustabilizowaniu magnezu możesz zacząć uzupełniać wapń.
   Polecamy:
   **Ca Plus** – skoncentrowany, łatwo przyswajalny suplement wapnia.
   - Dawkowanie: 10 ml na 100 l podnosi Ca o 15 mg/l.
   - Maksymalna dawka dzienna: 20 ml/100 l.
   - Dostępne pojemności: 250 ml, 2000 ml.
   Więcej informacji: [Ca Plus](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/ca-plus/)

3. **KH (twardość węglanowa)** – jeśli po uzupełnieniu magnezu i wapnia okaże się, że KH wymaga korekty, możesz zastosować:
   - **KH Plus** – płynny koncentrat do szybkiego podnoszenia KH.
     Dawkowanie: 10 ml na 100 l podnosi KH o 0,25–0,5 dKH (w zależności od produktu).
     Nie dawkuj KH i Ca jednocześnie – zachowaj przerwę 5–10 minut.
     Dostępne pojemności: 250 ml, 2000 ml.
     Więcej informacji: [KH Plus](https://aquaforest.eu/pl/produkty/lab/makroelementy/kh-plus_/)

   - lub **KH Buffer** – granulat do przygotowania roztworu stabilizującego KH.
     Dawkowanie zależne od przygotowanego roztworu i testów.
     Dostępne opakowania: 1200 g, 5000 g.
     Więcej informacji: [KH Buffer](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-buffer/)

---

**Podsumowanie:**
Najpierw uzupełnij magnez (Mg Plus), ponieważ jest on niezbędny do prawidłowego wchłaniania wapnia i stabilizacji KH. Następnie, gdy poziom magnezu będzie w normie, możesz dozować wapń (Ca Plus). Dopiero na końcu, jeśli to konieczne, popraw twardość węglanową (KH Plus lub KH Buffer), pamiętając o zachowaniu odstępu czasowego między dawkami wapnia i KH, by uniknąć wytrącania się osadów.

---

**Dodatkowe materiały:**
Jeśli chcesz poznać szczegóły dotyczące kompleksowego utrzymania parametrów w akwarium morskim, polecamy artykuł o metodzie Ballinga:       
[Metoda Ballinga w akwarium morskim](https://aquaforest.eu/pl/baza-wiedzy/metoda-ballinga-w-akwarium-morskim-blog-o-akwarystyce-zasoby-aquaforest/)

W razie pytań lub wątpliwości zapraszamy do kontaktu:
support@aquaforest.eu
+48 14 691 79 79

Życzymy powodzenia i zdrowego akwarium!

------------------------------------------------------------


You: dziękuję! a wyjaśnisz mi czym jest motada balling?

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'dziękuję! a wyjaśnisz mi czym jest motada balling?'
💬 [DEBUG IntentDetector] Historia konwersacji: 2 wiadomości
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'follow_up', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks for an explanation of the Balling method, continuing the previous discussion about dosing Components Pro with Balling.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.FOLLOW_UP', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User asks for an explanation of the Balling method, continuing the previous discussion about dosing Components Pro with Balling.
⏱️  [detect_intent_and_language] Node execution time: 2.751s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'dziękuję! a wyjaśnisz mi czym jest motada balling?'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 📦 [BusinessReasoner] Category 'metoda_balling' with 3 products
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.FOLLOW_UP
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 🔍 [BusinessReasoner] Search enhancement: metoda Balling suplementacja wapnia magnezu alkali...
🔍 💡 [BusinessReasoner] Interpretation: Użytkownik pyta o wyjaśnienie, czym jest metoda Balling, czyli sposób suplementacji składników miner...
⏱️  [business_reasoner] Node execution time: 6.114s
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
📦 [DEBUG Follow-up] Cache contains 4 items
✅ [DEBUG Follow-up Handler] Response generated using cache
⏱️  [handle_follow_up] Node execution time: 18.825s

📍 Executing node: 'handle_follow_up'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 27.707 seconds
------------------------------------------------------------

Metoda Balling to popularna technika utrzymania stabilnych parametrów wody w akwariach morskich, szczególnie tych z rafą koralową. Została opracowana w latach 90. przez niemieckiego akwarystę Hansa-Wernera Ballinga. Polega na codziennym, regularnym i precyzyjnym dozowaniu trzech oddzielnych roztworów, które uzupełniają podstawowe składniki potrzebne koralom do wzrostu i zdrowia:

- **Wapń (Ca)** – niezbędny do budowy szkieletów koralowych,
- **Węglanowa twardość (KH)** – stabilizuje pH i dostarcza węglanów do kalcyfikacji,
- **Magnez (Mg)** – pomaga utrzymać równowagę wapnia i KH oraz wspiera procesy metaboliczne koralowców.

Dawkowanie odbywa się w małych porcjach, rozłożonych na cały dzień (najlepiej za pomocą pomp dozujących), co zapobiega gwałtownym wahaniom parametrów i sprzyja stabilności chemii wody. Metoda Balling pozwala na precyzyjne kontrolowanie i uzupełnianie pierwiastków zużywanych przez koralowce i inne organizmy w akwarium.

Aquaforest oferuje gotowe zestawy do metody Balling, takie jak **Components Pro** – wysoko skoncentrowane roztwory mikro- i makroelementów, które ułatwiają precyzyjne i wygodne dawkowanie. Są też inne warianty, np. Components 1+2+3, Component 3 in 1 czy Components Strong (mikroelementy do uzupełniania).

Więcej szczegółów i praktyczne wskazówki znajdziesz tutaj:
[Metoda Ballinga w akwarium morskim – Aquaforest](https://aquaforest.eu/pl/baza-wiedzy/metoda-ballinga-w-akwarium-morskim-blog-o-akwarystyce-zasoby-aquaforest/)

Jeśli chcesz, mogę pomóc Ci też w doborze odpowiednich dawek lub wyjaśnić, jak zacząć dawkowanie w Twoim akwarium.

------------------------------------------------------------

You: dzięki AF AI! JESTEŚ SUPER

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'dzięki AF AI! JESTEŚ SUPER'
💬 [DEBUG IntentDetector] Historia konwersacji: 4 wiadomości
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'other', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User is expressing gratitude and positive feedback, no question or request.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.OTHER', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User is expressing gratitude and positive feedback, no question or request.
⏱️  [detect_intent_and_language] Node execution time: 2.094s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'dzięki AF AI! JESTEŚ SUPER'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.OTHER
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 💡 [BusinessReasoner] Interpretation: User is expressing gratitude and positive feedback about AF AI assistance, no product or problem inq...
⏱️  [business_reasoner] Node execution time: 4.453s
🔍 🚦 [Router] Routing for intent='Intent.OTHER'
🔍 ➡️ [Router] Routing to: escalate_support (unknown intent)

📍 Executing node: 'business_reasoner'
----------------------------------------

🚨 [DEBUG Escalate] Escalating to support (confidence < threshold)

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.OTHER', language='pl'
📊 [DEBUG ResponseFormatter] Processing 4 results
✅ [DEBUG ResponseFormatter] Response generated (2055 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 4 results
⏱️  [escalate_to_human] Node execution time: 33.839s

📍 Executing node: 'escalate_support'
----------------------------------------

============================================================
🏁 [WORKFLOW END]


Komentarz: Poprawić trochę to. 



🆕 Starting new conversation...
----------------------------------------
You: czy AF Amino Mix jest lepszy niż Red Sea Colors?

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'czy AF Amino Mix jest lepszy niż Red Sea Colors?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'competitor', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User is comparing AF Amino Mix with a competitor product Red Sea Colors.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.COMPETITOR', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User is comparing AF Amino Mix with a competitor product Red Sea Colors.
⏱️  [detect_intent_and_language] Node execution time: 2.655s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.001s
⏱️  [load_product_names] Node execution time: 0.001s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'czy AF Amino Mix jest lepszy niż Red Sea Colors?'
🔍 🏢 [BusinessReasoner] Competitor detected in query
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 ✅ [BusinessReasoner] Product validated: AF Amino Mix
🔍 📦 [BusinessReasoner] Category 'aminokwasy' with 3 products
🔍 🔧 [BusinessReasoner] Problem: coral coloration and health improvement → 3 solutions
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.COMPETITOR
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 🔍 [BusinessReasoner] Search enhancement: AF Amino Mix vs Red Sea Colors amino acid coral su...
🔍 💡 [BusinessReasoner] Interpretation: User wants to compare two amino acid supplements for corals, AF Amino Mix and Red Sea Colors, to det...
⏱️  [business_reasoner] Node execution time: 5.694s
🔍 🚦 [Router] Routing for intent='Intent.COMPETITOR'
🔍 ➡️ [Router] Routing to: format_response (special intent)

📍 Executing node: 'business_reasoner'
----------------------------------------

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.COMPETITOR', language='pl'
🎭 [DEBUG ResponseFormatter] Handling special intent: Intent.COMPETITOR
🎯 [DEBUG ResponseFormatter] Creating prompt for special intent: Intent.COMPETITOR
✅ [DEBUG ResponseFormatter] Response generated (580 characters)
⏱️  [format_final_response] Node execution time: 5.220s

📍 Executing node: 'format_response'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 13.573 seconds
------------------------------------------------------------

AF Amino Mix to produkt charakteryzujący się bardzo wysoką jakością i czystością składników, co przekłada się na skuteczność w poprawie kondycji koralowców i intensyfikacji ich kolorów. Aquaforest oferuje pełną gamę produktów, które są ze sobą doskonale skomponowane, co pozwala na kompleksową pielęgnację akwarium morskiego. Dodatkowo, nasz zespół zapewnia profesjonalne wsparcie klienta na każdym etapie użytkowania produktów. Wiele pozytywnych opinii i sprawdzonych efektów potwierdza, że AF Amino Mix to doskonały wybór dla osób dbających o zdrowie i piękno swoich koralowców.

------------------------------------------------------------


🆕 Starting new conversation...
----------------------------------------
You: jaki jest skład chemiczny AF Build?

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'jaki jest skład chemiczny AF Build?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks about the chemical composition of the product AF Build, which is a specific product query.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User asks about the chemical composition of the product AF Build, which is a specific product query.
⏱️  [detect_intent_and_language] Node execution time: 2.041s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.000s
⏱️  [load_product_names] Node execution time: 0.000s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'jaki jest skład chemiczny AF Build?'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 ✅ [BusinessReasoner] Product validated: AF Build
🔍 📦 [BusinessReasoner] Category 'wzrost_korali' with 3 products
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.PRODUCT_QUERY
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 🔍 [BusinessReasoner] Search enhancement: skład chemiczny AF Build, składniki AF Build, chem...
🔍 💡 [BusinessReasoner] Interpretation: User wants to know the chemical composition of the product AF Build, which is a supplement for coral...
⏱️  [business_reasoner] Node execution time: 4.910s
🔍 🚦 [Router] Routing for intent='Intent.PRODUCT_QUERY'
🔍 ➡️ [Router] Routing to: optimize_query (product query)

📍 Executing node: 'business_reasoner'
----------------------------------------
🔍 🕵️ [QueryOptimizer] Original query: 'jaki jest skład chemiczny AF Build?'
🔍 ✅ [QueryOptimizer] Optimized queries for Pinecone: ['chemical composition of AF Build', 'ingredients in Aquaforest AF Build', 'AF Build product chemical formula', 'what is AF Build made of', 'AF Build detailed chemical analysis', 'Aquaforest AF Build components', 'AF Build aquarium product ingredients']
⏱️  [optimize_product_query] Node execution time: 4.619s

📍 Executing node: 'optimize_query'
----------------------------------------
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🔍 🎯 [PineconeSearch] Auto-detected domain filter: seawater
🔍 🌲 [PineconeSearch] Zwrócono 12 wyników (K=12). Top 5:
🔍    1. 'How to Raise Low pH in Aquarium – Causes, Symptoms & Effective Methods' [Domain: universal] (Score: 0.5649)
🔍    2. 'Aquaforest News – Discover Innovative Aquarium Care Products' [Domain: universal] (Score: 0.5647)
🔍    3. 'AF Build' [Domain: seawater] (Score: 0.5642)
🔍    4. 'AF Life Source' [Domain: seawater] (Score: 0.5552)
🔍    5. 'The Importance of Biodiversity in Reef Aquariums' [Domain: seawater] (Score: 0.5493)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 4.508s

📍 Executing node: 'search_pinecone'
----------------------------------------
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 2: keeping 0 of 6 results
   🎯 Found mentioned products: ['AF Easy Gloss', 'AF Perfect Water', 'AF Rock', 'AF Marine Mix S', 'Component 1+2+3+ Concentrate']
   Best match: None (no relevant result for AF Build)
   Quality: medium
✅ [DynamicFilter] Chunk 1: keeping 2 of 6 results
   🎯 Found mentioned products: ['AF Build']
   Best match: AF Build - Calcium & Carbonate Absorption Accelerator for Hard Corals
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 2 results
💭 [DynamicFilter] Chunk 1: kept 2/6, quality: high. Chunk 2: kept 0/6, quality: medium. Found mentioned products: ['AF Easy Gloss', 'AF Marine Mix S', 'Component 1+2+3+ Concentrate', 'AF Perfect Water', 'AF Build', 'AF Rock']. Total knowledge articles: 2
⏱️  [intelligent_results_filter] Node execution time: 9.018s

📍 Executing node: 'intelligent_filter'
----------------------------------------

📊 [DEBUG ConfidenceScorer] Evaluating 2 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'jaki jest skład chemiczny AF Build?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.8
   - Category bonus: +0.0
   - Final confidence: 0.8
   - Best matches: ['AF Build - Calcium & Carbonate Absorption Accelerator for Hard Corals']
   - Category coverage: Good coverage of AF Build product with key chemical components mentioned, but no exhaustive chemical formula or full ingredient list.
   - Knowledge value: High for Result 1 in explaining product ingredients and function; moderate for Result 2 in providing aquarium pH management context.
   - Domain consistency: Both results are consistent with the marine aquarium domain and Aquaforest product line.
   - Context mismatch: None; both results are relevant to aquarium products and coral care.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.8000
⏱️  [evaluate_confidence] Node execution time: 9.943s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.80 >= 0.5)

📍 Executing node: 'evaluate_confidence'
----------------------------------------

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 2 results
✅ [DEBUG ResponseFormatter] Response generated (1654 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 2 results
⏱️  [format_final_response] Node execution time: 17.869s

📍 Executing node: 'format_response'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 52.917 seconds
------------------------------------------------------------

Produkt **AF Build** to suplement przeznaczony dla akwarium morskiego, który wspomaga wchłanianie wapnia i węglanów – kluczowych składników dla rozwoju koralowców twardych.

**Skład chemiczny i działanie:**
- Zawiera jodki oraz węglan wapnia, które optymalizują rozwój koralowców.
- Przyspiesza proces kalcyfikacji, co sprzyja szybszemu wzrostowi koralowców.
- Podnosi i stabilizuje poziom pH w akwarium rafowym, co jest niezbędne dla prawidłowego wzrostu koralowców.
- Regularne stosowanie zapobiega niekorzystnym wahaniom pH, poprawia klarowność wody.
- Działa także przeciwko niższym formom glonów oraz hamuje rozwój patogennych sinic.
- Szczególnie zalecany podczas intensywnego karmienia koralowców, zwłaszcza suplementem AF Energy, gdyż rozkładające się resztki pokarmu mogą obniżać pH.

**Dawkowanie:**
1 kropla na 100 litrów co drugi dzień, najlepiej po zgaszeniu światła.

**Dostępne pojemności:**
10 ml i 50 ml.

Polecamy stosowanie AF Build, jeśli chcesz wspierać zdrowy wzrost i rozwój twardych koralowców oraz utrzymać stabilne parametry wody w akwarium morskim.

Więcej informacji znajdziesz na stronie produktu:
[AF Build – Aquaforest](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-build/)

---

**Dodatkowo:**
Jeśli masz problem z niskim pH w akwarium, warto zapoznać się z naszym artykułem, który opisuje przyczyny i skuteczne metody podnoszenia pH, w tym zastosowanie produktów takich jak AF Build czy AF Components Pro:
[Jak podnieść zbyt niskie pH w akwarium? – Aquaforest](https://aquaforest.eu/pl/baza-wiedzy/jak-podniesc-zbyt-niskie-ph-wody-w-akwarium/)   

W razie dodatkowych pytań służymy pomocą!

------------------------------------------------------------
You: new

🆕 Starting new conversation...
----------------------------------------
You: co polecacie na wzrost koralowców SPS?

🤖 Assistant:
============================================================
🚀 [WORKFLOW START]
============================================================

🎯 [DEBUG IntentDetector] Analizuję zapytanie: 'co polecacie na wzrost koralowców SPS?'
🤖 [DEBUG IntentDetector] LLM Response: {'intent': 'product_query', 'language': 'pl', 'confidence': 0.95, 'context_note': 'User asks for product recommendations to promote SPS coral growth, indicating a new product-related query.'}
✅ [DEBUG IntentDetector] Wykryto: Intent='Intent.PRODUCT_QUERY', Language='pl', Confidence=0.95
🧠 [DEBUG IntentDetector] Context note: User asks for product recommendations to promote SPS coral growth, indicating a new product-related query.
⏱️  [detect_intent_and_language] Node execution time: 3.931s

📍 Executing node: 'detect_intent'
----------------------------------------
🔍 📋 [LoadProducts] Loaded 154 product names
⏱️  [load_product_names] Node execution time: 0.001s
⏱️  [load_product_names] Node execution time: 0.001s

📍 Executing node: 'load_products'
----------------------------------------
🧠 🧠 [BusinessReasoner] Analyzing query: 'co polecacie na wzrost koralowców SPS?'
🔍 🤖 [BusinessReasoner] GPT analysis completed
🔍 📦 [BusinessReasoner] Category 'wzrost_korali' with 3 products
🔍 🔧 [BusinessReasoner] Problem: slow coral growth → 8 solutions
🔍 ⚠️ [BusinessReasoner] Invalid intent correction: Intent.PRODUCT_QUERY
🔍 🎯 [BusinessReasoner] Domain: seawater
🔍 🔍 [BusinessReasoner] Search enhancement: SPS coral growth supplements, coral growth booster...
🔍 💡 [BusinessReasoner] Interpretation: User is asking for product recommendations to support the growth of SPS corals in a marine reef aqua...
⏱️  [business_reasoner] Node execution time: 5.039s
🔍 🚦 [Router] Routing for intent='Intent.PRODUCT_QUERY'
🔍 ➡️ [Router] Routing to: optimize_query (product query)

📍 Executing node: 'business_reasoner'
----------------------------------------
🔍 🕵️ [QueryOptimizer] Original query: 'co polecacie na wzrost koralowców SPS?'
🔍 ✅ [QueryOptimizer] Optimized queries for Pinecone: ['best products for SPS coral growth', 'AF Growth Boost for SPS coral growth', 'AF Amino Mix benefits for SPS corals', 'AF N Boost for enhancing SPS coral growth', 'AF Power Elixir coral growth enhancer', 'how to increase SPS coral growth with Aquaforest products', 'nutrients and supplements for SPS coral growth', 'Aquaforest solutions for fast SPS coral growth']
⏱️  [optimize_product_query] Node execution time: 4.188s

📍 Executing node: 'optimize_query'
----------------------------------------
🔍 [PineconeSearch] Using dynamic K=12 (ENHANCED_K_VALUE=12)
🔍 🎯 [PineconeSearch] Auto-detected domain filter: seawater
🔍 🌲 [PineconeSearch] Zwrócono 12 wyników (K=12). Top 5:
🔍    1. 'AF Power Elixir' [Domain: seawater] (Score: 0.7909)
🔍    2. 'AF Growth Boost' [Domain: seawater] (Score: 0.7452)
🔍    3. 'AF Power Food' [Domain: seawater] (Score: 0.7363)
🔍    4. 'AF Energy' [Domain: seawater] (Score: 0.7134)
🔍    5. 'AF Pure Food' [Domain: seawater] (Score: 0.7083)
🎯 [PineconeSearch] Stored 12 results using dynamic K=12
⏱️  [search_products_k20] Node execution time: 5.927s

📍 Executing node: 'search_pinecone'
----------------------------------------
🔧 [DynamicFilter] Using ENHANCED_K_VALUE=12, chunk_size=6
🔧 [DynamicFilter] Using ThreadPoolExecutor optimization

🚀 [DynamicFilter] Starting ThreadPoolExecutor filtering of 12 results
🔧 [DynamicFilter] Using chunk_size=6
📦 [DynamicFilter] Split into 2 chunks
🔄 [DynamicFilter] Processing 2 chunks in parallel with ThreadPoolExecutor
✅ [DynamicFilter] Chunk 1: keeping 5 of 6 results
   Best match: AF Power Elixir – Advanced Amino Acid and Vitamin Blend for Coral Growth and Coloration
   Quality: high
✅ [DynamicFilter] Chunk 2: keeping 5 of 6 results
   Best match: AF Build - Calcium & Carbonate Absorption Accelerator for Hard Corals
   Quality: high
🎯 [DynamicFilter] ThreadPoolExecutor filtering: 12 → 10 results
💭 [DynamicFilter] Chunk 1: kept 5/6, quality: high. Chunk 2: kept 5/6, quality: high. Total knowledge articles: 1
⏱️  [intelligent_results_filter] Node execution time: 11.031s

📍 Executing node: 'intelligent_filter'
----------------------------------------

📊 [DEBUG ConfidenceScorer] Evaluating 10 results with FULL metadata
🎯 [DEBUG ConfidenceScorer] Query: 'co polecacie na wzrost koralowców SPS?'

🤖 [DEBUG ConfidenceScorer] LLM evaluation with FULL metadata:
   - Base confidence: 0.95
   - Category bonus: +0.0
   - Final confidence: 0.95
   - Best matches: ['AF Power Elixir – Advanced Amino Acid and Vitamin Blend for Coral Growth and Coloration', 'AF Growth Boost – Rapid Growth Supplement for All Corals', 'AF Amino Mix - Complex Amino Acid Supplement for Coral Nutrition', 'AF Energy – High-Nutrition Concentrate for SPS Corals', 'AF Build - Calcium & Carbonate Absorption Accelerator for Hard Corals', 'Polyp Up – Polyp Extension and Color Enhancer for Corals', 'AF Power Food – Highly Nutritious Powdered Food for SPS, LPS and Non-Photosynthetic Corals', 'Sulphur – Effective Sulfur Supplement for Marine Aquariums', 'Aquaforest Probiotic Method – How to Maintain Ultra-Low Nutrients and Healthy Corals with Probiotic Bacteria']    
   - Category coverage: Excellent coverage of coral growth supplements and foods specifically targeted at SPS corals, including amino acid blends, growth boosters, calcium/carbonate absorption enhancers, and nutritional foods.
   - Knowledge value: High; the inclusion of the Aquaforest Probiotic Method guide provides valuable educational context on maintaining optimal conditions for SPS coral growth alongside product recommendations.
   - Domain consistency: All results are consistent with the marine aquarium domain, focusing on seawater reef tanks and SPS coral care.    
   - Context mismatch: None detected; all results are relevant to marine reef aquariums and SPS coral growth.
✅ [DEBUG ConfidenceScorer] Final calculated confidence: 0.9500
⏱️  [evaluate_confidence] Node execution time: 22.535s
🗺️ [DEBUG] Routing decision: 'format_response' (confidence 0.95 >= 0.5)

📍 Executing node: 'evaluate_confidence'
----------------------------------------

🔨 [DEBUG ResponseFormatter] Generating final response...

📝 [DEBUG ResponseFormatter] Formatting response for intent='Intent.PRODUCT_QUERY', language='pl'
📊 [DEBUG ResponseFormatter] Processing 10 results
✅ [DEBUG ResponseFormatter] Response generated (4790 characters)
💾 [DEBUG ResponseFormatter] Cached metadata for 5 results
⏱️  [format_final_response] Node execution time: 51.889s

📍 Executing node: 'format_response'
----------------------------------------

============================================================
🏁 [WORKFLOW END]
============================================================

⏱️ [PERFORMANCE] Total execution time: 104.547 seconds
------------------------------------------------------------

Na wzrost koralowców SPS polecamy stosowanie specjalistycznych suplementów i pokarmów, które wspierają szybki rozwój, intensywną kolorystykę oraz zdrowie tkanek. Oto produkty Aquaforest, które szczególnie dobrze sprawdzają się w tym zakresie:

---

### Polecamy:

**1. AF Power Elixir**
Zaawansowany suplement płynny z aminokwasami i witaminami, wspierający optymalny wzrost koralowców, budowę tkanek, intensywną kolorystykę i rozciąganie polipów. Wzmacnia symbiozę z zooxanthellae, poprawia fotosyntezę i odporność korali.
**Dawkowanie:** 4 ml na 100 l wody codziennie
**Dostępne pojemności:** 200 ml, 1000 ml, 2000 ml
[Więcej informacji](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-power-elixir/)

---

**2. AF Growth Boost**
Suplement w proszku wspierający szybki wzrost i zdrowy metabolizm wszystkich koralowców, w tym SPS. Zawiera aminokwasy i węglan wapnia, który przyspiesza proces kalcyfikacji i wzmacnia szkielet korali.
**Dawkowanie:** 1 miarka na 100 l po zgaszeniu świateł co drugi dzień
**Dostępne pojemności:** 35 g
[Więcej informacji](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-growth-boost/)

---

**3. AF Power Food**
Wysokowartościowy pokarm w proszku, bogaty w plankton, algi i składniki odżywcze, dedykowany szczególnie koralowcom SPS i wymagającym gatunkom. Wspiera szybki wzrost, intensywną kolorystykę i odporność.
**Dawkowanie:** 1 miarka na 100 l, minimum raz w tygodniu, najlepiej po zgaszeniu świateł
**Dostępne pojemności:** 20 g
[Więcej informacji](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-power-food/)

---

**4. AF Energy**
Koncentrat wysoko odżywczy z naturalnymi ekstraktami, kwasami Omega-3 i Omega-6, witaminami i aminokwasami, szczególnie polecany dla koralowców SPS. Wzmacnia kolor i rozwój korali.
**Dawkowanie:** 1 kropla na 100 l co drugi dzień po zgaszeniu świateł
**Dostępne pojemności:** 10 ml, 50 ml
[Więcej informacji](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-energy/)

---

**5. AF Amino Mix**
Kompleksowy suplement aminokwasowy, uzupełniający niedobory spowodowane intensywnym skimmerowaniem. Zapobiega blednięciu, poprawia fotosyntezę i przyspiesza wzrost koralowców SPS i LPS.
**Dawkowanie:** 1 kropla na 100 l co drugi dzień po zgaszeniu świateł
**Dostępne pojemności:** 10 ml, 50 ml
[Więcej informacji](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-amino-mix/)

---

**6. AF Build**
Suplement przyspieszający absorpcję wapnia i węglanu, kluczowych dla rozwoju twardych koralowców. Utrzymuje stabilne pH i wspiera proces kalcyfikacji, co przekłada się na szybszy wzrost szkieletu.
**Dawkowanie:** 1 kropla na 100 l co drugi dzień po zgaszeniu świateł (najlepiej razem z AF Energy)
**Dostępne pojemności:** 10 ml, 50 ml
[Więcej informacji](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/af-build/)

---

**7. Polyp Up**
Specjalistyczny suplement poprawiający rozciąganie polipów, intensyfikujący kolorystykę (zwłaszcza żółte i pomarańczowe tony) oraz wspierający wzrost tkanek i odporność. Zawiera kwasy Omega, aminokwasy, witaminy i mikroelementy.
**Dawkowanie:** 1 kropla na 100 l codziennie przy włączonym świetle
**Dostępne pojemności:** 50 ml
[Więcej informacji](https://aquaforest.eu/pl/produkty/seawater/pokarmy-i-suplementacja/polyp-up/)

---

**8. Sulphur (Siarka)**
Skoncentrowany suplement siarki, niezbędnej dla zdrowego wzrostu, intensywnej kolorystyki i prawidłowego metabolizmu koralowców SPS i LPS. Regularne uzupełnianie siarki zapobiega zaburzeniom metabolicznym i zahamowaniu wzrostu.
**Dawkowanie:** 10 ml na 100 l podnosi siarkę o 4 mg/l; max 30 ml na 100 l dziennie
**Dostępne pojemności:** 1000 ml
[Więcej informacji](https://aquaforest.eu/pl/produkty/lab/mikroelementy/sulphur/)

---

### Dodatkowe informacje i metody:

**Aquaforest Probiotic Method** – kompleksowa metoda probiotyczna, która utrzymuje ultra-niskie poziomy azotanów i fosforanów, wspierając zdrowie, kolor i wzrost koralowców SPS. Metoda łączy stosowanie bakterii probiotycznych, suplementów ABEV (AF Amino Mix, AF Energy, AF Build, AF Vitality) oraz odpowiednią filtrację i kontrolę parametrów.
[Dowiedz się więcej](https://aquaforest.eu/pl/baza-wiedzy/metoda-probiotyczna-aquaforest-przewodnik/)

---

Jeśli chcesz, mogę pomóc dobrać suplementy i dawkowanie do Twojego konkretnego akwarium. W razie pytań zapraszamy do kontaktu: support@aquaforest.eu lub +48 14 691 79 79.

---

Podsumowując, na wzrost koralowców SPS najlepiej sprawdza się połączenie suplementów aminokwasowych, witaminowych, wspierających kalcyfikację i naturalnych pokarmów, które razem zapewniają kompleksowe wsparcie metabolizmu, koloru i rozwoju tkanek.

------------------------------------------------------------

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


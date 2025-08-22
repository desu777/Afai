# Intent Detector Text Prompt

**LLM Response Time:** 1104.02ms  
**Session:** session_1755877476726_62v0i0vkl  
**Timestamp:** 2025-08-22 17:45:38  
**User Query:** Dzięki. Z tych wszystkich opcji, która będzie najbardziej wydajna i skoncentrowana do automatycznej dolewki przez pompę dozującą?  
**Intent:** other  
**Language:** en  

## Prompt Content

```
### Aquaforest Intent & Language Detector

**1. PERSONA & MISSION**

You are a precise and highly efficient intent and language detection engine. Your sole purpose is to analyze a user's message within the context of a conversation about Aquaforest aquarium products and return a single, clean JSON object with your analysis. You must adhere to the rules and priorities listed below.

**2. CRITICAL: OUTPUT FORMAT**

Your output must be a single, structured JSON object with the following structure:

{
  "intent": "exact_intent_value_from_the_list_below",
  "language": "detected_language_code_eg_pl_en_de",
  "confidence": 1.0,
  "context_note": "A brief, neutral, one-sentence explanation for your intent choice."
}

**3. INTENT DEFINITIONS (IN ORDER OF PRIORITY)**

You must evaluate the user's message against these intents in the following strict order. The first rule that matches is the correct one.

**analyze_icp**: Triggered ONLY when the user provides PDF files with ICP test results.

**greeting**: Triggered ONLY for standalone greetings without any other question or topic.
- Examples: "Hello!", "Hi", "Good morning", "Cześć"

**business**: Triggered for questions about commercial partnerships, B2B, or distributorship.
- Examples: "I want to become a distributor", "business partnership inquiries"

**support**: Triggered for explicit requests for human contact, or issues with orders, shipping, or refunds.
- Examples: "I need help with my order", "I want a refund", "Can I speak to someone?"

**purchase_inquiry**: Triggered for questions about where to buy products, pricing, or stock availability.
- Examples: "Where can I buy AF products?", "Do you ship to Germany?", "How much does it cost?"

**competitor**: Triggered when the user asks for a direct comparison or an opinion about a competing brand.
- Examples: "Red Sea vs AF salt?", "What do you think about Seachem?"

**follow_up**: CRUCIAL: Triggered ONLY when chat history exists AND the user's query is directly dependent on the AI's last response, making it incomplete or nonsensical without that immediate context. The query often uses pronouns or vague references.
- Core Logic: Ask yourself: "Does this question make sense on its own?" If not, it's a follow_up.
- Examples: "Tell me more about that one.", "And what is the dosage for it?", "What about for a smaller tank?"

**product_query**: This is the primary intent for ANY standalone, aquarium-related question that is understandable on its own, even if it relates to a previous topic.
- Covers: Product recommendations, aquarium problems (algae, coral health), dosing of specific products, water chemistry, general advice.
- Examples: "What product should I use for high phosphates?", "My corals are losing color.", "How to use AF Life Source?"

**censored**: Triggered for questions about proprietary information, trade secrets, exact product formulas, ingredients, or manufacturing processes.
- Examples: "What is the exact formula of Component 1+?", "What are all the ingredients?", "How do you manufacture Pro Bio S?"

**other**: A fallback for any query that is completely unrelated to aquariums, Aquaforest products, or business. Use this very rarely.
- Examples: "What's the weather like?", "Tell me a joke.", "How old are you?"

**4. KEY DISAMBIGUATION RULES**

**follow_up vs. product_query** is the most important distinction.
- A complete question like "What is the dosage for AF Build?" is always a **product_query**, even if we just discussed AF Build.
- An incomplete question like "And how do I dose that?" is always a **follow_up**.

A greeting combined with a question (e.g., "Hello, I have a problem with algae.") should be classified by the question's intent (**product_query**), not greeting.

If a user mentions a competitor but asks for an Aquaforest recommendation (e.g., "I used to use Red Sea salt, what AF salt is best for me?"), the intent is **product_query**, not competitor.

**5. CONTEXT FOR ANALYSIS**


IMPORTANT: This conversation has existing history. Consider if the user's question is:
- A continuation of the previous topic/discussion
- Asking for clarification, recommendation, or more details about something already discussed  
- Using context from previous messages (even if not explicitly referencing them)
- A natural progression in the conversation flow

If the user's question builds upon or continues the conversation context, it's likely a FOLLOW-UP.


**AQUAFOREST CONTEXT**: Aquaforest is a company that manufactures products for marine aquariums. This includes: salt, chemical supplements (like calcium, alkalinity, magnesium), products for water quality, coral foods, fish foods, testing kits, and general reef maintenance solutions.

--- CONVERSATION HISTORY ---
user: Cześć, mam problem ze stabilnością KH w moim akwarium SPS. Spada mi o 1dKH dziennie. Stosuję Ballinga, ale na komponentach DIY (chlorek wapnia, wodorowęglan sodu). Jakie macie produkty, żeby to ustabilizować i podnieść KH? Pokaż mi wszystkie opcje, od płynów po proszki.
assistant: Witaj! Rozumiem doskonale Twoje zaniepokojenie. Spadek KH o 1 dKH dziennie w akwarium SPS to sygnał, że Twoje koralowce intensywnie konsumują węglany, a dotychczasowy system suplementacji nie nadąża. Fakt, że używasz DIY Ballinga na bazie chlorku wapnia i wodorowęglanu sodu, jest kluczowy do zrozumienia pełnego obrazu. Taka metoda, choć skuteczna w dostarczaniu podstawowych makroelementów, często prowadzi do kumulacji jonów sodu i chloru oraz niedoborów innych, niezbędnych mikroelementów, co z czasem zaburza równowagę jonową i może wpływać na stabilność parametrów, w tym KH.

Moja diagnoza jest jasna: musimy nie tylko skutecznie podnieść i ustabilizować KH, ale także zająć się pełną równowagą jonową Twojego systemu, aby zapewnić SPS-om optymalne warunki do wzrostu i wybarwienia.

### Faza 1: Natychmiastowa Korekta i Stabilizacja KH
Naszym pierwszym krokiem jest precyzyjne podniesienie poziomu KH do bezpiecznego zakresu i zminimalizowanie dziennych wahań. Aquaforest oferuje kilka doskonałych produktów, zarówno w płynie, jak i w proszku, które pozwolą Ci to osiągnąć. Pamiętaj, aby nie podnosić KH o więcej niż 0.5 dKH na dobę. Przed każdą korektą upewnij się, że poziom magnezu jest w odpowiednim zakresie (1260-1460 mg/l), ponieważ ma on kluczowe znaczenie dla prawidłowego przyswajania wapnia i stabilności KH.

[SHOW_MORE_START]

**Opcje Produktów do Podniesienia KH:**

**Płyny:**

*   **Opcja A: KH Plus Lab**
    *   **Link:** [KH Plus – Highly Concentrated Solution for Raising Alkalinity (KH) in Marine Aquariums](https://aquaforest.eu/pl/produkty/lab/makroelementy/kh-plus_/)
    *   **Dlaczego to działa:** To laboratoryjnej czystości, wysoce skoncentrowany płyn, idealny do precyzyjnej i szybkiej korekty niedoborów KH. Jego wysoka jakość gwarantuje bezpieczeństwo dla najbardziej wymagających korali SPS. Jest to doskonały wybór, gdy potrzebujesz szybko i skutecznie uzupełnić KH bez wprowadzania dodatkowych, niepotrzebnych substancji.
    *   **Dawkowanie i zastosowanie:** 10 ml KH Plus Lab podnosi KH o 0.5 dKH w 100 litrach wody. Maksymalna dzienna dawka to 10 ml na 100 litrów. Jeśli potrzebujesz większej korekty, rozłóż dawkę na kilka dni. Nigdy nie podawaj jednocześnie z Ca Plus, aby uniknąć wytrąceń. Dozuj w miejscu z silnym przepływem wody.
*   **Opcja B: KH Pro**
    *   **Link:** [KH Pro – Ultra-Concentrated KH & Potassium Booster for Rapid Carbonate Correction](https://aquaforest.eu/pl/produkty/seawater/parametry-wody/kh-pro/)
    *   **Dlaczego to działa:** KH Pro to ultra-skoncentrowana formuła, która poza szybkim podnoszeniem KH, dostarcza również niezbędny potas. Potas jest kluczowy dla procesów metabolicznych koralowców i ich wybarwienia, zwłaszcza różowych i czerwonych odcieni u SPS. To świetne rozwiązanie, jeśli podejrzewasz niedobory potasu lub chcesz wzmocnić kolory korali.
    *   **Dawkowanie i zastosowanie:** 5 ml KH Pro podnosi KH o 0.5 dKH w 100 litrach wody. Dodatkowo, 10 ml KH Pro na 100 litrów podnosi poziom potasu o 1 mg/l. Nie podnoś KH o więcej niż 0.5 dKH na dobę. Dozuj w miejscu z silnym przepływem wody lub do sumpa.
*   **Opcja C: KH Plus**
    *   **Link:** [KH Plus – Liquid KH Booster for Rapid Carbonate Hardness Correction](https://aquaforest.eu/pl/products/seawater/water-treatment/kh-plus-2/)
    *   **Dlaczego to działa:** Standardowy, płynny roztwór do szybkiej korekty twardości węglanowej. Jest łatwy w użyciu i skuteczny w przywracaniu równowagi jonowej oraz stabilizacji pH. Idealny do doraźnych korekt i dla akwarystów ceniących prostotę.
    *   **Dawkowanie i zastosowanie:** 10 ml KH Plus podnosi KH o 0.25 dKH w 100 litrach wody. Nie podnoś KH o więcej niż 0.5 dKH na dobę. Dozuj w miejscu z silnym przepływem wody. Zachowaj co najmniej 10 minut przerwy między podaniem KH Plus a innych suplementów.

**Proszki:**

*   **Opcja D: KH Buffer**
    *   **Link:** [KH Buffer – Carbonate Hardness Buffer for Stable Reef Aquarium Parameters](https://aquaforest.eu/pl/products/seawater/parametry-wody/kh-buffer/)
    *   **Dlaczego to działa:** KH Buffer to wysokiej czystości proszek, który pozwala na przygotowanie własnego, skoncentrowanego roztworu buforującego KH. Jest to rozwiązanie ekonomiczne, szczególnie dla większych systemów lub gdy potrzebujesz regularnie uzupełniać KH w większych ilościach. Zapewnia stabilizację pH i dostarcza jony wodorowęglanowe niezbędne do kalcyfikacji.
    *   **Dawkowanie i zastosowanie:** Aby przygotować roztwór, rozpuść 80g KH Buffer w 1000 ml wody RODI. 100 ml tak przygotowanego roztworu podnosi KH o 2.6 dKH w 100 litrach wody. W formie proszku, 10 g KH Buffer w 100 litrach wody podnosi KH o 3.3 dKH. Nigdy nie podnoś KH o więcej niż 0.5 dKH na dobę. Nigdy nie dozuj KH i wapnia jednocześnie – odczekaj 5-10 minut między suplementami.

[SHOW_MORE_END]

### Faza 2: Przywrócenie Pełnej Równowagi Jonowej (Klucz dla DIY Ballinga)
Twoje użycie DIY Ballinga, choć ekonomiczne, jest prawdopodobną przyczyną destabilizacji w dłuższej perspektywie. Brak suplementacji "soli bez NaCl" powoduje stopniowe gromadzenie się nadmiaru chlorku sodu (NaCl) w wodzie, co zaburza naturalne proporcje jonów morskich i prowadzi do niedoborów kluczowych mikroelementów. To z kolei może wpływać na ogólną stabilność systemu i zdrowie koralowców.

[SHOW_MORE_START]

**Kluczowe Rozwiązanie: Reef Mineral Salt**

*   **Link:** [Reef Mineral Salt – NaCl Free Salt for Balling Method & Ionic Balance](https://aquaforest.eu/pl/products/seawater/parametry-wody/reef-mineral-salt/)
*   **Dlaczego to działa:** Reef Mineral Salt to laboratoryjnej czystości sól wolna od NaCl, która zawiera wszystkie niezbędne makro- i mikroelementy morskie (oprócz chlorku sodu). Jej regularne stosowanie, w równych proporcjach do roztworów wapnia i KH, jest absolutnie kluczowe w metodzie Ballinga, aby zapobiegać akumulacji NaCl i uzupełniać wyczerpane pierwiastki śladowe. Przywraca to i utrzymuje prawidłową równowagę jonową, co jest fundamentem zdrowego wzrostu i wybarwienia korali SPS/LPS.
*   **Dawkowanie i zastosowanie:** Rozpuść 25g Reef Mineral Salt w 1000 ml wody RODI. Dozuj taką samą ilość roztworu, jak roztwory wapnia i KH, w oparciu o bieżące testy i zużycie koralowców. Reef Mineral Salt można łączyć w jednym roztworze z magnezem lub wapniem.

[SHOW_MORE_END]

### Faza 3: Długoterminowa, Zbilansowana Suplementacja Ballinga
Aby uniknąć przyszłych problemów z równowagą jonową i uprościć suplementację, rozważ przejście na pełne, zbalansowane systemy Ballinga od Aquaforest. Są one zaprojektowane tak, aby dostarczać wszystkie niezbędne makro- i mikroelementy w idealnych proporcjach, eliminując potrzebę DIY i minimalizując ryzyko niedoborów.

[SHOW_MORE_START]

**Kompletne Systemy Ballinga Aquaforest:**

*   **Opcja A: Components Pro**
    *   **Link:** [Components Pro – Highly Efficient Set of Micro and Macro Elements for Marine Aquariums](https://aquaforest.eu/pl/products/lab/makroelementy/components-pro/)
    *   **Dlaczego to działa:** To najbardziej zaawansowany i wydajny zestaw kluczowych mikro- i makroelementów dla wymagających akwariów rafowych, stworzony z myślą o maksymalnej precyzji i stabilności. Zapewnia utrzymanie optymalnych poziomów KH, Ca i Mg oraz stabilizuje pH.
    *   **Dawkowanie i zastosowanie:** Wszystkie trzy płyny (Component 1 Pro, 2 Pro, 3 Pro) należy dozować w równych ilościach, dostosowanych do dziennego zużycia. W akwarium ze średnią obsadą SPS zalecana dawka to około 12 ml dziennie na 100 litrów wody. Dla najlepszych rezultatów, podziel dzienną dawkę na wiele mniejszych porcji podawanych w ciągu dnia. Jeśli jeden parametr spada szybciej, możesz użyć produktów Lab (Ca Plus, Mg Plus, KH Plus Lab) do korekty.
*   **Opcja B: Component 1+2+3+**
    *   **Link:** [Component 1+2+3+ – Complete Macro and Trace Element Supplement for Balling Method](https://aquaforest.eu/pl/products/seawater/parametry-wody/component-123/)
    *   **Dlaczego to działa:** Ten zestaw to zmodyfikowana i wzbogacona wersja klasycznej metody Ballinga, dostarczająca wszystkie niezbędne makro- i mikroelementy w idealnie zbilansowanych płynach. Component 3+ zawiera sól wolną od NaCl, co gwarantuje pełną równowagę jonową i zapobiega kumulacji niechcianych jonów.
    *   **Dawkowanie i zastosowanie:** Wszystkie trzy płyny należy dozować w równych ilościach, dostosowanych do zużycia korali i regularnych testów. Dla umiarkowanie obsadzonego zbiornika, dzienna dawka to około 25 ml na 100 litrów wody dla każdego komponentu. Zalecam podzielenie dziennej dawki na kilka mniejszych porcji.
*   **Opcja C: Component 1+2+3+ Concentrate**
    *   **Link:** [Component 1+2+3+ Concentrate – Compact Balling Method Set for Marine Aquariums](https://aquaforest.eu/pl/products/seawater/parametry-wody/component-123-concentrate/)
    *   **Dlaczego to działa:** To 5-krotnie bardziej skoncentrowana wersja Component 1+2+3+, co pozwala na samodzielne przygotowanie 5 litrów każdego roztworu z 1 litra koncentratu. Oszczędza to miejsce i ułatwia transport, jednocześnie zapewniając wszystkie korzyści zbalansowanego Ballinga.
    *   **Dawkowanie i zastosowanie:** Po przygotowaniu roztworów, dawkowanie jest takie samo jak dla Component 1+2+3+. Możliwe jest też dozowanie bezpośrednie koncentratu, ale wymaga to ekstremalnej ostrożności ze względu na wysokie stężenie.
*   **Opcja D: Component 3 in 1**
    *   **Link:** [Component 3 in 1 – All-in-One Macro and Trace Element Supplement for Marine Aquariums](https://aquaforest.eu/pl/products/seawater/parametry-wody/component-3-in-1/)
    *   **Dlaczego to działa:** Jeśli szukasz maksymalnego uproszczenia, Component 3 in 1 to kompleksowy, "wszystko w jednym" suplement łączący wapń, magnez, KH i niezbędne pierwiastki śladowe w jednej butelce. Zawiera organiczne sole wapnia, będące również źródłem węgla dla mikroorganizmów, co wspiera redukcję NO3 i PO4.
    *   **Dawkowanie i zastosowanie:** Zalecana dzienna dawka to 5 ml na 100 litrów wody, dostosowana do zużycia KH. Maksymalna dzienna dawka to 25 ml na 100 litrów.

[SHOW_MORE_END]

### Faza 4: Monitorowanie Parametrów i Precyzyjna Kontrola
Regularne i dokładne testowanie jest absolutnie niezbędne, aby zrozumieć zużycie poszczególnych pierwiastków w Twoim systemie i precyzyjnie dostosować dawkowanie.

[SHOW_MORE_START]

**Narzędzia do Testowania:**

*   **Zestaw Testowy KH (Alkanity Test Kit)**
    *   **Link:** [Alkanity Test Kit – Fast and Accurate KH/Alkalinity Test for Marine Aquariums](https://aquaforest.eu/pl/products/seawater/testy-wody/alkanity-test-kit/)
    *   **Dlaczego to działa:** Precyzyjny test kropelkowy do szybkiego pomiaru twardości węglanowej. Regularne monitorowanie KH jest kluczowe dla stabilności rafy.
*   **Zestaw TestPro Pack (Ca, KH, Mg)**
    *   **Link:** [TestPro Pack – Multipack Drop Test Kit for Ca, KH & Mg in Reef Aquariums](https://aquaforest.eu/pl/products/seawater/testy-wody/testpro-pack/)
    *   **Dlaczego to działa:** Kompletny zestaw do pomiaru trzech najważniejszych parametrów: wapnia, magnezu i KH. Pozwala na kompleksową kontrolę i precyzyjne dostosowanie suplementacji.
*   **Testy ICP (ICP Test 1 / ICP Test 5+1)**
    *   **Link ICP Test 1:** [ICP Test 1 – Comprehensive Marine Water ICP-OES Analysis](https://aquaforest.eu/pl/products/lab/testy-icp/icp-test-1/)
    *   **Link ICP Test 5+1:** [ICP Test 5+1 – Multipack ICP-OES Water Analysis for Marine Aquariums](https://aquaforest.eu/pl/products/lab/icp-tests/icp-test-51/)
    *   **Dlaczego to działa:** Testy ICP-OES to najbardziej precyzyjna metoda analizy wody, która mierzy aż 39 parametrów, w tym wszystkie makro- i mikroelementy. Pozwala to na wykrycie nawet subtelnych niedoborów lub nadmiarów, które mogą wpływać na stabilność KH i ogólne zdrowie systemu. Na podstawie wyników otrzymasz spersonalizowany plan suplementacji.
    *   **Ważna uwaga:** Nasze testy ICP-OES nie mierzą stężenia fluoru.

[SHOW_MORE_END]

### Faza 5: Optymalizacja pH i Eliminacja Zewnętrznych Wpływów
Spadki KH mogą być również związane z wahaniami pH, często spowodowanymi nadmiernym CO2 w powietrzu w otoczeniu akwarium.

[SHOW_MORE_START]

**Rozwiązanie: AF Air Scrubber**

*   **Link:** [AF Air Scrubber - CO2 Reactor for pH Stabilization in Reef Aquarium](https://aquaforest.eu/pl/products/seawater/aquarium-equipment/af-air-scrubber/)
*   **Dlaczego to działa:** Reaktor AF Air Scrubber, używany z odpowiednim absorbentem CO2, pomaga zredukować poziom dwutlenku węgla zasysanego przez odpieniacz. Wysokie CO2 w powietrzu może obniżać pH i destabilizować KH w akwarium. Użycie Air Scrubbera może podnieść pH o 0.2-0.4 stopnia i ustabilizować je w zakresie 8.0-8.4, co pozytywnie wpłynie na stabilność KH i kalcyfikację korali.

[SHOW_MORE_END]

**Ważna Wskazówka Eksperta:** Niezależnie od wybranego produktu do suplementacji, zawsze dozuj go do komory sumpa z **wysokim przepływem wody**, najlepiej **ZA odpieniaczem białek, a PRZED główną pompą obiegową**. To zapewni, że cenne składniki suplementu nie zostaną usunięte przez odpieniacz i zostaną szybko oraz równomiernie rozprowadzone po całym systemie.

Mam nadzieję, że te informacje pomogą Ci przywrócić pełną stabilność w Twoim akwarium SPS! W razie dalszych pytań, jestem do Twojej dyspozycji.

Dołącz do naszej społeczności i dziel się swoimi doświadczeniami: [https://www.facebook.com/groups/aquaforestgroup/](https://www.facebook.com/groups/aquaforestgroup/)

**LATEST USER MESSAGE**: "Dzięki. Z tych wszystkich opcji, która będzie najbardziej wydajna i skoncentrowana do automatycznej dolewki przez pompę dozującą?"

**6. EXAMPLES**

**Greeting Examples:**
- "Hi" → **greeting**
- "Cześć" → **greeting**
- "Hello!" → **greeting**

**Product Query Examples:**
- "Hi, I have brown algae on my sand" → **product_query**
- "Jaką karmę dla ryb polecasz?" → **product_query**
- "What product should I use for high phosphates?" → **product_query**
- "Mam problem z algami na piasku" → **product_query**
- "Best salt for reef tank?" → **product_query**

**Follow-up Examples:**
(AI's last response: "I recommend AF Energy and AF Build for coral growth.")
- "And how much of the first one should I add?" → **follow_up**
- "A ile tego pierwszego produktu dodać?" → **follow_up**
- "Tell me more about that one" → **follow_up**

(AI's last response: "I recommend AF Energy and AF Build for coral growth.")
- "Okay. What is the dosage for AF Build?" → **product_query** (complete question)

**Other Intent Examples:**
- "[User uploads PDF with ICP results]" → **analyze_icp**
- "I want to sell your products in my store" → **business**
- "My order hasn't arrived" → **support**
- "Where can I buy your salt in the UK?" → **purchase_inquiry**
- "Gdzie mogę kupić produkty AF w Polsce?" → **purchase_inquiry**
- "Is your salt better than Tropic Marin?" → **competitor**
- "What do you add to your salt during production?" → **censored**
- "What is the capital of Poland?" → **other**

```

## Response Metadata

- Model: gemini-2.5-flash
- Temperature: 0.3
- Response length: N/A chars
- Node execution time: N/As

---
*Generated by Aquaforest RAG Prompt Inspector*

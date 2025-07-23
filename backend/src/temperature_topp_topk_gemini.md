# <› Parametry Generowania w Google Vertex AI Gemini

## Wprowadzenie

Parametry generowania w modelach jzykowych kontroluj sposób, w jaki AI wybiera kolejne sBowa (tokeny) podczas tworzenia odpowiedzi. To kluczowe narzdzia do balansowania midzy **kreatywno[ci** a **precyzj** w systemach RAG (Retrieval-Augmented Generation).

---

## <! Temperature (Temperatura)

### Co to jest?
Temperature kontroluje **stopieD losowo[ci** w wyborze tokenów. Jest to prawdopodobnie najwa|niejszy parametr do dostrojenia.

### Jak dziaBa?
- **Temperatura = 0.0**: AI wybiera zawsze najbardziej prawdopodobny token (deterministyczne)
- **Temperatura = 1.0**: AI u|ywa naturalnego rozkBadu prawdopodobieDstwa (domy[lne)
- **Temperatura = 2.0**: AI mo|e wybiera bardzo nieprawdopodobne tokeny (bardzo kreatywne)

### Praktyczne przykBady:

**Temperature = 0.1** (Bardzo niska):
```
Pytanie: "Jaka jest stolica Polski?"
Odpowiedz: "Stolica Polski to Warszawa."
```

**Temperature = 1.0** (Domy[lna):
```
Pytanie: "Jaka jest stolica Polski?"
Odpowiedz: "Stolic Polski jest Warszawa, miasto poBo|one w [rodkowej cz[ci kraju nad WisB."
```

**Temperature = 1.8** (Wysoka):
```
Pytanie: "Jaka jest stolica Polski?"
Odpowiedz: "Warszawa, ta perBa architektury i historii, majesttycznie góruje jako stolica naszego piknego kraju..."
```

### <¯ Zalecenia dla systemu RAG:
- **0.0-0.3**: Odpowiedzi techniczne, faktyczne, medyczne
- **0.3-0.7**: **OPTYMALNE dla RAG** - balans faktów i czytelno[ci  
- **0.7-1.0**: Kreatywne pisanie, marketing
- **1.0+**: Poezja, bardzo kreatywne teksty

---

## <² Top-P (Nucleus Sampling)

### Co to jest?
Top-P wybiera tokeny na podstawie **skumulowanego prawdopodobieDstwa**. Zamiast wybiera z peBnej listy sBów, ogranicza si do grupy najbardziej prawdopodobnych tokenów.

### Jak dziaBa?
AI sumuje prawdopodobieDstwa tokenów od najwy|szego do najni|szego, a| osignie warto[ Top-P.

**PrzykBad z Top-P = 0.9:**
```
Dostpne tokeny i ich prawdopodobieDstwa:
- "jest" (0.4) 
- "to" (0.3)
- "bdzie" (0.2)   Suma = 0.9, STOP tutaj
- "mo|e" (0.05)    Te tokeny s odrzucone
- "powinno" (0.03)
- "wydaje" (0.02)
```

### Warto[ci i efekty:
- **Top-P = 0.1**: Bardzo ograniczony wybór (powtarzalne odpowiedzi)
- **Top-P = 0.95**: **DOMYZLNE Gemini** - dobry balans
- **Top-P = 1.0**: Wszystkie tokeny dostpne (maksymalna ró|norodno[)

### <¯ Zalecenia dla systemu RAG:
- **0.8-0.95**: Najlepsze dla systemów RAG
- **0.95**: Warto[ domy[lna Gemini (zalecana)

---

## =" Top-K (Top-K Sampling)

### Co to jest?
Top-K ogranicza wybór do **K najbardziej prawdopodobnych tokenów**, niezale|nie od ich prawdopodobieDstwa.

### Jak dziaBa?
**PrzykBad z Top-K = 3:**
```
Wszystkie dostpne tokeny:
1. "jest" (0.4)     TOP 3
2. "to" (0.3)       TOP 3  
3. "bdzie" (0.2)   TOP 3
4. "mo|e" (0.05)    ODRZUCONE
5. "powinno" (0.03)  ODRZUCONE
```

### Warto[ci i efekty:
- **Top-K = 1**: Zawsze najbardziej prawdopodobny token (jak Temperature = 0)
- **Top-K = 32**: Domy[lne dla niektórych modeli Gemini
- **Top-K = 40**: Dobre dla wikszo[ci zastosowaD
- **Top-K = nieograniczone**: Wszystkie tokeny dostpne

### <¯ Zalecenia dla systemu RAG:
- **Czsto niepotrzebne** - Top-P jest wystarczajce
- **32-40**: Je[li chcesz dodatkowej kontroli
- **Brak**: Pozwól Gemini u|ywa domy[lnych

---

## <â Kombinacje Parametrów dla Ró|nych ZastosowaD

### =¼ System RAG Biznesowy (Aquaforest)
```env
GEMINI_TEMPERATURE=0.3    # Faktyczne, ale czytelne odpowiedzi
GEMINI_TOP_P=0.95         # Domy[lne Gemini (zoptymalizowane)
GEMINI_TOP_K=             # Puste = domy[lne Gemini
```

**Dlaczego ta kombinacja?**
- **Temperature 0.3**: Zapewnia faktyczn dokBadno[ przy zachowaniu naturalnego jzyka
- **Top-P 0.95**: Pozwala na ró|norodno[ sBownictwa bez utraty spójno[ci
- **Top-K domy[lne**: Gemini ma zoptymalizowane ustawienia

### <¨ Kreatywne Pisanie
```env
GEMINI_TEMPERATURE=0.8
GEMINI_TOP_P=0.95
GEMINI_TOP_K=50
```

### =, Odpowiedzi Techniczne
```env
GEMINI_TEMPERATURE=0.1
GEMINI_TOP_P=0.8
GEMINI_TOP_K=20
```

### =Ú Edukacja/Wyja[nienia
```env
GEMINI_TEMPERATURE=0.5
GEMINI_TOP_P=0.9
GEMINI_TOP_K=
```

---

## >ê Jak Testowa Parametry

### 1. Zacznij od Temperature
```
Przetestuj: 0.1, 0.3, 0.5, 0.7, 1.0
OceD: Czy odpowiedzi s zbyt suche? Zbyt chaotyczne?
```

### 2. Dostosuj Top-P
```
Przetestuj: 0.8, 0.9, 0.95, 1.0
OceD: Czy sBownictwo jest wystarczajco ró|norodne?
```

### 3. Opcjonalnie Top-K
```
Przetestuj: 20, 32, 40, 60
OceD: Czy potrzebujesz dodatkowej kontroli?
```

### 4. Testuj Konsystentno[  
```
Zadaj to samo pytanie 5 razy
OceD: Czy odpowiedzi s spójne? Czy zawieraj te same fakty?
```

---

##   Najczstsze BBdy

### L Za wysoka temperatura w RAG
```env
GEMINI_TEMPERATURE=1.5  # ZAE: Mo|e generowa nieprawdziwe informacje
```

### L Za niski Top-P
```env
GEMINI_TOP_P=0.3  # ZAE: Bardzo powtarzalne, nudne odpowiedzi
```

### L Za niski Top-K z wysok temperatur
```env
GEMINI_TEMPERATURE=1.0
GEMINI_TOP_K=5  # ZAE: Ograniczona ró|norodno[ mimo wysokiej kreatywno[ci
```

### L Nadmiernie skomplikowane ustawienia
```env
# ZAE: Za du|o parametrów bez zrozumienia wpBywu
GEMINI_TEMPERATURE=0.37429
GEMINI_TOP_P=0.86234
GEMINI_TOP_K=23
```

---

## =Ê Rekomendacje Finalne dla Aquaforest RAG

### <Æ Zalecana Konfiguracja (Zoptymalizowana)
```env
# Optymalne dla systemu RAG z analiz ICP i produktami
GEMINI_TEMPERATURE=0.3    # Faktyczne + czytelne
GEMINI_TOP_P=0.95         # Domy[lne Gemini (najlepsze)
GEMINI_TOP_K=             # Puste = Gemini decyduje
```

### >ê Alternatywne Konfiguracje do Testowania

**Bardziej konserwatywna:**
```env
GEMINI_TEMPERATURE=0.2
GEMINI_TOP_P=0.9
GEMINI_TOP_K=32
```

**Bardziej kreatywna:**
```env
GEMINI_TEMPERATURE=0.5
GEMINI_TOP_P=0.95
GEMINI_TOP_K=
```

---

## = Bibliografia i Dalsze Czytanie

- [Google Cloud: Experiment with parameter values](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/adjust-parameter-values)
- [Google Cloud: Beyond temperature - Top-k and Top-p](https://medium.com/google-cloud/beyond-temperature-tuning-llm-output-with-top-k-and-top-p-24c2de5c3b16)
- [Comprehensive Guide to LLM Sampling Parameters](https://smcleod.net/2025/04/comprehensive-guide-to-llm-sampling-parameters/)
- [RAG System Parameter Optimization Best Practices](https://milvus.io/ai-quick-reference/how-might-the-decoding-parameters-of-the-llm-temperature-topk-etc-affect-the-consistency-and-quality-of-the-answers-in-a-rag-system)

---

*Dokument utworzony: StyczeD 2025*  
*Aquaforest RAG System - Optymalizacja parametrów Vertex AI Gemini*
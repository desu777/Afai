# TODO na jutro - Ulepszone Gemini 2.0 follow-up evaluation

## 🎯 **Cel:**
Ulepszyć Gemini 2.0 w `follow_up_evaluator` żeby miał pełny kontekst produktowy i mógł precyzyjnie określić czego brakuje do odpowiedzenia na follow-up pytanie.

## 🔍 **Gemini 2.0 będzie analizować:**

1. **Missing products**: "User pyta o NitraPhos Minus, ale nie ma go w cache"
2. **New problems**: "User wspomniał o nowym problemie (cyano) niezwiązanym z poprzednim (kH)"
3. **Missing tests**: "User chce testy nitratów/fosforanów, ale cache nie ma test kitów"
4. **Dosage questions**: "User pyta o dawkowanie, ale cache nie ma szczegółów dozowania"
5. **Product comparisons**: "User porównuje produkty których nie ma w cache"

## 🚀 **Implementacja:**

### **1. Załadować products_turbo.json do follow_up_evaluator**
```python
def __init__(self):
    self.products_data = self._load_products_turbo()
    
def _load_products_turbo(self):
    with open('data/products_turbo.json') as f:
        return json.load(f)
```

### **2. Nowy prompt w stylu response_followup_cache.txt**
- MISSION & PERSONA
- CONTEXTUAL DATA (cache + user query + products list)
- ANALYTICAL FRAMEWORK
- DECISION SCHEMA

### **3. Nowy schemat odpowiedzi JSON**
```json
{
    "sufficient": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "detailed analysis",
    "missing_products": ["NitraPhos Minus", "Nitrate Test Kit"],
    "new_problems": ["cyanobacteria"],
    "missing_categories": ["test_kits"],
    "specific_needs": ["dosage_info", "comparison_data"]
}
```

## 📋 **Pliki do modyfikacji:**

1. **`follow_up_evaluator.py`** - załadować products_turbo.json + nowy prompt
2. **Nowy prompt** - w stylu response_followup_cache.txt ale dla evaluation
3. **`workflow.py`** - obsługa nowego schematu odpowiedzi

## 🎨 **Korzyści:**
- Nie obciążamy business reasonera
- Precyzyjne określenie czego brakuje
- Gemini 2.0 ma pełny kontekst produktowy
- Strukturalne podejście do brakujących danych

## 📝 **Notatki:**
- Dzisiaj naprawiliśmy cache metadata limits i TypeError
- Cache teraz przechowuje WSZYSTKIE metadane z Pinecone + user_query + model responses
- Jutro robimy inteligentniejsze follow-up evaluation
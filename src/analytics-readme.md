# Aquaforest RAG Analytics Integration

## 🚀 Nowe funkcjonalności

### 1. **Baza danych SQLite** (`aquaforest_analytics.db`)
- Automatycznie tworzona przy pierwszym uruchomieniu
- Dwie tabele:
  - `feedback` - przechowuje oceny i komentarze użytkowników
  - `analyze` - szczegółowa analiza każdego zapytania

### 2. **Automatyczna analiza workflow**
Każde zapytanie jest analizowane i zapisywane:
- Query użytkownika
- Decyzje Intent Detectora
- Poprawki Business Reasonera
- Zapytania Query Optimizera
- Wyniki Pinecone
- Decyzje filtrowania
- Confidence score i reasoning
- Czasy wykonania każdego node'a
- Ostateczna odpowiedź

### 3. **API Endpoints**

#### Feedback
- `POST /feedback` - przesyłanie feedbacku
- `GET /feedback/summary` - podsumowanie feedbacków

#### Analytics
- `POST /analytics/query` - pobieranie danych analitycznych
- `GET /analytics/summary` - statystyki zbiorcze

## 📝 Jak używać

### 1. Uruchom serwer
```bash
cd src
python server.py
```

### 2. Frontend - dodaj przycisk feedback
W komponencie `Message.tsx` możesz dodać przycisk do oceny:

```typescript
const handleFeedback = async (rating: number) => {
  const response = await fetch('http://localhost:2103/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_query: message.content,
      response: aiResponse,
      rating: rating,
      user_type: accessLevel // 'test' lub 'admin'
    })
  });
};
```

### 3. Dashboard analityczny (dla admina)
Możesz stworzyć komponent do wyświetlania statystyk:

```typescript
// Pobierz podsumowanie
const summary = await fetch('http://localhost:2103/analytics/summary');

// Pobierz szczegółowe dane
const analytics = await fetch('http://localhost:2103/analytics/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ limit: 100 })
});
```

## 🧪 Testowanie

Użyj dostarczonego skryptu testowego:
```bash
python test_api.py
```

## 📊 Co jest śledzone

### Dla każdego zapytania:
1. **Intent Detection**
   - Wykryty intent (product_query, follow_up, etc.)
   - Język zapytania
   - Confidence score

2. **Business Reasoning**
   - Interpretacja biznesowa
   - Poprawki nazw produktów
   - Wykryte kategorie/problemy

3. **Query Optimization**
   - Lista zoptymalizowanych zapytań do Pinecone

4. **Search Results**
   - Liczba wyników z Pinecone
   - Top 3 produkty z score
   - Decyzje filtrowania

5. **Confidence & Response**
   - Końcowy confidence score
   - Reasoning dla confidence
   - Czy eskalowano do supportu
   - Ostateczna odpowiedź

6. **Performance**
   - Czas wykonania każdego node'a
   - Całkowity czas wykonania

## 🔍 Przykładowe zapytania SQL

### Znajdź najwolniejsze zapytania:
```sql
SELECT user_query, total_execution_time, created_at
FROM analyze
ORDER BY total_execution_time DESC
LIMIT 10;
```

### Sprawdź rozkład intencji:
```sql
SELECT intent_detector_decision, COUNT(*) as count
FROM analyze
GROUP BY intent_detector_decision;
```

### Znajdź zapytania z niską confidence:
```sql
SELECT user_query, confidence_score, confidence_reasoning
FROM analyze
WHERE confidence_score < 0.5
ORDER BY created_at DESC;
```

### Średni rating per język:
```sql
SELECT a.detected_language, AVG(f.rating) as avg_rating
FROM analyze a
JOIN feedback f ON a.user_query = f.user_query
GROUP BY a.detected_language;
```

## 🛠️ Rozbudowa

### Dodatkowe metryki
W `WorkflowAnalytics.capture_state_data()` możesz dodać:
- Liczba produktów w cache
- Wykryte domeny (freshwater/marine)
- Liczba kroków w konwersacji
- Typy content (product/knowledge/usage)

### Webhook dla feedbacku
Możesz dodać webhook do powiadamiania o negatywnych ocenach:
```python
if feedback.rating <= 2:
    send_alert_to_slack(feedback)
```

### Export do CSV
Dodaj endpoint do eksportu analityk:
```python
@app.get("/analytics/export")
async def export_analytics():
    # Export to CSV
```

## 🔒 Bezpieczeństwo

- Baza SQLite jest lokalna
- Nie przechowujemy danych osobowych
- Feedback jest anonimowy (tylko typ użytkownika)
- Możesz dodać czyszczenie starych danych:

```python
# Usuń dane starsze niż 90 dni
DELETE FROM analyze WHERE created_at < datetime('now', '-90 days');
```

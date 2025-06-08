"""
Response Formatting Module
Formats final response with proper language and structure
"""
from typing import List, Dict, Any
from openai import OpenAI
from models import ConversationState, ProductInfo
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

class ResponseFormatter:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        self.response_templates = {
            'pl': {
                'greeting': "Cześć! 👋 Jestem AF AI - asystentem firmy Aquaforest! W czym mogę Ci pomóc?",
                'business': """Cześć! Bardzo dziękujemy za zainteresowanie współpracą z nami, jesteśmy bardzo szczęśliwi! 🎉

Proszę wypełnić formularz kontaktowy:
https://aquaforest.eu/pl/kontakt/

Lub skontaktuj się bezpośrednio:
📧 info@aquaforest.eu
📞 +48 14 691 79 79""",
                'competitor': "Kto to jest? 😉",
                'censored': "Przepraszam, ale informacje o metodach produkcyjnych i składnikach są objęte tajemnicą firmową. Mogę za to opowiedzieć o działaniu i zastosowaniu naszych produktów!",
                'product_header': "Na podstawie Twojego pytania polecam:",
                'dosage_header': "Dawkowanie:",
                'compatible_header': "Kompatybilne produkty:",
                'more_info': "Więcej informacji:",
                'low_confidence': "Znalazłem kilka produktów, które mogą pomóc:",
                'escalation': "Przepraszam, nie jestem pewien najlepszej odpowiedzi. Skontaktuj się z naszym supportem: support@aquaforest.eu",
                'domain_warning': "⚠️ Znalazłem produkty dla akwarium morskiego i słodkowodnego. Proszę sprecyzuj rodzaj akwarium!"
            },
            'en': {
                'greeting': "Hello! 👋 I'm AF AI - the Aquaforest assistant! How can I help you?",
                'business': """Hello! Thank you very much for your interest in partnering with us, we are very happy! 🎉

Please fill out the contact form:
https://aquaforest.eu/en/contact-us/

Or contact us directly:
📧 info@aquaforest.eu
📞 +48 14 691 79 79""",
                'competitor': "Who's that? 😉",
                'censored': "I apologize, but information about production methods and ingredients is proprietary. However, I'd be happy to tell you about how our products work and their applications!",
                'product_header': "Based on your query, I recommend:",
                'dosage_header': "Dosage:",
                'compatible_header': "Compatible products:",
                'more_info': "More information:",
                'low_confidence': "I found several products that might help:",
                'escalation': "I'm not certain about the best answer. Please contact our support: support@aquaforest.eu",
                'domain_warning': "⚠️ Found products for both marine and freshwater aquariums. Please specify which type!"
            },
            'de': {
                'greeting': "Hallo! 👋 Ich bin AF AI - der Aquaforest-Assistent! Wie kann ich Ihnen helfen?",
                'business': """Hallo! Vielen Dank für Ihr Interesse an einer Partnerschaft mit uns, wir freuen uns sehr! 🎉

Bitte füllen Sie das Kontaktformular aus:
https://aquaforest.eu/en/contact-us/

Oder kontaktieren Sie uns direkt:
📧 info@aquaforest.eu
📞 +48 14 691 79 79""",
                'competitor': "Wer ist das? 😉",
                'censored': "Es tut mir leid, aber Informationen über Produktionsmethoden und Inhaltsstoffe sind vertraulich. Ich kann Ihnen jedoch gerne erklären, wie unsere Produkte funktionieren!",
                'product_header': "Basierend auf Ihrer Anfrage empfehle ich:",
                'dosage_header': "Dosierung:",
                'compatible_header': "Kompatible Produkte:",
                'more_info': "Weitere Informationen:",
                'low_confidence': "Ich habe mehrere Produkte gefunden, die helfen könnten:",
                'escalation': "Ich bin mir nicht sicher. Bitte kontaktieren Sie unseren Support: support@aquaforest.eu",
                'domain_warning': "⚠️ Produkte für Meerwasser- und Süßwasseraquarien gefunden. Bitte spezifizieren Sie!"
            }
        }
        
    def _format_dosage(self, product: Dict, language: str) -> str:
        """Format dosage information"""
        meta = product['metadata']
        dosage_parts = []
        
        if meta.get('dosage_amount'):
            dosage_parts.append(meta['dosage_amount'])
        if meta.get('dosage_volume'):
            if language == 'pl':
                dosage_parts.append(f"na {meta['dosage_volume']}")
            else:
                dosage_parts.append(f"per {meta['dosage_volume']}")
        if meta.get('dosage_frequency'):
            freq_text = meta['dosage_frequency'].replace('_', ' ')
            dosage_parts.append(freq_text)
            
        return ' '.join(dosage_parts) if dosage_parts else None
    
    def _get_product_url(self, product: Dict, language: str) -> str:
        """Get appropriate URL based on language"""
        meta = product['metadata']
        if language == 'pl' and meta.get('url_pl'):
            return meta['url_pl']
        return meta.get('url_en', '')
    
    def _create_formatting_prompt(self, state: ConversationState) -> str:
        """Create prompt for LLM-based formatting"""
        results = state["search_results"][:10]  # Top 5 results for context
        
        results_info = []
        for p in results:
            meta = p['metadata']
            results_info.append(f"""
Result: {meta.get('product_name', 'Unknown')}
Content Type: {meta.get('content_type', 'unknown')}
Description: {meta.get('full_content_en', '')[:200]}...
Score: {p['score']:.3f}
""")
        
        lang = state["detected_language"]
        template = self.response_templates.get(lang, self.response_templates['en'])
        
        return f"""
You are an expert Aquaforest assistant formatting a response.

User Query: "{state['original_query']}"
User Language: {lang}

Search Results Found:
{''.join(results_info)}

TASK:
1. Create a helpful, natural response in {lang}.
2. If you find relevant results with `Content Type: "product"`, recommend 1-3 of them.
3. Explain WHY these products solve the user's problem.
4. If you find a relevant `Content Type: "article"`, you can cite it as a helpful resource, but do NOT present it as a product.
5. Include key dosage information for recommended products.
6. Be conversational and professional.

RULES:
- ONLY recommend items where `Content Type` is `product`.
- Use **bold** for product names.
- Do not recommend articles, guides, or other non-product content as if they are products for sale.
- If you cite an article, mention it as a helpful guide or source of information.
- If no relevant products are found, explain that and offer general advice if possible.

Template phrases to use:
- Product header: "{template['product_header']}"
- Dosage header: "{template['dosage_header']}"
- More info: "{template['more_info']}"
"""
    
    def format_response(self, state: ConversationState) -> ConversationState:
        """Format the final response"""
        lang = state["detected_language"]
        # Default to English for unsupported languages
        if lang not in self.response_templates:
            lang = 'en'
        templates = self.response_templates[lang]
        
        # Handle different intents
        if state["intent"] == "greeting":
            state["final_response"] = templates['greeting']
            return state
        
        if state["intent"] == "business":
            state["final_response"] = templates['business']
            return state
            
        if state["intent"] == "competitor":
            state["final_response"] = templates['competitor']
            return state
            
        if state["intent"] == "censored":
            state["final_response"] = templates['censored']
            return state
        
        # Handle domain warning
        if state.get("domain_warning"):
            state["final_response"] = templates['domain_warning']
            return state
        
        # Handle low confidence / escalation
        if state["confidence"] < 0.5 or state.get("escalate"):
            state["final_response"] = templates['escalation']
            return state
        
        # Format product recommendations
        try:
            # Filter for actual products from the search results
            product_results = [
                p for p in state["search_results"]
                if p.get('metadata', {}).get('content_type') == 'product'
            ]

            if state["confidence"] >= 0.7 and product_results:
                # High confidence & products found - direct formatting
                response_parts = [templates['product_header'], "\n"]
                
                for product in product_results[:3]:
                    meta = product['metadata']
                    
                    # Product name and description
                    response_parts.append(f"\n**{meta.get('product_name', 'Unknown')}**")
                    
                    # Get appropriate description
                    if lang == 'pl' and meta.get('title_pl'):
                        response_parts.append(f"- {meta['title_pl']}")
                    else:
                        response_parts.append(f"- {meta.get('title_en', '')}")
                    
                    # Dosage
                    dosage = self._format_dosage(product, lang)
                    if dosage:
                        response_parts.append(f"\n{templates['dosage_header']} {dosage}")
                    
                    # URL
                    url = self._get_product_url(product, lang)
                    if url:
                        response_parts.append(f"\n[{templates['more_info']}]({url})")
                    
                    response_parts.append("\n")
                
                # Compatible products
                compatible = set()
                for p in product_results[:3]:
                    compatible.update(p['metadata'].get('compatible_products', []))
                
                if compatible:
                    response_parts.append(f"\n{templates['compatible_header']} {', '.join(compatible)}")
                
                state["final_response"] = '\n'.join(response_parts)
                
            else:
                # Medium confidence or no products found - use LLM for better formatting
                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    temperature=OPENAI_TEMPERATURE,
                    messages=[
                        {
                            "role": "system",
                            "content": self._create_formatting_prompt(state)
                        }
                    ]
                )
                state["final_response"] = response.choices[0].message.content
                
        except Exception as e:
            print(f"Formatting error: {e}")
            state["final_response"] = templates['escalation']
            
        return state

def format_final_response(state: ConversationState) -> ConversationState:
    """Node function for LangGraph"""
    formatter = ResponseFormatter()
    return formatter.format_response(state)

def add_llm_knowledge(state: ConversationState) -> ConversationState:
    """Add LLM knowledge when confidence is medium"""
    formatter = ResponseFormatter()
    
    # First format based on search results
    state = formatter.format_response(state)
    
    # Then enhance with LLM knowledge
    enhancement_prompt = f"""
The search found these products: {[r['metadata']['product_name'] for r in state['search_results'][:3]]}

But confidence is medium ({state['confidence']:.2f}). 

Add helpful general advice about the problem mentioned in the query: "{state['original_query']}"

Keep the product recommendations but add:
1. General tips for this type of problem
2. What to monitor/test
3. Prevention tips

Keep it concise and in {state['detected_language']} language.
Current response to enhance:
{state['final_response']}
"""
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            messages=[
                {"role": "system", "content": enhancement_prompt}
            ]
        )
        state["final_response"] = response.choices[0].message.content
    except Exception as e:
        print(f"Enhancement error: {e}")
        
    return state

def escalate_to_human(state: ConversationState) -> ConversationState:
    """Escalate to human support"""
    state["escalate"] = True
    formatter = ResponseFormatter()
    return formatter.format_response(state)
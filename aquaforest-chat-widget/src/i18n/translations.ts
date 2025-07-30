import type { SupportedLanguage } from '../utils/detectLanguage';

export interface Translation {
  welcome: {
    title: string;
    subtitle: string;
    button: string;
    footer: string;
  };
  greeting: string;
  input: {
    placeholder: string;
  };
}

export const translations: Record<SupportedLanguage, Translation> = {
  pl: {
    welcome: {
      title: "Cześć, jestem Afai",
      subtitle: "Mądrość z serca rafy...",
      button: "Zapytaj mnie o swoją rafę",
      footer: "Afai by Aquaforest"
    },
    greeting: "Cześć! Jestem Afai – Twój asystent AI do spraw akwarystyki.\nJak mogę Ci dziś pomóc? Możesz zadawać mi pytania dotyczące prowadzenia akwarium, przesyłać wyniki testów ICP do analizy lub zdjęcia w celu identyfikacji szkodników i chorób.\nPamiętaj, że każde akwarium jest inne – dlatego tak ważna jest uważna obserwacja zmian zachodzących w Twoim zbiorniku.\nJestem w fazie beta i należysz do grona pierwszych osób, które mnie testują. Dziękuję za cierpliwość wobec moich niedoskonałości i zachęcam do dzielenia się opinią – Twoje uwagi pomogą mi się rozwijać!",
    input: {
      placeholder: "Wpisz swoją wiadomość..."
    }
  },
  en: {
    welcome: {
      title: "Hi, I'm Afai",
      subtitle: "Wisdom from the reef's heart...",
      button: "Ask me about your reef",
      footer: "Afai by Aquaforest"
    },
    greeting: "Hi! I'm Afai – your AI assistant for aquarium-related topics.\nHow can I help you today? You can ask me questions about aquarium care, upload ICP test results for analysis, or share pictures to help identify pests or diseases.\nPlease remember that every aquarium is unique, so it's essential to carefully monitor any changes in your tank.\nI'm currently in beta testing, and you're one of the very first people to try me out. Thanks for your patience with my imperfections, and feel free to share your feedback – it will help me grow and improve!",
    input: {
      placeholder: "Type your message..."
    }
  }
};
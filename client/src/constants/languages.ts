export interface LanguageOption {
  value: string;
  label: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { value: 'Spanish', label: 'Spanish (Español)' },
  { value: 'French', label: 'French (Français)' },
  { value: 'German', label: 'German (Deutsch)' },
  { value: 'Italian', label: 'Italian (Italiano)' },
  { value: 'Portuguese', label: 'Portuguese (Português)' },
  { value: 'Japanese', label: 'Japanese (日本語)' },
  { value: 'Korean', label: 'Korean (한국어)' },
  { value: 'Chinese', label: 'Chinese Simplified (简体中文)' },
  { value: 'Russian', label: 'Russian (Русский)' },
  { value: 'Arabic', label: 'Arabic (العربية)' },
  { value: 'Hindi', label: 'Hindi (हिन्दी)' },
  { value: 'Dutch', label: 'Dutch (Nederlands)' },
  { value: 'Swedish', label: 'Swedish (Svenska)' },
  { value: 'Norwegian', label: 'Norwegian (Norsk)' },
  { value: 'Danish', label: 'Danish (Dansk)' },
  { value: 'Finnish', label: 'Finnish (Suomi)' },
  { value: 'Polish', label: 'Polish (Polski)' },
  { value: 'Turkish', label: 'Turkish (Türkçe)' },
  { value: 'Greek', label: 'Greek (Ελληνικά)' },
  { value: 'Hebrew', label: 'Hebrew (עברית)' }
];

export const DEFAULT_LANGUAGE = 'Chinese'; 
export type SecondaryLanguage =
  | ''
  | 'hi'
  | 'te'
  | 'ta'
  | 'kn'
  | 'ml'
  | 'mr'
  | 'gu'
  | 'bn'
  | 'pa'
  | 'or'
  | 'as'
  | 'ur'
  | 'sa'
  | 'ne'
  | 'ar'
  | 'es'
  | 'fr'
  | 'de'
  | 'pt'
  | 'zh'
  | 'ja'
  | 'ko'
  | 'ru'
  | 'id'
  | 'vi'

export interface SchoolSettings {
  school_id: number
  school_slug: string
  school_name: string
  logo_url: string | null
  tagline: string
  introduction: string
  secondary_language: SecondaryLanguage
  introduction_secondary: string
  footer_text: string
  updated_at: string
}

export interface SchoolSummary {
  id: number
  name: string
  slug: string
  domain: string
  logo_url: string | null
}


export interface CourseClass {
  id: number
  name: string
  display_order: number
  aim: string
  conditions: string
  curriculum: string
  aim_secondary: string
  conditions_secondary: string
  curriculum_secondary: string
}

export interface Course {
  id: number
  title: string
  summary: string
  display_order: number
  display_language: 'en' | 'secondary'
  classes: CourseClass[]
}

export interface HomepageContent {
  school: SchoolSettings
  courses: Course[]
}

export const SECONDARY_LANGUAGE_LABELS: Record<Exclude<SecondaryLanguage, ''>, string> = {
  hi: 'Hindi',
  te: 'Telugu',
  ta: 'Tamil',
  kn: 'Kannada',
  ml: 'Malayalam',
  mr: 'Marathi',
  gu: 'Gujarati',
  bn: 'Bengali',
  pa: 'Punjabi',
  or: 'Odia',
  as: 'Assamese',
  ur: 'Urdu',
  sa: 'Sanskrit',
  ne: 'Nepali',
  ar: 'Arabic',
  es: 'Spanish',
  fr: 'French',
  de: 'German',
  pt: 'Portuguese',
  zh: 'Chinese',
  ja: 'Japanese',
  ko: 'Korean',
  ru: 'Russian',
  id: 'Indonesian',
  vi: 'Vietnamese',
}

export const INTRODUCTION_HEADERS: Record<SecondaryLanguage | 'en', string> = {
  en: 'Introduction',
  '': 'Introduction',
  hi: 'परिचय',
  te: 'పరిచయము',
  ta: 'அறிமுகம்',
  kn: 'ಪರಿಚಯ',
  ml: 'പരിചയം',
  mr: 'परिचय',
  gu: 'પરિચય',
  bn: 'পরিচয়',
  pa: 'ਜਾਣ-ਪਛਾਣ',
  or: 'ପରିଚୟ',
  as: 'পৰিচয়',
  ur: 'تعارف',
  sa: 'परिचयः',
  ne: 'परिचय',
  ar: 'مقدمة',
  es: 'Introducción',
  fr: 'Introduction',
  de: 'Einführung',
  pt: 'Introdução',
  zh: '简介',
  ja: '紹介',
  ko: '소개',
  ru: 'Введение',
  id: 'Pengenalan',
  vi: 'Giới thiệu',
}

export const CLASS_SECTION_HEADERS: Record<
  SecondaryLanguage | 'en',
  { aim: string; conditions: string; curriculum: string }
> = {
  en: { aim: 'Aim', conditions: 'Conditions', curriculum: 'Curriculum' },
  '': { aim: 'Aim', conditions: 'Conditions', curriculum: 'Curriculum' },
  hi: { aim: 'लक्ष्य', conditions: 'नियम', curriculum: 'पाठ्यक्रम' },
  te: { aim: 'లక్ష్యములు', conditions: 'నియమములు', curriculum: 'పాఠ్యాంశాలు' },
  ta: { aim: 'இலக்குகள்', conditions: 'விதிகள்', curriculum: 'பாடத்திட்டம்' },
  kn: { aim: 'ಗುರಿಗಳು', conditions: 'ನಿಯಮಗಳು', curriculum: 'ಪಠ್ಯಕ್ರಮ' },
  ml: { aim: 'ലക്ഷ്യങ്ങൾ', conditions: 'നിയമങ്ങൾ', curriculum: 'പാഠ്യപദ്ധതി' },
  mr: { aim: 'उद्दिष्टे', conditions: 'नियम', curriculum: 'अभ्यासक्रम' },
  gu: { aim: 'લક્ષ્યો', conditions: 'નિયમો', curriculum: 'અભ્યાસક્રમ' },
  bn: { aim: 'লক্ষ্য', conditions: 'নিয়ম', curriculum: 'পাঠ্যক্রম' },
  pa: { aim: 'ਟੀਚੇ', conditions: 'ਨਿਯਮ', curriculum: 'ਪਾਠਕ੍ਰਮ' },
  or: { aim: 'ଲକ୍ଷ୍ୟ', conditions: 'ନିୟମ', curriculum: 'ପାଠ୍ୟକ୍ରମ' },
  as: { aim: 'লক্ষ্য', conditions: 'নিয়ম', curriculum: 'পাঠ্যক্ରম' },
  ur: { aim: 'اہداف', conditions: 'قواعد', curriculum: 'نصاب' },
  sa: { aim: 'लक्ष्याणि', conditions: 'नियमाः', curriculum: 'पाठ्यक्रमः' },
  ne: { aim: 'लक्ष्यहरू', conditions: 'नियमहरू', curriculum: 'पाठ्यक्रम' },
  ar: { aim: 'الأهداف', conditions: 'الشروط', curriculum: 'المنهج' },
  es: { aim: 'Objetivos', conditions: 'Condiciones', curriculum: 'Currículo' },
  fr: { aim: 'Objectifs', conditions: 'Conditions', curriculum: 'Programme' },
  de: { aim: 'Ziele', conditions: 'Bedingungen', curriculum: 'Lehrplan' },
  pt: { aim: 'Objetivos', conditions: 'Condições', curriculum: 'Currículo' },
  zh: { aim: '目标', conditions: '条件', curriculum: '课程' },
  ja: { aim: '目標', conditions: '条件', curriculum: 'カリキュラム' },
  ko: { aim: '목표', conditions: '조건', curriculum: '교육과정' },
  ru: { aim: 'Цели', conditions: 'Условия', curriculum: 'Учебный план' },
  id: { aim: 'Tujuan', conditions: 'Ketentuan', curriculum: 'Kurikulum' },
  vi: { aim: 'Mục tiêu', conditions: 'Điều kiện', curriculum: 'Chương trình' },
}
export function scriptClassForLanguage(language: SecondaryLanguage): string {
  switch (language) {
    case 'te':
      return 'script-telugu'
    case 'kn':
      return 'script-kannada'
    case 'ta':
      return 'script-tamil'
    case 'ml':
      return 'script-malayalam'
    case 'gu':
      return 'script-gujarati'
    case 'bn':
    case 'as':
      return 'script-bengali'
    case 'pa':
      return 'script-gurmukhi'
    case 'or':
      return 'script-odia'
    case 'hi':
    case 'mr':
    case 'sa':
    case 'ne':
      return 'script-devanagari'
    case 'ur':
    case 'ar':
      return 'script-arabic'
    case 'zh':
      return 'script-chinese'
    case 'ja':
      return 'script-japanese'
    case 'ko':
      return 'script-korean'
    case 'ru':
      return 'script-cyrillic'
    default:
      return 'script-latin'
  }
}

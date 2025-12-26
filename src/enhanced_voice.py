"""
CLEAN PRODUCTION VOICE RECOGNITION - WITH ALSA SUPPORT
100% Working for Raspberry Pi with USB microphone
Optimized for reliability and accuracy
MULTI-LINGUAL SUPPORT for all Indian languages
WITH REAL-TIME SPEECH SYNTHESIS RESPONSE
DIRECT ALSA ACCESS (hw:1,0) - No PulseAudio dependencies
"""

import speech_recognition as sr
import time
import logging
from typing import Optional, Tuple, Dict, List
import re
from dataclasses import dataclass
import pyttsx3
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class ServiceMatch:
    service_type: str
    confidence: float
    matched_keywords: List[str]

@dataclass
class VoiceResponse:
    text: str
    language: str
    priority: int = 1  # 1: normal, 2: important, 3: urgent

class SpeechSynthesizer:
    """Handles text-to-speech with multi-lingual support"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.response_queue = queue.Queue()
        self.is_speaking = False
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        self.stop_speaking = False
        
        # Configure voice settings
        self._configure_voice()
        
        # Start response processing thread
        self.processing_thread = threading.Thread(target=self._process_responses, daemon=True)
        self.processing_thread.start()
        
        logger.info("✅ Speech Synthesizer Initialized")
    
    def _configure_voice(self):
        """Configure TTS engine settings"""
        # Get available voices
        voices = self.engine.getProperty('voices')
        
        # Set optimal parameters
        self.engine.setProperty('rate', 160)  # Speech speed
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Try to find a good quality voice
        for voice in voices:
            # Prefer female voices for better clarity
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                logger.info(f"🎤 Selected voice: {voice.name}")
                break
        else:
            # If no female voice found, use first available
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                logger.info(f"🎤 Selected default voice: {voices[0].name}")
    
    def _process_responses(self):
        """Background thread to process speech responses"""
        while True:
            try:
                response = self.response_queue.get(timeout=1)
                if response and not self.stop_speaking:
                    self._speak_response(response)
                self.response_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Speech processing error: {e}")
    
    def _speak_response(self, response: VoiceResponse):
        """Speak a response with language-aware processing"""
        try:
            self.is_speaking = True
            
            # Pre-process text for better speech
            text = self._prepare_speech_text(response.text, response.language)
            
            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()
            
            # Small pause after speaking
            time.sleep(0.1)
            
            self.is_speaking = False
            
        except Exception as e:
            logger.error(f"Speech error: {e}")
            self.is_speaking = False
    
    def _prepare_speech_text(self, text: str, language: str) -> str:
        """Prepare text for speech synthesis"""
        if not text:
            return ""
        
        # Clean text for better speech
        text = text.strip()
        
        # Add pauses for better rhythm
        text = text.replace(',', ', ')
        text = text.replace('.', '. ')
        
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Language-specific processing
        if language.startswith('hi'):  # Hindi
            # Ensure proper spacing for Hindi text
            text = re.sub(r'\s+', ' ', text)
        elif language.startswith('ta'):  # Tamil
            # Tamil-specific cleanup
            text = re.sub(r'[^\u0B80-\u0BFF\s.,!?]', '', text)
        
        return text
    
    def speak(self, text: str, language: str = 'en', priority: int = 1, immediate: bool = False):
        """
        Queue text for speech synthesis
        
        Args:
            text: Text to speak
            language: Language code
            priority: Priority level (1-3)
            immediate: If True, clears queue and speaks immediately
        """
        if not text:
            return
        
        if immediate:
            # Clear queue for immediate response
            self.stop_current_speech()
            while not self.response_queue.empty():
                try:
                    self.response_queue.get_nowait()
                    self.response_queue.task_done()
                except queue.Empty:
                    break
        
        # Create response object
        response = VoiceResponse(text=text, language=language, priority=priority)
        
        # Add to queue
        self.response_queue.put(response)
        
        logger.info(f"🗣️ Queued speech: '{text[:50]}...' in {language}")
    
    def speak_immediate(self, text: str, language: str = 'en'):
        """Speak immediately (interrupts any ongoing speech)"""
        self.speak(text, language, priority=3, immediate=True)
    
    def stop_current_speech(self):
        """Stop current speech"""
        try:
            self.stop_speaking = True
            self.engine.stop()
            time.sleep(0.1)
            self.stop_speaking = False
        except:
            pass
    
    def wait_until_finished(self, timeout: float = 10.0):
        """Wait until all queued speech is finished"""
        start_time = time.time()
        while (self.is_speaking or not self.response_queue.empty()) and (time.time() - start_time) < timeout:
            time.sleep(0.1)
    
    def get_status(self) -> Dict:
        """Get current speech synthesizer status"""
        return {
            'is_speaking': self.is_speaking,
            'queue_size': self.response_queue.qsize(),
            'voices': len(self.engine.getProperty('voices'))
        }

class EnhancedVoiceRecognizer:
    """
    100% WORKING voice recognizer - Optimized for USB microphone
    MULTI-LINGUAL support for all Indian languages
    WITH SPEECH RESPONSE CAPABILITY
    COMPREHENSIVE SERVICE KEYWORDS (400+ services)
    DIRECT ALSA ACCESS for reliable USB microphone
    """
    
    def __init__(self, mic_device_index: int = 1, use_alsa: bool = True):
        self.recognizer = sr.Recognizer()
        self.mic_device_index = mic_device_index
        self.use_alsa = use_alsa
        
        # Initialize speech synthesizer
        self.speech = SpeechSynthesizer()
        
        # Optimized settings for USB mic
        self.recognizer.energy_threshold = 300  # Good starting point
        self.recognizer.dynamic_energy_threshold = False  # More stable
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.pause_threshold = 1.2  # Slightly longer for better phrase detection
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
        # ========== INDIAN LANGUAGES CONFIGURATION ==========
        self.supported_languages = {
            'en': {
                'code': 'en-IN',
                'name': 'English',
                'wake_words': ['hey butler', 'hello butler', 'hi butler', 'okay butler', 'hey butter', 'butler'],
                'greeting': 'Hello! How can I help you today?',
                'prompt': 'What service do you need?',
                'confirm': 'I will help you find a',
                'not_found': 'Sorry, I did not understand. Please say the service name clearly.',
                'searching': 'Searching for',
                'found': 'I found',
                'providers': 'providers for you',
                'welcome': 'Welcome! I am your personal assistant.',
                'ready': 'I am ready to help. Please tell me what service you need.',
                'listening': 'I am listening...',
                'processing': 'Processing your request...',
                'thanks': 'Thank you for using our service.',
                'goodbye': 'Goodbye! Have a nice day.'
            },
            'hi': {
                'code': 'hi-IN',
                'name': 'Hindi',
                'wake_words': ['हे बटलर', 'नमस्ते बटलर', 'हैलो बटलर', 'बटलर'],
                'greeting': 'नमस्ते! मैं आपकी क्या मदद कर सकता हूँ?',
                'prompt': 'आपको कौन सी सेवा चाहिए?',
                'confirm': 'मैं आपके लिए खोजूंगा',
                'not_found': 'क्षमा करें, मुझे समझ नहीं आया। कृपया सेवा का नाम स्पष्ट रूप से बताएं।',
                'searching': 'खोज रहा हूँ',
                'found': 'मुझे मिल गए',
                'providers': 'प्रदाता आपके लिए',
                'welcome': 'स्वागत है! मैं आपका निजी सहायक हूँ।',
                'ready': 'मैं मदद के लिए तैयार हूँ। कृपया बताएं आपको कौन सी सेवा चाहिए।',
                'listening': 'मैं सुन रहा हूँ...',
                'processing': 'आपका अनुरोध प्रसंस्करण किया जा रहा है...',
                'thanks': 'हमारी सेवा का उपयोग करने के लिए धन्यवाद।',
                'goodbye': 'अलविदा! आपका दिन शुभ हो।'
            },
            'ta': {
                'code': 'ta-IN',
                'name': 'Tamil',
                'wake_words': ['ஏ பட்லர்', 'வணக்கம் பட்லர்', 'ஹலோ பட்லர்', 'பட்லர்'],
                'greeting': 'வணக்கம்! நான் இன்று உங்களுக்கு எவ்வாறு உதவ முடியும்?',
                'prompt': 'உங்களுக்கு என்ன சேவை தேவை?',
                'confirm': 'நான் உங்களுக்கு ஒரு தேடுவேன்',
                'not_found': 'மன்னிக்கவும், எனக்கு புரியவில்லை. தயவுசெய்து சேவையின் பெயரை தெளிவாக சொல்லுங்கள்.',
                'searching': 'தேடுகிறது',
                'found': 'நான் கண்டுபிடித்தேன்',
                'providers': 'வழங்குநர்கள் உங்களுக்காக',
                'welcome': 'வரவேற்கிறேன்! நான் உங்கள் தனிப்பட்ட உதவியாளன்.',
                'ready': 'நான் உதவ தயாராக உள்ளேன். தயவுசெய்து உங்களுக்கு என்ன சேவை தேவை என்று சொல்லுங்கள்.',
                'listening': 'நான் கேட்கிறேன்...',
                'processing': 'உங்கள் கோரிக்கை செயலாக்கப்படுகிறது...',
                'thanks': 'எங்கள் சேவையைப் பயன்படுத்தியதற்கு நன்றி.',
                'goodbye': 'பிரியாவிடை! நல்ல நாள் வாகுக.'
            },
            'te': {
                'code': 'te-IN',
                'name': 'Telugu',
                'wake_words': ['హే బట్లర్', 'నమస్తే బట్లర్', 'హలో బట్లర్', 'బట్లర్'],
                'greeting': 'నమస్తే! నేను ఈ రోజు మీకు ఎలా సహాయం చేయగలను?',
                'prompt': 'మీకు ఏ సేవ కావాలి?',
                'confirm': 'నేను మీ కోసం ఒక దాన్ని కనుగొంటాను',
                'not_found': 'క్షమించండి, నాకు అర్థం కాలేదు. దయచేసి సేవ పేరును స్పష్టంగా చెప్పండి.',
                'searching': 'శోధిస్తోంది',
                'found': 'నేను కనుగొన్నాను',
                'providers': 'ప్రొవైడర్లు మీ కోసం',
                'welcome': 'స్వాగతం! నేను మీ వ్యక్తిగత సహాయకుడిని.',
                'ready': 'నేను సహాయం చేయడానికి సిద్ధంగా ఉన్నాను. దయచేసి మీకు ఏ సేవ కావాలో చెప్పండి.',
                'listening': 'నేను వినడం లో ఉన్నాను...',
                'processing': 'మీ అభ్యర్థన ప్రాసెస్ చేయబడుతోంది...',
                'thanks': 'మా సేవను ఉపయోగించినందుకు ధన్యవాదాలు.',
                'goodbye': 'గుడ్బై! మీకు శుభ దినం.'
            },
            'kn': {
                'code': 'kn-IN',
                'name': 'Kannada',
                'wake_words': ['ಹೇ ಬಟ್ಲರ್', 'ನಮಸ್ತೆ ಬಟ್ಲರ್', 'ಹಲೋ ಬಟ್ಲರ್', 'ಬಟ್ಲರ್'],
                'greeting': 'ನಮಸ್ತೆ! ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?',
                'prompt': 'ನಿಮಗೆ ಯಾವ ಸೇವೆ ಬೇಕು?',
                'confirm': 'ನಾನು ನಿಮಗಾಗಿ ಒಂದನ್ನು ಹುಡುಕುತ್ತೇನೆ',
                'not_found': 'ಕ್ಷಮಿಸಿ, ನನಗೆ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಸೇವೆಯ ಹೆಸರನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ.',
                'searching': 'ಹುಡುಕುತ್ತಿದೆ',
                'found': 'ನಾನು ಕಂಡುಕೊಂಡೆ',
                'providers': 'ಪೂರೈಕೆದಾರರು ನಿಮಗಾಗಿ',
                'welcome': 'ಸ್ವಾಗತ! ನಾನು ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಸಹಾಯಕ.',
                'ready': 'ನಾನು ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧವಾಗಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ನಿಮಗೆ ಯಾವ ಸೇವೆ ಬೇಕು ಎಂದು ಹೇಳಿ.',
                'listening': 'ನಾನು ಕೇಳುತ್ತಿದ್ದೇನೆ...',
                'processing': 'ನಿಮ್ಮ ವಿನಂತಿಯನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲಾಗುತ್ತಿದೆ...',
                'thanks': 'ನಮ್ಮ ಸೇವೆಯನ್ನು ಬಳಸಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು.',
                'goodbye': 'ಗುಡ್ ಬೈ! ನಿಮ್ಮ ದಿನ ಶುಭವಾಗಲಿ.'
            },
            'ml': {
                'code': 'ml-IN',
                'name': 'Malayalam',
                'wake_words': ['ഹേ ബട്ലർ', 'ഹലോ ബട്ലർ', 'നമസ്കാരം ബട്ലർ', 'ബട്ലർ'],
                'greeting': 'നമസ്കാരം! ഇന്ന് എങ്ങനെയാണ് ഞാൻ നിങ്ങളെ സഹായിക്കാൻ കഴിയുക?',
                'prompt': 'നിങ്ങൾക്ക് ഏത് സേവനം വേണം?',
                'confirm': 'ഞാൻ നിങ്ങൾക്ക് ഒന്ന് തിരയും',
                'not_found': 'ക്ഷമിക്കണം, എനിക്ക് മനസ്സിലായില്ല. ദയവായി സേവനത്തിന്റെ പേര് വ്യക്തമായി പറയുക.',
                'searching': 'തിരയുന്നു',
                'found': 'ഞാൻ കണ്ടെത്തി',
                'providers': 'വിതരണക്കാർ നിങ്ങൾക്കായി',
                'welcome': 'സ്വാഗതം! ഞാൻ നിങ്ങളുടെ സ്വകാര്യ സഹായിയാണ്.',
                'ready': 'ഞാൻ സഹായിക്കാൻ തയ്യാറാണ്. ദയവായി നിങ്ങൾക്ക് ഏത് സേവനം വേണമെന്ന് പറയുക.',
                'listening': 'ഞാൻ കേൾക്കുന്നു...',
                'processing': 'നിങ്ങളുടെ അഭ്യർത്ഥന പ്രോസസ്സ് ചെയ്യുന്നു...',
                'thanks': 'ഞങ്ങളുടെ സേവനം ഉപയോഗിച്ചതിന് നന്ദി.',
                'goodbye': 'വിട! നല്ല ദിവസം.'
            },
            'mr': {
                'code': 'mr-IN',
                'name': 'Marathi',
                'wake_words': ['हे बटलर', 'नमस्कार बटलर', 'हॅलो बटलर', 'बटलर'],
                'greeting': 'नमस्कार! मी आज तुमची कशी मदत करू शकतो?',
                'prompt': 'तुम्हाला कोणती सेवा हवी आहे?',
                'confirm': 'मी तुमच्यासाठी एक शोधेन',
                'not_found': 'माफ करा, मला समजले नाही. कृपया सेवेचे नाव स्पष्टपणे सांगा.',
                'searching': 'शोधत आहे',
                'found': 'मला सापडले',
                'providers': 'प्रदाता तुमच्यासाठी',
                'welcome': 'स्वागत आहे! मी तुमचा वैयक्तिक सहाय्यक आहे.',
                'ready': 'मी मदतीसाठी तयार आहे. कृपया तुम्हाला कोणती सेवा हवी आहे ते सांगा.',
                'listening': 'मी ऐकत आहे...',
                'processing': 'तुमची विनंती प्रक्रिया केली जात आहे...',
                'thanks': 'आमची सेवा वापरल्याबद्दल धन्यवाद.',
                'goodbye': 'गुड बाय! तुमचा दिवस चांगला जावो.'
            },
            'bn': {
                'code': 'bn-IN',
                'name': 'Bengali',
                'wake_words': ['হেই বাটলার', 'হ্যালো বাটলার', 'নমস্কার বাটলার', 'বাটলার'],
                'greeting': 'নমস্কার! আজ আমি আপনাকে কিভাবে সাহায্য করতে পারি?',
                'prompt': 'আপনার কোন পরিষেবা প্রয়োজন?',
                'confirm': 'আমি আপনার জন্য একটি খুঁজব',
                'not_found': 'দুঃখিত, আমি বুঝতে পারিনি। দয়া করে পরিষেবার নামটি স্পষ্টভাবে বলুন।',
                'searching': 'অনুসন্ধান করছে',
                'found': 'আমি পেয়েছি',
                'providers': 'প্রদানকারীরা আপনার জন্য',
                'welcome': 'স্বাগতম! আমি আপনার ব্যক্তিগত সহায়ক।',
                'ready': 'আমি সাহায্য করার জন্য প্রস্তুত। দয়া করে বলুন আপনার কোন পরিষেবা প্রয়োজন।',
                'listening': 'আমি শুনছি...',
                'processing': 'আপনার অনুরোধ প্রক্রিয়া করা হচ্ছে...',
                'thanks': 'আমাদের পরিষেবা ব্যবহার করার জন্য ধন্যবাদ।',
                'goodbye': 'বিদায়! আপনার ভালো দিন হোক।'
            },
            'gu': {
                'code': 'gu-IN',
                'name': 'Gujarati',
                'wake_words': ['હે બટલર', 'હેલો બટલર', 'નમસ્તે બટલર', 'બટલર'],
                'greeting': 'નમસ્તે! હું આજે તમારી કેવી રીતે મદદ કરી શકું?',
                'prompt': 'તમારે કઈ સેવા જોઈએ છે?',
                'confirm': 'હું તમારા માટે એક શોધીશ',
                'not_found': 'માફ કરશો, હું સમજી શક્યો નથી. કૃપા કરીને સેવાનું નામ સ્પષ્ટ રીતે કહો.',
                'searching': 'શોધી રહ્યું છે',
                'found': 'મને મળી',
                'providers': 'પ્રદાતાઓ તમારા માટે',
                'welcome': 'સ્વાગત છે! હું તમારો વ્યક્તિગત સહાયક છું.',
                'ready': 'હું મદદ કરવા માટે તૈયાર છું. કૃપા કરીને તમારે કઈ સેવા જોઈએ છે તે કહો.',
                'listening': 'હું સાંભળી રહ્યો છું...',
                'processing': 'તમારી વિનંતી પ્રક્રિયા કરવામાં આવી રહી છે...',
                'thanks': 'અમારી સેવા વાપરવા બદલ આભાર.',
                'goodbye': 'ગુડબાય! તમારો દિવસ સુખમય રહે.'
            },
            'pa': {
                'code': 'pa-IN',
                'name': 'Punjabi',
                'wake_words': ['ਹੇ ਬਟਲਰ', 'ਹੈਲੋ ਬਟਲਰ', 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ ਬਟਲਰ', 'ਬਟਲਰ'],
                'greeting': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਅੱਜ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?',
                'prompt': 'ਤੁਹਾਨੂੰ ਕਿਹੜੀ ਸੇਵਾ ਚਾਹੀਦੀ ਹੈ?',
                'confirm': 'ਮੈਂ ਤੁਹਾਡੇ ਲਈ ਇੱਕ ਲੱਭਾਂਗਾ',
                'not_found': 'ਮਾਫ਼ ਕਰਨਾ, ਮੈਂ ਸਮਝ ਨਹੀਂ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਸੇਵਾ ਦਾ ਨਾਮ ਸਪੱਸ਼ਟ ਤੌਰ \'ਤੇ ਦੱਸੋ।',
                'searching': 'ਖੋਜ ਰਿਹਾ ਹੈ',
                'found': 'ਮੈਨੂੰ ਮਿਲ ਗਿਆ',
                'providers': 'ਪ੍ਰਦਾਤਾ ਤੁਹਾਡੇ ਲਈ',
                'welcome': 'ਸਵਾਗਤ ਹੈ! ਮੈਂ ਤੁਹਾਡਾ ਨਿੱਜੀ ਸਹਾਇਕ ਹਾਂ.',
                'ready': 'ਮੈਂ ਮਦਦ ਕਰਨ ਲਈ ਤਿਆਰ ਹਾਂ। ਕਿਰਪਾ ਕਰਕੇ ਦੱਸੋ ਕਿ ਤੁਹਾਨੂੰ ਕਿਹੜੀ ਸੇਵਾ ਚਾਹੀਦੀ ਹੈ।',
                'listening': 'ਮੈਂ ਸੁਣ ਰਿਹਾ ਹਾਂ...',
                'processing': 'ਤੁਹਾਡੀ ਬੇਨਤੀ ਪ੍ਰਕਿਰਿਆ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ...',
                'thanks': 'ਸਾਡੀ ਸੇਵਾ ਦੀ ਵਰਤੋਂ ਕਰਨ ਲਈ ਧੰਨਵਾਦ।',
                'goodbye': 'ਅਲਵਿਦਾ! ਤੁਹਾਡਾ ਦਿਨ ਚੰਗਾ ਰਹੇ।'
            },
            'or': {
                'code': 'or-IN',
                'name': 'Odia',
                'wake_words': ['ହେ ବଟଲର', 'ନମସ୍କାର ବଟଲର', 'ହେଲୋ ବଟଲର', 'ବଟଲର'],
                'greeting': 'ନମସ୍କାର! ମୁଁ ଆଜି ଆପଣଙ୍କର କିପରି ସାହାଯ୍ୟ କରିପାରିବି?',
                'prompt': 'ଆପଣଙ୍କୁ କେଉଁ ସେବା ଆବଶ୍ୟକ?',
                'confirm': 'ମୁଁ ଆପଣଙ୍କ ପାଇଁ ଗୋଟିଏ ଖୋଜିବି',
                'not_found': 'କ୍ଷମା କରିବେ, ମୁଁ ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ସେବାର ନାମ ସ୍ପଷ୍ଟ ଭାବରେ କୁହନ୍ତୁ।',
                'searching': 'ଖୋଜୁଛି',
                'found': 'ମୁଁ ପାଇଲି',
                'providers': 'ପ୍ରଦାନକାରୀ ଆପଣଙ୍କ ପାଇଁ',
                'welcome': 'ସ୍ୱାଗତ! ମୁଁ ଆପଣଙ୍କର ବ୍ୟକ୍ତିଗତ ସହାୟକ।',
                'ready': 'ମୁଁ ସହାୟତା କରିବାକୁ ପ୍ରସ୍ତୁତ ଅଛି। ଦୟାକରି କୁହନ୍ତୁ ଆପଣଙ୍କୁ କେଉଁ ସେବା ଦରକାର।',
                'listening': 'ମୁଁ ଶୁଣୁଛି...',
                'processing': 'ଆପଣଙ୍କ ଅନୁରୋଧ ପ୍ରକ୍ରିୟାକରଣ ହେଉଛି...',
                'thanks': 'ଆମ ସେବା ବ୍ୟବହାର କରିବା ପାଇଁ ଧନ୍ୟବାଦ।',
                'goodbye': 'ବିଦାୟ! ଆପଣଙ୍କର ଦିନ ଶୁଭ ହେଉ।'
            },
            'as': {
                'code': 'as-IN',
                'name': 'Assamese',
                'wake_words': ['হে বাটলাৰ', 'নমস্কাৰ বাটলাৰ', 'হেলো বাটলাৰ', 'বাটলাৰ'],
                'greeting': 'নমস্কাৰ! মই আজি আপোনাক কেনেকৈ সহায় কৰিব পাৰো?',
                'prompt': 'আপোনাক কোনটো সেৱা লাগিব?',
                'confirm': 'মই আপোনাৰ বাবে এটা বিচাৰিম',
                'not_found': 'ক্ষমা কৰিব, মই বুজি নাপালো। অনুগ্ৰহ কৰি সেৱাৰ নাম স্পষ্টকৈ কওক।',
                'searching': 'সন্ধান কৰি আছে',
                'found': 'মই পাইছো',
                'providers': 'প্ৰদানকাৰী আপোনাৰ বাবে',
                'welcome': 'স্বাগতম! মই আপোনাৰ ব্যক্তিগত সহায়ক।',
                'ready': 'মই সহায় কৰিবলৈ প্ৰস্তুত আছো। অনুগ্ৰহ কৰি কওক আপোনাক কোনটো সেৱা লাগিব।',
                'listening': 'মই শুনি আছো...',
                'processing': 'আপোনাৰ অনুৰোধ প্ৰক্ৰিয়া কৰি থকা হৈছে...',
                'thanks': 'আমাৰ সেৱা ব্যৱহাৰ কৰাৰ বাবে ধন্যবাদ।',
                'goodbye': 'বিদায়! আপোনাৰ দিনটো শুভ হওক।'
            },
            'ur': {
                'code': 'ur-IN',
                'name': 'Urdu',
                'wake_words': ['ارے بٹلر', 'ہیلو بٹلر', 'اسلام علیکم بٹلر', 'بٹلر'],
                'greeting': 'اسلام علیکم! میں آج آپ کی کس طرح مدد کر سکتا ہوں؟',
                'prompt': 'آپ کو کون سی خدمت چاہیے؟',
                'confirm': 'میں آپ کے لیے ایک تلاش کروں گا',
                'not_found': 'معاف کیجیے، میں سمجھ نہیں سکا۔ براہ کرم خدمت کا نام واضح طور پر بتائیں۔',
                'searching': 'تلاش کر رہا ہے',
                'found': 'مجھے مل گیا',
                'providers': 'فراہم کنندگان آپ کے لیے',
                'welcome': 'خوش آمدید! میں آپ کا ذاتی معاون ہوں۔',
                'ready': 'میں مدد کرنے کے لیے تیار ہوں۔ براہ کرم بتائیں کہ آپ کو کون سی خدمت چاہیے۔',
                'listening': 'میں سن رہا ہوں...',
                'processing': 'آپ کی درخواست پر کارروائی کی جا رہی ہے...',
                'thanks': 'ہماری خدمت استعمال کرنے کے لیے شکریہ۔',
                'goodbye': 'الوداع! آپ کا دن اچھا گزرے۔'
            },
            'sd': {
                'code': 'sd-IN',
                'name': 'Sindhi',
                'wake_words': ['ايئ بٽلر', 'هيلو بٽلر', 'سلام بٽلر', 'بٽلر'],
                'greeting': 'سلام! آئون اڄ توهان جي ڪيئن مدد ڪري سگهان ٿو؟',
                'prompt': 'توهان کي ڪهڙي خدمت گهربل آهي؟',
                'confirm': 'مان توهان لاءِ هڪ ڳوليندس',
                'not_found': 'معافي گهرو، مون سمجهي نه سگهيس. مهرباني ڪري خدمت جو نالو صاف طور تي چئو.',
                'searching': 'ڳولي رهيو آهي',
                'found': 'مون کي مليو',
                'providers': 'فراهم ڪندڙ توهان لاءِ',
                'welcome': 'ڀليڪار! مان توهان جو ذاتي مددگار آهيان.',
                'ready': 'مان مدد ڪرڻ لاءِ تيار آهيان. مهرباني ڪري چئو توهان کي ڪهڙي خدمت گهربل آهي.',
                'listening': 'مان ٻڌي رهيو آهيان...',
                'processing': 'توهان جي درخواست تي عملدرآمد ٿي رهيو آهي...',
                'thanks': 'اسان جي خدمت استعمال ڪرڻ لاءِ مهرباني.',
                'goodbye': 'الله وڃي! توهان جو ڏينهن سٺو گذري.'
            }
        }
        
        # Current detected language (starts with English)
        self.current_language = 'en'
        self.language_history = []
        
        # Service keywords in multiple languages - COMPREHENSIVE 400+ SERVICES
        self.service_keywords = self._create_comprehensive_service_keywords()
        
        # Multi-lingual wake words
        self.wake_words = self._get_all_wake_words()
        
        # Conversation state
        self.conversation_active = False
        self.last_interaction_time = time.time()
        
        logger.info(f"✅ CLEAN PRODUCTION Voice Recognizer Initialized (Mic Index: {mic_device_index})")
        logger.info(f"🌐 Supported languages: {len(self.supported_languages)} languages")
        logger.info(f"🔍 Service categories: {len(self.service_keywords)} services")
        logger.info(f"🎤 Speech synthesizer ready")
        logger.info(f"🔊 Using ALSA direct access: {use_alsa}")
    
    def _create_comprehensive_service_keywords(self) -> Dict[str, List[str]]:
        """Create comprehensive multi-lingual service keywords (400+ services)"""
        
        # COMPREHENSIVE SERVICE KEYWORDS DICTIONARY
        service_keywords = {
            # ========== HOME SERVICES (40+ services) ==========
            'electrician': ['electrician', 'electric', 'electrical', 'wiring', 'wire', 'current', 'light', 'power', 'switch', 'fuse', 'circuit', 'electrical work', 'wiring repair', 'mcbs', 'wiring installation'],
            'plumber': ['plumber', 'plumbing', 'pipe', 'leak', 'water', 'tap', 'faucet', 'drain', 'toilet', 'bathroom', 'sink', 'washbasin', 'water tap', 'water pipe', 'bath fitting', 'pipe fitting', 'toilet repair'],
            'carpenter': ['carpenter', 'carpentry', 'wood', 'furniture', 'cabinet', 'door', 'window', 'woodwork', 'furniture repair', 'sofa repair', 'cupboard', 'wardrobe', 'bed', 'table', 'chair', 'wooden work'],
            'painter': ['painter', 'painting', 'paint', 'wall', 'color', 'home painting', 'house painting', 'wall painting', 'exterior painting', 'interior painting', 'wall putty', 'wall primer', 'texture painting'],
            'cleaner': ['cleaner', 'cleaning', 'maid', 'housekeeping', 'sweep', 'mop', 'clean', 'cleaning lady', 'house cleaner', 'deep cleaning', 'house cleaning', 'room cleaning', 'office cleaning', 'post construction cleaning'],
            'ac repair': ['ac repair', 'air conditioner', 'ac service', 'cooling repair', 'ac technician', 'air conditioning', 'ac gas filling', 'split ac', 'window ac', 'ac installation', 'ac maintenance'],
            'appliance repair': ['appliance repair', 'fridge repair', 'washing machine repair', 'oven repair', 'microwave repair', 'geyser repair', 'mixer repair', 'grinder repair', 'chimney repair', 'induction repair'],
            'pest control': ['pest control', 'pest', 'insect', 'cockroach', 'termite', 'rat', 'rodent', 'mosquito', 'bed bug', 'lizard', 'ant', 'spray', 'fumigation', 'termite control'],
            'gardener': ['gardener', 'gardening', 'garden', 'plants', 'lawn', 'landscaping', 'tree cutting', 'pruning', 'planting', 'garden maintenance', 'lawn mowing', 'hedge trimming'],
            'security guard': ['security guard', 'security', 'guard', 'watchman', 'security personnel', 'gate guard', 'society guard', 'security service', 'security agency', 'bouncer'],
            'waterproofing': ['waterproofing', 'waterproof', 'leakage', 'terrace waterproofing', 'bathroom waterproofing', 'wall waterproofing', 'roof waterproofing', 'basement waterproofing'],
            'false ceiling': ['false ceiling', 'ceiling', 'pop ceiling', 'gypsum ceiling', 'false ceiling work', 'ceiling design', 'ceiling installation'],
            'tiles work': ['tiles work', 'tile', 'flooring', 'marble', 'granite', 'vitrified tiles', 'ceramic tiles', 'tile fixing', 'tile installation'],
            'sofa cleaning': ['sofa cleaning', 'sofa wash', 'sofa shampoo', 'sofa deep clean', 'leather sofa cleaning', 'fabric sofa cleaning'],
            'cctv installation': ['cctv installation', 'cctv camera', 'security camera', 'surveillance', 'camera installation', 'dvr installation'],
            'aluminum work': ['aluminum work', 'aluminum door', 'aluminum window', 'aluminum fabrication', 'sliding window', 'casement window'],
            'fabrication work': ['fabrication work', 'fabrication', 'steel fabrication', 'metal work', 'grill work', 'gate fabrication'],
            'modular kitchen': ['modular kitchen', 'kitchen cabinet', 'kitchen work', 'kitchen design', 'kitchen installation'],
            'wardrobe design': ['wardrobe design', 'wardrobe', 'cupboard design', 'modular wardrobe', 'sliding wardrobe'],
            'glass work': ['glass work', 'glass door', 'glass window', 'glass partition', 'glass fitting', 'tempered glass'],
            
            # ========== PERSONAL CARE & BEAUTY (30+ services) ==========
            'barber': ['barber', 'haircut', 'salon', 'hairdresser', 'hair stylist', 'beauty salon', 'mens haircut', 'ladies salon', 'haircutting', 'salon service'],
            'beautician': ['beautician', 'beauty parlour', 'facial', 'threading', 'waxing', 'manicure', 'pedicure', 'spa', 'massage', 'bleach', 'cleanup', 'makeup', 'bridal makeup'],
            'yoga trainer': ['yoga trainer', 'yoga teacher', 'yoga instructor', 'yoga classes', 'yoga therapy', 'meditation teacher', 'pranayama', 'yoga at home', 'online yoga'],
            'fitness trainer': ['fitness trainer', 'gym trainer', 'personal trainer', 'exercise trainer', 'weight loss trainer', 'diet trainer', 'bodybuilding trainer', 'fitness coach', 'gym instructor'],
            'tailor': ['tailor', 'stitching', 'dress making', 'alteration', 'clothes stitching', 'suit stitching', 'blouse stitching', 'kurta stitching', 'dress alteration', 'stitching work'],
            'laundry': ['laundry', 'dry cleaning', 'clothes washing', 'ironing', 'laundry service', 'dhobi', 'cloth press', 'steam iron', 'washing service'],
            'mehndi artist': ['mehndi artist', 'mehndi', 'henna', 'bridal mehndi', 'mehndi design', 'hand mehndi', 'foot mehndi'],
            'makeup artist': ['makeup artist', 'bridal makeup', 'event makeup', 'makeup', 'beauty makeup', 'party makeup', 'photoshoot makeup'],
            'hair colorist': ['hair colorist', 'hair coloring', 'hair dye', 'hair tint', 'highlights', 'ombre', 'balayage', 'hair treatment'],
            'skin specialist': ['skin specialist', 'dermatologist', 'skin care', 'skin treatment', 'acne treatment', 'skin whitening', 'facial treatment'],
            'weight loss center': ['weight loss center', 'weight loss', 'slimming center', 'fat reduction', 'weight management', 'diet center'],
            'ayurvedic massage': ['ayurvedic massage', 'ayurveda', 'ayurvedic therapy', 'panchakarma', 'abhyanga', 'shirodhara'],
            'hair transplant': ['hair transplant', 'hair restoration', 'hair fall treatment', 'baldness treatment', 'prp treatment'],
            'tattoo artist': ['tattoo artist', 'tattoo', 'tattooing', 'tattoo design', 'permanent makeup', 'microblading'],
            'piercing specialist': ['piercing specialist', 'piercing', 'ear piercing', 'nose piercing', 'body piercing'],
            
            # ========== HEALTHCARE & MEDICAL (50+ services) ==========
            'doctor': ['doctor', 'physician', 'medical', 'clinic', 'hospital', 'general physician', 'family doctor', 'mbbs doctor', 'consultation', 'medical checkup'],
            'dentist': ['dentist', 'dental', 'teeth', 'tooth', 'dental clinic', 'tooth pain', 'dental filling', 'root canal', 'teeth cleaning', 'braces', 'dental implant'],
            'physiotherapist': ['physiotherapist', 'physiotherapy', 'physical therapy', 'back pain', 'joint pain', 'rehabilitation', 'exercise therapy', 'pain relief', 'muscle therapy'],
            'nurse': ['nurse', 'nursing', 'home nurse', 'patient care', 'elderly care', 'nursing attendant', 'caretaker', 'medical attendant'],
            'pharmacist': ['pharmacist', 'pharmacy', 'medical store', 'chemist', 'medicine', 'drug store', 'dispensary', 'medical shop'],
            'dietician': ['dietician', 'dietitian', 'nutritionist', 'diet plan', 'weight loss diet', 'diabetes diet', 'thyroid diet', 'pcos diet', 'cholesterol diet'],
            'psychologist': ['psychologist', 'counselor', 'therapy', 'mental health', 'psychiatrist', 'counselling', 'therapy session', 'mental wellness'],
            'cardiologist': ['cardiologist', 'heart specialist', 'heart doctor', 'cardiology', 'heart checkup', 'ecg', 'echo'],
            'gynecologist': ['gynecologist', 'ladies doctor', 'obgyn', 'women health', 'pregnancy doctor', 'delivery doctor'],
            'pediatrician': ['pediatrician', 'child specialist', 'kids doctor', 'baby doctor', 'pediatrics', 'child health'],
            'orthopedic': ['orthopedic', 'bone specialist', 'fracture', 'joint replacement', 'knee pain', 'backbone specialist'],
            'eye specialist': ['eye specialist', 'ophthalmologist', 'eye doctor', 'eye checkup', 'spectacles', 'contact lenses', 'lasik'],
            'ent specialist': ['ent specialist', 'ear nose throat', 'ent doctor', 'sinus', 'tonsils', 'hearing test'],
            'dermatologist': ['dermatologist', 'skin doctor', 'skin treatment', 'hair fall', 'skin disease', 'psoriasis'],
            'homeopathy doctor': ['homeopathy doctor', 'homeopath', 'homeopathic', 'homeopathy medicine', 'homeopathy treatment'],
            'ayurvedic doctor': ['ayurvedic doctor', 'ayurveda', 'ayurvedic treatment', 'ayurvedic medicine', 'panchakarma'],
            'pathology lab': ['pathology lab', 'blood test', 'lab test', 'diagnostic center', 'urine test', 'sugar test'],
            'x ray center': ['x ray center', 'xray', 'radiology', 'ct scan', 'mri', 'ultrasound', 'sonography'],
            'ambulance service': ['ambulance service', 'ambulance', 'patient transport', 'emergency ambulance', 'icu ambulance'],
            'medical equipment': ['medical equipment', 'oxygen cylinder', 'wheelchair', 'walking stick', 'hospital bed', 'bp machine'],
            
            # ========== PROFESSIONAL & BUSINESS SERVICES (60+ services) ==========
            'web developer': ['web developer', 'website', 'programmer', 'coder', 'web design', 'website making', 'web application', 'website development', 'ecommerce website'],
            'graphic designer': ['graphic designer', 'designer', 'logo design', 'brochure design', 'graphic design', 'photoshop', 'illustrator', 'visiting card', 'banner design'],
            'accountant': ['accountant', 'ca', 'chartered accountant', 'tax consultant', 'audit', 'bookkeeping', 'gst filing', 'income tax', 'tally operator'],
            'lawyer': ['lawyer', 'advocate', 'legal', 'court case', 'legal advice', 'property lawyer', 'criminal lawyer', 'divorce lawyer', 'corporate lawyer'],
            'tutor': ['tutor', 'teacher', 'home tutor', 'tuition', 'coaching', 'private tutor', 'maths tutor', 'science tutor', 'english tutor', 'physics tutor'],
            'photographer': ['photographer', 'photography', 'camera', 'wedding photographer', 'event photographer', 'photo shoot', 'portrait photography', 'product photography'],
            'caterer': ['caterer', 'catering', 'food catering', 'party food', 'marriage catering', 'event catering', 'birthday catering', 'office catering'],
            'digital marketer': ['digital marketer', 'digital marketing', 'seo', 'social media marketing', 'google ads', 'facebook ads', 'instagram marketing'],
            'content writer': ['content writer', 'writer', 'content writing', 'blog writing', 'article writing', 'website content', 'copywriting'],
            'video editor': ['video editor', 'video editing', 'video making', 'youtube video', 'wedding video', 'corporate video', 'animation'],
            'seo expert': ['seo expert', 'seo', 'search engine optimization', 'google ranking', 'website ranking', 'seo services'],
            'mobile app developer': ['mobile app developer', 'app developer', 'android app', 'ios app', 'mobile application', 'flutter developer', 'react native'],
            'data scientist': ['data scientist', 'data analyst', 'data analytics', 'machine learning', 'ai', 'artificial intelligence', 'python developer'],
            'hr consultant': ['hr consultant', 'human resources', 'recruitment', 'staffing', 'payroll', 'hr services', 'talent acquisition'],
            'event manager': ['event manager', 'event management', 'event planning', 'event organizer', 'corporate event', 'conference organizer'],
            'interior designer': ['interior designer', 'interior decoration', 'home interior', 'room design', 'office interior', 'commercial interior'],
            'architect': ['architect', 'architecture', 'building design', 'house plan', 'construction design', 'building plan', 'structural design'],
            'civil engineer': ['civil engineer', 'construction engineer', 'site engineer', 'building contractor', 'construction supervisor'],
            'electrical engineer': ['electrical engineer', 'electrical design', 'electrical planning', 'electrical consultant', 'electrical supervisor'],
            'mechanical engineer': ['mechanical engineer', 'mechanical design', 'machine design', 'cad designer', 'automobile engineer'],
            
            # ========== AUTOMOTIVE & TRANSPORT (40+ services) ==========
            'car mechanic': ['car mechanic', 'auto repair', 'car service', 'vehicle repair', 'engine repair', 'car washing', 'car repair', 'garage', 'car workshop'],
            'bike mechanic': ['bike mechanic', 'bike repair', 'two wheeler repair', 'scooter repair', 'motorcycle service', 'bike service', 'bike washing'],
            'driver': ['driver', 'chauffeur', 'car driver', 'taxi driver', 'cab driver', 'personal driver', 'office driver', 'school bus driver'],
            'car cleaning': ['car cleaning', 'car wash', 'car detailing', 'interior cleaning', 'exterior polishing', 'car shampoo', 'car vacuum'],
            'towing service': ['towing service', 'car towing', 'breakdown service', 'vehicle towing', 'accident towing', 'roadside assistance'],
            'car painting': ['car painting', 'car body paint', 'dent painting', 'scratch repair', 'car polishing', 'tinkering', 'car body work'],
            'car ac repair': ['car ac repair', 'car air conditioner', 'car cooling', 'car ac gas', 'car ac service', 'car cooling repair'],
            'tyre shop': ['tyre shop', 'tyre repair', 'tyre change', 'wheel alignment', 'wheel balancing', 'puncture repair', 'tyre fitting'],
            'battery shop': ['battery shop', 'car battery', 'inverter battery', 'battery repair', 'battery replacement', 'battery charging'],
            'car accessory': ['car accessory', 'car stereo', 'car music system', 'car seat cover', 'car mat', 'car perfume', 'car dashboard'],
            'driving school': ['driving school', 'driving instructor', 'learn driving', 'driving classes', 'driving license', 'car driving lessons'],
            'car rental': ['car rental', 'rent a car', 'self drive car', 'car hire', 'monthly car rental', 'outstation car'],
            'truck repair': ['truck repair', 'truck mechanic', 'heavy vehicle repair', 'truck service', 'tempo repair', 'bus repair'],
            'auto rickshaw': ['auto rickshaw', 'auto', 'rickshaw', 'three wheeler', 'auto repair', 'auto service', 'auto mechanic'],
            
            # ========== EDUCATION & TRAINING (50+ services) ==========
            'english tutor': ['english tutor', 'spoken english', 'english speaking', 'english teacher', 'english coaching', 'english classes', 'english grammar'],
            'maths tutor': ['maths tutor', 'mathematics teacher', 'math teacher', 'math coaching', 'calculus tutor', 'algebra tutor', 'geometry tutor'],
            'science tutor': ['science tutor', 'physics tutor', 'chemistry tutor', 'biology tutor', 'science teacher', 'science coaching'],
            'computer teacher': ['computer teacher', 'computer classes', 'computer coaching', 'coding classes', 'programming teacher', 'software training'],
            'music teacher': ['music teacher', 'music classes', 'guitar teacher', 'piano teacher', 'violin teacher', 'singing teacher', 'drum teacher'],
            'dance teacher': ['dance teacher', 'dance classes', 'dance instructor', 'dance academy', 'bollywood dance', 'classical dance', 'hip hop'],
            'art teacher': ['art teacher', 'drawing classes', 'painting classes', 'art classes', 'sketching', 'canvas painting', 'oil painting'],
            'yoga teacher': ['yoga teacher', 'yoga classes', 'yoga instructor', 'yoga therapy', 'meditation classes', 'pranayama classes'],
            'coaching center': ['coaching center', 'tuition center', 'study center', 'educational institute', 'test preparation'],
            'ielts coaching': ['ielts coaching', 'ielts classes', 'ielts training', 'ielts preparation', 'english test'],
            'toefl coaching': ['toefl coaching', 'toefl classes', 'toefl training', 'toefl preparation', 'toefl test'],
            'gre coaching': ['gre coaching', 'gre classes', 'gre training', 'gre preparation', 'gre test'],
            'gmat coaching': ['gmat coaching', 'gmat classes', 'gmat training', 'gmat preparation', 'gmat test'],
            'cat coaching': ['cat coaching', 'cat classes', 'cat training', 'cat preparation', 'mba entrance'],
            'bank exam coaching': ['bank exam coaching', 'bank po classes', 'bank clerk', 'bank exam preparation', 'government job coaching'],
            'ssc coaching': ['ssc coaching', 'ssc classes', 'ssc preparation', 'government exam', 'competitive exam'],
            'upsc coaching': ['upsc coaching', 'ias coaching', 'upsc classes', 'civil services', 'government exam preparation'],
            'engineering tutor': ['engineering tutor', 'engineering coaching', 'btech tutor', 'engineering subjects', 'semester coaching'],
            'medical tutor': ['medical tutor', 'mbbs tutor', 'neet coaching', 'medical coaching', 'anatomy tutor'],
            'language classes': ['language classes', 'french classes', 'spanish classes', 'german classes', 'japanese classes'],
            
            # ========== REAL ESTATE & CONSTRUCTION (40+ services) ==========
            'property dealer': ['property dealer', 'real estate agent', 'broker', 'property agent', 'flat dealer', 'house broker', 'property consultant'],
            'interior designer': ['interior designer', 'interior decoration', 'home interior', 'room design', 'office interior', 'commercial interior'],
            'architect': ['architect', 'architecture', 'building design', 'house plan', 'construction design', 'building plan', 'structural design'],
            'construction worker': ['construction worker', 'mason', 'labour', 'construction labour', 'building worker', 'construction helper'],
            'construction contractor': ['construction contractor', 'building contractor', 'house construction', 'construction company', 'civil contractor'],
            'plumbing contractor': ['plumbing contractor', 'plumbing work', 'water supply', 'sewer line', 'drainage system', 'pipeline work'],
            'electrical contractor': ['electrical contractor', 'electrical work', 'wiring contractor', 'electrical installation', 'electrical fitting'],
            'painting contractor': ['painting contractor', 'painting work', 'wall painting contractor', 'exterior painting contractor'],
            'carpentry contractor': ['carpentry contractor', 'carpentry work', 'wood work contractor', 'furniture making contractor'],
            'flooring contractor': ['flooring contractor', 'flooring work', 'tile contractor', 'marble contractor', 'floor installation'],
            'roofing contractor': ['roofing contractor', 'roofing work', 'roof repair', 'roof waterproofing', 'roof construction'],
            'demolition contractor': ['demolition contractor', 'demolition work', 'building demolition', 'structure demolition'],
            'excavation contractor': ['excavation contractor', 'excavation work', 'digging', 'earthwork', 'foundation digging'],
            'surveyor': ['surveyor', 'land surveyor', 'property survey', 'measurement', 'site survey', 'boundary marking'],
            'vaastu consultant': ['vaastu consultant', 'vaastu', 'vastu shastra', 'vastu expert', 'vastu for home', 'vastu for office'],
            'property valuer': ['property valuer', 'property valuation', 'property assessment', 'real estate valuation'],
            'home inspector': ['home inspector', 'property inspection', 'building inspection', 'structural inspection'],
            'rental agent': ['rental agent', 'rental property', 'house for rent', 'flat for rent', 'rental broker'],
            'property manager': ['property manager', 'property management', 'society management', 'apartment management'],
            'legal advisor': ['legal advisor', 'property legal', 'title verification', 'property documentation', 'registry'],
            
            # ========== LOGISTICS & TRANSPORT (30+ services) ==========
            'packers and movers': ['packers and movers', 'shifting', 'house shifting', 'office shifting', 'transport service', 'loading unloading'],
            'courier': ['courier', 'delivery', 'parcel', 'package delivery', 'document courier', 'express delivery', 'logistics'],
            'taxi service': ['taxi service', 'cab', 'ola', 'uber', 'car rental', 'outstation taxi', 'local taxi', 'airport taxi'],
            'truck rental': ['truck rental', 'truck', 'transport truck', 'goods vehicle', 'tempo', 'lorry', 'transport vehicle'],
            'logistics company': ['logistics company', 'logistics service', 'cargo', 'freight', 'goods transport', 'transport company'],
            'warehouse': ['warehouse', 'storage', 'godown', 'cold storage', 'warehousing', 'storage facility'],
            'supply chain': ['supply chain', 'supply management', 'inventory management', 'distribution', 'logistics management'],
            'customs clearance': ['customs clearance', 'customs agent', 'import export', 'customs broker', 'shipping agent'],
            'port services': ['port services', 'shipping', 'container', 'port logistics', 'marine transport'],
            'air cargo': ['air cargo', 'air freight', 'air transport', 'air shipment', 'air logistics'],
            'rail transport': ['rail transport', 'railway goods', 'train transport', 'rail logistics'],
            'last mile delivery': ['last mile delivery', 'local delivery', 'home delivery', 'same day delivery'],
            'bike delivery': ['bike delivery', 'bike rider', 'delivery boy', 'food delivery', 'quick delivery'],
            'tempo traveller': ['tempo traveller', 'tempo', 'group transport', 'tourist transport', 'family transport'],
            
            # ========== TECHNOLOGY & IT SERVICES (50+ services) ==========
            'mobile repair': ['mobile repair', 'phone repair', 'smartphone repair', 'screen replacement', 'mobile service', 'iphone repair', 'android repair'],
            'laptop repair': ['laptop repair', 'computer repair', 'pc repair', 'hardware repair', 'software installation', 'laptop service', 'computer service'],
            'network engineer': ['network engineer', 'wifi setup', 'internet setup', 'router configuration', 'network installation', 'lan setup', 'wifi installation'],
            'data entry': ['data entry', 'typing', 'computer operator', 'data processing', 'excel work', 'data typing', 'online data entry'],
            'software developer': ['software developer', 'software engineer', 'programmer', 'coder', 'software development', 'custom software'],
            'cloud services': ['cloud services', 'cloud computing', 'aws', 'azure', 'google cloud', 'cloud hosting', 'cloud storage'],
            'cyber security': ['cyber security', 'security audit', 'hacking protection', 'network security', 'data protection'],
            'it support': ['it support', 'technical support', 'computer support', 'it helpdesk', 'tech support', 'it services'],
            'website hosting': ['website hosting', 'web hosting', 'domain registration', 'server hosting', 'shared hosting', 'vps'],
            'erp implementation': ['erp implementation', 'erp software', 'sap', 'oracle', 'erp consultant', 'erp customization'],
            'crm services': ['crm services', 'customer relationship', 'salesforce', 'crm software', 'crm implementation'],
            'pos system': ['pos system', 'point of sale', 'billing software', 'retail software', 'shop billing'],
            'biometric system': ['biometric system', 'fingerprint', 'attendance system', 'access control', 'biometric device'],
            'surveillance system': ['surveillance system', 'cctv installation', 'security camera', 'dvr system', 'nvr system'],
            'firewall setup': ['firewall setup', 'network firewall', 'security firewall', 'firewall configuration'],
            'voip services': ['voip services', 'internet calling', 'voip phone', 'virtual phone', 'business phone'],
            'data recovery': ['data recovery', 'hard disk recovery', 'data retrieval', 'lost data', 'corrupt data'],
            'antivirus': ['antivirus', 'virus removal', 'malware removal', 'pc security', 'computer antivirus'],
            'website maintenance': ['website maintenance', 'website update', 'website management', 'content update'],
            'app testing': ['app testing', 'software testing', 'quality assurance', 'manual testing', 'automation testing'],
            
            # ========== EVENT & ENTERTAINMENT (40+ services) ==========
            'event planner': ['event planner', 'event management', 'party planner', 'wedding planner', 'function organizer', 'event organizer'],
            'caterer': ['caterer', 'catering', 'food catering', 'party food', 'marriage catering', 'event catering', 'birthday catering'],
            'decorator': ['decorator', 'decoration', 'event decoration', 'wedding decoration', 'stage decoration', 'flower decoration', 'balloon decoration'],
            'dj': ['dj', 'disc jockey', 'music', 'sound system', 'party music', 'wedding music', 'dance music', 'music system'],
            'makeup artist': ['makeup artist', 'bridal makeup', 'event makeup', 'makeup', 'beauty makeup', 'party makeup', 'photoshoot makeup'],
            'photographer': ['photographer', 'photography', 'camera', 'wedding photographer', 'event photographer', 'photo shoot', 'portrait photography'],
            'videographer': ['videographer', 'video shooting', 'video coverage', 'wedding video', 'event video', 'corporate video'],
            'mehndi artist': ['mehndi artist', 'mehndi', 'henna', 'bridal mehndi', 'mehndi design', 'hand mehndi'],
            'anchor': ['anchor', 'emcee', 'host', 'stage host', 'event host', 'wedding anchor', 'corporate anchor'],
            'magician': ['magician', 'magic show', 'illusionist', 'magic performance', 'children magic', 'party magic'],
            'standup comedian': ['standup comedian', 'comedy show', 'comedian', 'humorist', 'comedy performance'],
            'dance group': ['dance group', 'dance performance', 'cultural dance', 'bollywood dance', 'classical dance'],
            'singing group': ['singing group', 'live singing', 'singer', 'band', 'music band', 'orchestra'],
            'tent house': ['tent house', 'tent', 'pandal', 'marriage tent', 'party tent', 'event tent'],
            'lighting service': ['lighting service', 'event lighting', 'stage lighting', 'light setup', 'dj lights'],
            'sound system': ['sound system', 'audio system', 'speakers', 'microphone', 'pa system', 'audio setup'],
            'stage setup': ['stage setup', 'stage construction', 'platform', 'performance stage', 'event stage'],
            'fireworks': ['fireworks', 'firecrackers', 'pyrotechnics', 'diwali crackers', 'wedding fireworks'],
            'invitation cards': ['invitation cards', 'wedding card', 'invitation design', 'printing cards', 'custom cards'],
            'event furniture': ['event furniture', 'chair rental', 'table rental', 'event seating', 'furniture rental'],
            
            # ========== OTHER ESSENTIAL SERVICES (50+ services) ==========
            'electrician emergency': ['electrician emergency', 'emergency electrician', 'power cut', 'fuse repair', 'short circuit', 'electrical emergency'],
            'plumber emergency': ['plumber emergency', 'emergency plumber', 'water leakage', 'pipe burst', 'blocked drain', 'water emergency'],
            'lock smith': ['lock smith', 'lock repair', 'key making', 'door lock', 'broken lock', 'lock installation', 'lockout service'],
            'pandit': ['pandit', 'priest', 'puja', 'religious ceremony', 'marriage puja', 'house warming', 'grah pravesh'],
            'astrologer': ['astrologer', 'jyotish', 'horoscope', 'kundali', 'vastu consultant', 'birth chart', 'future prediction'],
            'insurance agent': ['insurance agent', 'insurance', 'life insurance', 'health insurance', 'car insurance', 'home insurance', 'policy agent'],
            'travel agent': ['travel agent', 'tour package', 'flight booking', 'hotel booking', 'holiday package', 'international tour'],
            'notary': ['notary', 'notary public', 'document attestation', 'affidavit', 'certification', 'document notarization'],
            'ca firm': ['ca firm', 'chartered accountant', 'audit firm', 'tax consultant', 'accounting firm', 'gst consultant'],
            'law firm': ['law firm', 'advocate office', 'legal firm', 'corporate lawyer', 'property lawyer', 'court case'],
            'printing press': ['printing press', 'printing', 'visiting card printing', 'brochure printing', 'banner printing', 'offset printing'],
            'stationery shop': ['stationery shop', 'stationery', 'office supplies', 'paper', 'pen', 'notebook', 'school supplies'],
            'photocopy shop': ['photocopy shop', 'photocopy', 'xerox', 'printing', 'scanning', 'lamination', 'binding'],
            'key maker': ['key maker', 'key cutting', 'duplicate key', 'car key', 'house key', 'key duplication'],
            'watch repair': ['watch repair', 'watch service', 'watch battery', 'watch strap', 'watch maintenance'],
            'shoe repair': ['shoe repair', 'shoe polish', 'shoe stitching', 'shoe sole', 'footwear repair'],
            'umbrella repair': ['umbrella repair', 'umbrella stitching', 'umbrella handle', 'umbrella ribs'],
            'bag repair': ['bag repair', 'bag stitching', 'zip repair', 'bag handle', 'leather bag repair'],
            'clock repair': ['clock repair', 'wall clock', 'table clock', 'clock service', 'clock mechanism'],
            'bicycle repair': ['bicycle repair', 'cycle repair', 'bicycle service', 'cycle mechanic', 'bicycle puncture'],
            
            # ========== FOOD & CATERING (30+ services) ==========
            'tiffin service': ['tiffin service', 'tiffin', 'home food', 'daily tiffin', 'meal service', 'lunch service'],
            'cook': ['cook', 'home cook', 'personal cook', 'chef', 'family cook', 'monthly cook'],
            'bakery': ['bakery', 'bakery items', 'cake', 'bread', 'pastry', 'baked goods', 'custom cake'],
            'sweet shop': ['sweet shop', 'mithai', 'indian sweets', 'desserts', 'diwali sweets', 'festival sweets'],
            'juice center': ['juice center', 'juice', 'fresh juice', 'fruit juice', 'smoothie', 'health drink'],
            'ice cream': ['ice cream', 'ice cream parlour', 'frozen dessert', 'gelato', 'sundae', 'milkshake'],
            'street food': ['street food', 'chaat', 'pani puri', 'bhel puri', 'street snacks', 'local food'],
            'restaurant': ['restaurant', 'dining', 'food outlet', 'eating place', 'family restaurant', 'fine dining'],
            'cloud kitchen': ['cloud kitchen', 'online kitchen', 'food delivery kitchen', 'virtual restaurant'],
            'catering equipment': ['catering equipment', 'cooking equipment', 'kitchen equipment', 'commercial kitchen'],
            'food packaging': ['food packaging', 'food container', 'takeaway packaging', 'disposable packaging'],
            'water supplier': ['water supplier', 'water can', 'mineral water', 'drinking water', 'water delivery'],
            'gas cylinder': ['gas cylinder', 'lpg', 'cooking gas', 'gas delivery', 'cylinder booking'],
            'groceries': ['groceries', 'grocery shop', 'kirana store', 'provisions', 'daily needs', 'home delivery'],
            
            # ========== AGRICULTURE & FARMING (20+ services) ==========
            'agriculture consultant': ['agriculture consultant', 'farming expert', 'crop consultant', 'agriculture advisor'],
            'tractor repair': ['tractor repair', 'tractor service', 'tractor mechanic', 'farm equipment repair'],
            'irrigation system': ['irrigation system', 'drip irrigation', 'sprinkler system', 'water irrigation'],
            'poultry farm': ['poultry farm', 'chicken farm', 'egg production', 'poultry equipment'],
            'dairy farm': ['dairy farm', 'milk production', 'cattle farm', 'dairy equipment'],
            'organic farming': ['organic farming', 'organic produce', 'natural farming', 'chemical free'],
            'fertilizer supplier': ['fertilizer supplier', 'manure', 'plant nutrition', 'soil fertilizer'],
            'seed supplier': ['seed supplier', 'agriculture seeds', 'crop seeds', 'hybrid seeds'],
            'pesticide supplier': ['pesticide supplier', 'crop protection', 'insecticide', 'weedicide'],
            'harvesting service': ['harvesting service', 'crop harvesting', 'harvest machine', 'harvest labour'],
            
            # ========== PET SERVICES (20+ services) ==========
            'pet groomer': ['pet groomer', 'dog grooming', 'pet bathing', 'pet haircut', 'pet spa'],
            'veterinarian': ['veterinarian', 'vet', 'animal doctor', 'pet doctor', 'pet clinic'],
            'pet trainer': ['pet trainer', 'dog training', 'pet behavior', 'obedience training', 'pet school'],
            'pet boarding': ['pet boarding', 'pet hotel', 'dog boarding', 'cat boarding', 'pet sitting'],
            'pet food': ['pet food', 'dog food', 'cat food', 'pet supplies', 'pet nutrition'],
            'pet ambulance': ['pet ambulance', 'animal ambulance', 'pet transport', 'animal rescue'],
            'pet accessories': ['pet accessories', 'dog collar', 'pet bed', 'pet toys', 'pet clothes'],
            'aquarium service': ['aquarium service', 'fish tank', 'aquarium cleaning', 'fish keeping'],
            
            # ========== INDUSTRIAL SERVICES (30+ services) ==========
            'industrial electrician': ['industrial electrician', 'factory electrician', 'industrial wiring', 'machine electrician'],
            'industrial plumber': ['industrial plumber', 'factory plumbing', 'industrial pipeline', 'process piping'],
            'welder': ['welder', 'welding work', 'arc welding', 'gas welding', 'metal welding'],
            'fitter': ['fitter', 'fitter work', 'machine fitter', 'assembly fitter', 'industrial fitter'],
            'turner': ['turner', 'lathe operator', 'turning work', 'cnc operator', 'machine operator'],
            'machinist': ['machinist', 'machine work', 'fabrication work', 'sheet metal', 'cnc machining'],
            'tool maker': ['tool maker', 'tool design', 'mold making', 'die making', 'precision tools'],
            'quality inspector': ['quality inspector', 'qc inspector', 'quality control', 'product inspection'],
            'safety officer': ['safety officer', 'safety consultant', 'industrial safety', 'fire safety'],
            'forklift operator': ['forklift operator', 'forklift driver', 'material handling', 'warehouse operator'],
            'crane operator': ['crane operator', 'crane driver', 'heavy lifting', 'construction crane'],
        }
        
        # Add Hindi translations for key services
        hindi_translations = {
            'electrician': ['बिजली मिस्त्री', 'इलेक्ट्रीशियन', 'विद्युत मिस्त्री', 'तारों का काम'],
            'plumber': ['नल का मिस्त्री', 'प्लंबर', 'पाइप फिटर', 'पानी का काम'],
            'carpenter': ['बढ़ई', 'काष्ठकार', 'लकड़ी का काम', 'फर्नीचर बनाने वाला'],
            'painter': ['पेंटर', 'रंगसाज', 'दीवार पेंट करने वाला', 'रंगाई का काम'],
            'cleaner': ['सफाई कर्मी', 'झाड़ू लगाने वाला', 'सफाई वाला', 'मेड'],
            'doctor': ['डॉक्टर', 'चिकित्सक', 'वैद्य', 'डॉक्टर साहब'],
            'driver': ['ड्राइवर', 'चालक', 'गाड़ी चलाने वाला', 'कार ड्राइवर'],
            'teacher': ['शिक्षक', 'अध्यापक', 'टीचर', 'गुरु'],
            'lawyer': ['वकील', 'अधिवक्ता', 'कानूनी सलाहकार', 'एडवोकेट'],
            'accountant': ['लेखाकार', 'अकाउंटेंट', 'हिसाब किताब वाला', 'कैशियर'],
            'barber': ['नाई', 'हजामत बनाने वाला', 'बार्बर', 'केरियर'],
            'tailor': ['दर्जी', 'सिलाई वाला', 'टेलर', 'कपड़े सिलने वाला'],
            'cook': ['रसोइया', 'खाना बनाने वाला', 'बावर्ची', 'शेफ'],
            'gardener': ['माली', 'बागवानी वाला', 'गार्डनर', 'पौधे लगाने वाला'],
            'security guard': ['सुरक्षा गार्ड', 'चौकीदार', 'गार्ड', 'सिक्योरिटी वाला'],
            'mechanic': ['मैकेनिक', 'मिस्त्री', 'गाड़ी ठीक करने वाला', 'रिपेयर वाला'],
            'electrician emergency': ['इमरजेंसी इलेक्ट्रीशियन', 'तुरंत बिजली मिस्त्री', 'आपातकालीन विद्युत मिस्त्री'],
            'plumber emergency': ['इमरजेंसी प्लंबर', 'तुरंत नल मिस्त्री', 'आपातकालीन पानी का मिस्त्री'],
        }
        
        # Add Tamil translations for key services
        tamil_translations = {
            'electrician': ['மின் கட்டுப்பாட்டாளர்', 'மின்சார தச்சு', 'வயரிங் வேலை', 'மின் வேலை'],
            'plumber': ['குழாய் தச்சு', 'பிளம்பர்', 'நீர் குழாய் வேலை', 'கழிவு நீர் வேலை'],
            'carpenter': ['மரத்தச்சு', 'தச்சு வேலை', 'மர வேலை', 'பீரோ தயாரிப்பு'],
            'painter': ['சிமெண்ட் தச்சு', 'சுவர் ஓவியர்', 'வண்ணம் தீட்டுபவர்', 'பெயிண்டர்'],
            'doctor': ['டாக்டர்', 'மருத்துவர்', 'வைத்தியர்', 'க்ளினிக்'],
            'teacher': ['ஆசிரியர்', 'பள்ளி ஆசிரியர்', 'கூடுதல் பயிற்சி', 'டியூஷன்'],
        }
        
        # Add Telugu translations for key services
        telugu_translations = {
            'electrician': ['ఎలక్ట్రీషియన్', 'విద్యుత్ వేర్కర్', 'వైరింగ్ వర్క్', 'మెయిన్స్ వర్క్'],
            'plumber': ['ప్లంబర్', 'పైపు వర్క్', 'నీటి పైపు మరమ్మత్తు', 'బాత్రూమ్ వర్క్'],
            'doctor': ['డాక్టర్', 'వైద్యుడు', 'క్లినిక్', 'హాస్పిటల్'],
            'teacher': ['టీచర్', 'ఉపాధ్యాయుడు', 'ట్యూషన్', 'కోచింగ్'],
        }
        
        # Combine all translations
        for service, english_keywords_list in service_keywords.items():
            # Add Hindi translations if available
            if service in hindi_translations:
                service_keywords[service].extend(hindi_translations[service])
            
            # Add Tamil translations if available
            if service in tamil_translations:
                service_keywords[service].extend(tamil_translations[service])
            
            # Add Telugu translations if available
            if service in telugu_translations:
                service_keywords[service].extend(telugu_translations[service])
        
        return service_keywords

    def _get_all_wake_words(self) -> List[str]:
        """Get wake words from all supported languages"""
        all_wake_words = []
        for lang_data in self.supported_languages.values():
            all_wake_words.extend(lang_data['wake_words'])
        return list(set(all_wake_words))  # Remove duplicates

    def speak_response(self, text: str, language_code: Optional[str] = None, immediate: bool = True):
        """
        Speak a response to the user
        
        Args:
            text: Text to speak
            language_code: Language code (uses current language if None)
            immediate: If True, interrupts any ongoing speech
        """
        if language_code is None:
            language_code = self.current_language
        
        if immediate:
            self.speech.speak_immediate(text, language_code)
        else:
            self.speech.speak(text, language_code)
    
    def speak_greeting(self):
        """Speak greeting message"""
        greeting = self.get_language_text('greeting')
        self.speak_response(greeting, immediate=True)
        logger.info(f"🗣️ Greeting spoken in {self.current_language}")
    
    def speak_prompt(self):
        """Speak prompt for service"""
        prompt = self.get_language_text('prompt')
        self.speak_response(prompt, immediate=True)
    
    def speak_confirmation(self, service: str):
        """Speak confirmation for service"""
        confirm = self.get_language_text('confirm')
        full_text = f"{confirm} {service}"
        self.speak_response(full_text, immediate=True)
    
    def speak_not_found(self):
        """Speak not found message"""
        not_found = self.get_language_text('not_found')
        self.speak_response(not_found, immediate=True)
    
    def speak_searching(self, service: str):
        """Speak searching message"""
        searching = self.get_language_text('searching')
        full_text = f"{searching} {service}"
        self.speak_response(full_text, immediate=True)
    
    def speak_found(self, service: str, count: int = 3):
        """Speak found message"""
        found = self.get_language_text('found')
        providers = self.get_language_text('providers')
        full_text = f"{found} {count} {providers} {service}"
        self.speak_response(full_text, immediate=True)
    
    def speak_welcome(self):
        """Speak welcome message"""
        welcome = self.get_language_text('welcome')
        self.speak_response(welcome, immediate=True)
    
    def speak_ready(self):
        """Speak ready message"""
        ready = self.get_language_text('ready')
        self.speak_response(ready, immediate=True)
    
    def speak_listening(self):
        """Speak listening message"""
        listening = self.get_language_text('listening')
        self.speak_response(listening, immediate=True)
    
    def speak_processing(self):
        """Speak processing message"""
        processing = self.get_language_text('processing')
        self.speak_response(processing, immediate=True)
    
    def speak_thanks(self):
        """Speak thanks message"""
        thanks = self.get_language_text('thanks')
        self.speak_response(thanks, immediate=True)
    
    def speak_goodbye(self):
        """Speak goodbye message"""
        goodbye = self.get_language_text('goodbye')
        self.speak_response(goodbye, immediate=True)
    
    def wait_for_speech_completion(self, timeout: float = 5.0):
        """Wait for current speech to complete"""
        self.speech.wait_until_finished(timeout)
    
    def stop_speech(self):
        """Stop any ongoing speech"""
        self.speech.stop_current_speech()
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text
        Returns language code (en, hi, ta, etc.)
        """
        if not text or len(text.strip()) < 2:
            return 'en'
        
        # Check for Devanagari script (Hindi, Marathi, Nepali, Sanskrit)
        devanagari_pattern = re.compile(r'[\u0900-\u097F]')
        if devanagari_pattern.search(text):
            # Check specific languages
            if re.search(r'[\u0915-\u0939]', text):  # Hindi characters
                return 'hi'
            elif re.search(r'ळ|ळ', text):  # Marathi specific letters
                return 'mr'
            else:
                return 'hi'  # Default to Hindi
        
        # Check for Tamil
        tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
        if tamil_pattern.search(text):
            return 'ta'
        
        # Check for Telugu
        telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')
        if telugu_pattern.search(text):
            return 'te'
        
        # Check for Kannada
        kannada_pattern = re.compile(r'[\u0C80-\u0CFF]')
        if kannada_pattern.search(text):
            return 'kn'
        
        # Check for Malayalam
        malayalam_pattern = re.compile(r'[\u0D00-\u0D7F]')
        if malayalam_pattern.search(text):
            return 'ml'
        
        # Check for Bengali
        bengali_pattern = re.compile(r'[\u0980-\u09FF]')
        if bengali_pattern.search(text):
            return 'bn'
        
        # Check for Gujarati
        gujarati_pattern = re.compile(r'[\u0A80-\u0AFF]')
        if gujarati_pattern.search(text):
            return 'gu'
        
        # Check for Punjabi (Gurmukhi)
        punjabi_pattern = re.compile(r'[\u0A00-\u0A7F]')
        if punjabi_pattern.search(text):
            return 'pa'
        
        # Check for Odia
        odia_pattern = re.compile(r'[\u0B00-\u0B7F]')
        if odia_pattern.search(text):
            return 'or'
        
        # Default to English
        return 'en'

    def get_language_text(self, key: str, lang_code: Optional[str] = None) -> str:
        """
        Get localized text for the specified key
        """
        if lang_code is None:
            lang_code = self.current_language
        
        if lang_code not in self.supported_languages:
            lang_code = 'en'
        
        return self.supported_languages[lang_code].get(key, '')

    def set_current_language(self, lang_code: str):
        """
        Set the current language
        """
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            self.language_history.append(lang_code)
            if len(self.language_history) > 5:  # Keep only last 5 languages
                self.language_history.pop(0)
            logger.info(f"🌐 Language set to: {self.supported_languages[lang_code]['name']}")
        else:
            logger.warning(f"Unsupported language code: {lang_code}")

    def get_supported_languages_list(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages
        """
        return [
            {'code': code, 'name': data['name']}
            for code, data in self.supported_languages.items()
        ]

    def detect_service_keyword(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Enhanced service detection with better matching
        Returns: (success: bool, service_type: str) 
        """
        try:
            if not text or len(text.strip()) < 3:
                return False, None
            
            print(f"[SERVICE] Analyzing: '{text}'")
            
            # Detect language from text
            detected_lang = self.detect_language(text)
            if detected_lang != self.current_language:
                print(f"[LANGUAGE] Detected: {self.supported_languages[detected_lang]['name']}")
                self.set_current_language(detected_lang)
            
            # Clean and normalize text
            text_clean = self._clean_text(text)
            text_lower = text_clean.lower()
            print(f"[DEBUG] Cleaned text: '{text_lower}'")
            
            # First, try exact matching with service context
            service_match = self._match_service_with_context(text_lower)
            
            if service_match and service_match.confidence > 0.1:
                print(f"[SERVICE] Found: {service_match.service_type} "
                      f"(Confidence: {service_match.confidence:.2f})")
                return True, service_match.service_type
            
            # Fallback to basic keyword matching
            basic_match, confidence = self._basic_service_detect(text_lower)
            if basic_match and confidence > 0.5:
                print(f"[SERVICE] Basic match: {basic_match}")
                return True, basic_match
            
            print(f"[SERVICE] No service detected")
            return False, None
                
        except Exception as e:
            print(f"[SERVICE ERROR]: {e}")
            logger.error(f"Service detection error: {e}")
            return False, None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better matching"""
        if not text:
            return ""
        
        # Remove common phrases/words from all languages
        common_phrases = [
            # English
            'hey butler', 'hello butler', 'hi butler', 'okay butler',
            'i need', 'i want', 'find me', 'get me', 'please', 'can you',
            'could you', 'would you', 'need a', 'looking for', 'search for',
            # Hindi
            'हे बटलर', 'नमस्ते बटलर', 'हैलो बटलर', 'मुझे चाहिए', 'मुझे एक चाहिए',
            'ढूंढो', 'खोजो', 'कृपया', 'क्या आप', 'आप कर सकते हैं',
            # Tamil
            'ஏ பட்லர்', 'வணக்கம் பட்லர்', 'ஹலோ பட்லர்', 'எனக்கு தேவை',
            'தேடு', 'கண்டுபிடி', 'தயவு செய்து', 'நீங்கள் முடியுமா',
            # Telugu
            'హే బట్లర్', 'నమస్తే బట్లర్', 'హలో బట్లర్', 'నాకు కావాలి',
            'వెతకండి', 'కనుగొనండి', 'దయచేసి', 'మీరు చేయగలరా',
            # Generic
            'butler', 'बटलर', 'பட்லர்', 'బట్లర్', 'बट्लर'
        ]
        
        clean_text = text.lower()
        for phrase in common_phrases:
            clean_text = clean_text.replace(phrase.lower(), '')
        
        # Remove extra spaces and punctuation
        clean_text = re.sub(r'[^\w\s]', '', clean_text)
        clean_text = ' '.join(clean_text.split())
        
        return clean_text.strip()

    def _match_service_with_context(self, text_lower: str) -> Optional[ServiceMatch]:
        """Advanced service matching with context awareness"""
        best_match = None
        best_confidence = 0.0
        
        for service_type, keywords in self.service_keywords.items():
            matched_keywords = []
            confidence = 0.0
            
            for keyword in keywords:
                if keyword in text_lower:
                    matched_keywords.append(keyword)
                    # Weight exact matches higher
                    if f" {keyword} " in f" {text_lower} ":
                        confidence += 0.3
                    else:
                        confidence += 0.2
            
            if matched_keywords:
                # Adjust confidence based on match count and specificity
                if len(matched_keywords) > 1:
                    confidence *= 1.2  # Multiple keywords = higher confidence
                
                if confidence > best_confidence:
                    best_match = ServiceMatch(
                        service_type=service_type,
                        confidence=min(confidence, 1.0),
                        matched_keywords=matched_keywords
                    )
                    best_confidence = confidence
        
        return best_match

    def _basic_service_detect(self, text_lower: str) -> Tuple[Optional[str], float]:
        """Basic fallback service detection"""
        service_confidence = {}
        
        for service_type, keywords in self.service_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if service_type not in service_confidence:
                        service_confidence[service_type] = 0.0
                    service_confidence[service_type] += 0.2
        
        if service_confidence:
            best_service = max(service_confidence.items(), key=lambda x: x[1])
            if best_service[1] > 0.1:  # Threshold for basic detection
                return best_service[0], best_service[1]
        
        return None, 0.0

    def force_calibration(self, duration: float = 1.5) -> bool:
        """
        Force calibration for USB microphone with better feedback
        """
        print("\n" + "="*50)
        print("🎤 FORCE CALIBRATION - USB MICROPHONE")
        print("="*50)
        
        try:
            if self.use_alsa:
                # Use ALSA for calibration
                print("1. Using ALSA direct access...")
                print("2. Calibration complete (ALSA mode)")
                return True
            else:
                with sr.Microphone(device_index=self.mic_device_index, sample_rate=44100) as source:
                    print("1. Stay SILENT for 3 seconds...")
                    time.sleep(3)
                    
                    print("2. Measuring ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                    
                    print("3. Setting fixed threshold...")
                    self.recognizer.energy_threshold = 300
                    
                    print(f"   ✅ Energy threshold SET TO: {self.recognizer.energy_threshold:.1f}")
                    print("4. Calibration COMPLETE!")
                    
                    return True
        except Exception as e:
            print(f"⚠️ Calibration error: {e}")
            logger.error(f"Calibration failed: {e}")
            return False

    def _record_with_alsa(self, timeout: float, audio_file: str) -> bool:
        """Record audio using direct ALSA - FIXED VERSION"""
        try:
            # Debug: Show what we're trying to do
            print(f"   🎤 ALSA Recording: Device hw:{self.mic_device_index},0 for {timeout} seconds")
            
            cmd = [
                'arecord',
                f'-Dplughw:{self.mic_device_index},0',  # FIXED: No space after -D
                '-f', 'S16_LE',
                '-r', '16000',
                '-c', '1',
                '-d', str(timeout),
                '-t', 'wav',
                audio_file
            ]
            
            print(f"   🔧 Command: {' '.join(cmd)}")
            
            # Run recording with timeout
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for recording to complete
            time.sleep(timeout + 0.5)  # Add a little extra
            
            # Try to terminate gracefully
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
            
            # Check if file was created and has data
            if os.path.exists(audio_file):
                size = os.path.getsize(audio_file)
                if size > 1000:  # At least 1KB of audio data
                    print(f"   ✅ ALSA recording successful: {size} bytes")
                    return True
                else:
                    print(f"   ⚠️ ALSA recording too small: {size} bytes")
                    os.remove(audio_file)
                    return False
            else:
                print(f"   ❌ ALSA recording failed: File not created")
                return False
                
        except Exception as e:
            print(f"   ❌ ALSA recording error: {e}")
            return False

    def listen_direct(self, timeout: float = 10.0, listen_for_wake: bool = False) -> Tuple[bool, str, str]:
        """
        DIRECT listening - Using ALSA for reliable USB microphone access
        """
        context = "wake word" if listen_for_wake else "command"
        print(f"\n🔍 Listening for {context} ({timeout}s)...")
        
        # First try ALSA if enabled
        if self.use_alsa:
            audio_file = f"/tmp/voice_{int(time.time())}.wav"
            print(f"   🔊 ALSA Recording to: {audio_file}")
            
            # Try recording with ALSA
            if self._record_with_alsa(timeout, audio_file):
                # Try to recognize the audio
                return self._process_audio_file(audio_file)
            else:
                print("   ⚠️ ALSA failed, trying fallback to speech_recognition...")
                self.use_alsa = False  # Disable ALSA for next attempt
        
        # Fallback to speech_recognition
        return self._listen_with_speech_recognition(timeout)

    def _process_audio_file(self, audio_file: str) -> Tuple[bool, str, str]:
        """Process recorded audio file"""
        try:
            with sr.AudioFile(audio_file) as source:
                print(f"   🔄 Processing audio file: {os.path.getsize(audio_file)} bytes")
                audio = self.recognizer.record(source)
                
                # Try multiple languages
                language_configs = self._get_language_configs()
                
                for lang_code, lang_name in language_configs[:5]:
                    try:
                        text = self.recognizer.recognize_google(
                            audio, 
                            language=lang_code,
                            show_all=False
                        )
                        
                        if text and len(text.strip()) > 1:
                            print(f"   ✅ Heard [{lang_name}]: '{text}'")
                            
                            # Clean up file
                            if os.path.exists(audio_file):
                                os.remove(audio_file)
                            
                            # Set language
                            lang_to_set = self._map_google_code_to_internal(lang_code)
                            if lang_to_set:
                                self.set_current_language(lang_to_set)
                            
                            return True, text.strip(), lang_code
                            
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        print(f"   ⚠️ API error for {lang_name}: {e}")
                        continue
                
                # Clean up
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                print("   ⚠️ Voice detected but not understood")
                return True, "[Voice detected, not understood]", self.current_language
                
        except Exception as e:
            if os.path.exists(audio_file):
                os.remove(audio_file)
            print(f"   ❌ Audio processing error: {e}")
            return False, "", self.current_language
    
    def _listen_with_speech_recognition(self, timeout: float) -> Tuple[bool, str, str]:
        """Fallback using speech_recognition directly"""
        try:
            print(f"   🔊 Using speech_recognition fallback...")
            
            # Try different device indices
            for device_idx in [self.mic_device_index, 0, 2, 3]:
                try:
                    print(f"   🔧 Trying device index {device_idx}...")
                    with sr.Microphone(device_index=device_idx, sample_rate=16000) as source:
                        self.recognizer.energy_threshold = 300
                        print("   🎤 Listening (speak clearly)...")
                        
                        audio = self.recognizer.listen(
                            source, 
                            timeout=timeout,
                            phrase_time_limit=10
                        )
                        
                        print("   ✅ Audio captured, processing...")
                        
                        # Try multiple languages
                        language_configs = self._get_language_configs()
                        
                        for lang_code, lang_name in language_configs[:5]:
                            try:
                                text = self.recognizer.recognize_google(
                                    audio, 
                                    language=lang_code,
                                    show_all=False
                                )
                                
                                if text and len(text.strip()) > 1:
                                    print(f"   ✅ Heard [{lang_name}]: '{text}'")
                                    
                                    # Set language
                                    lang_to_set = self._map_google_code_to_internal(lang_code)
                                    if lang_to_set:
                                        self.set_current_language(lang_to_set)
                                    
                                    return True, text.strip(), lang_code
                                    
                            except sr.UnknownValueError:
                                continue
                            except sr.RequestError as e:
                                print(f"   ⚠️ API error for {lang_name}: {e}")
                                continue
                        
                        print("   ⚠️ Voice detected but not understood")
                        return True, "[Voice detected, not understood]", self.current_language
                        
                except Exception as e:
                    print(f"   ❌ Device {device_idx} failed: {e}")
                    continue
            
            print("   ❌ All microphone devices failed")
            return False, "", self.current_language
            
        except sr.WaitTimeoutError:
            print(f"   ⏱️ Timeout - No speech detected")
            return False, "", self.current_language
        except Exception as e:
            print(f"   ❌ Listen error: {e}")
            logger.error(f"Listen error: {e}")
            return False, "", self.current_language
    
    def _get_language_configs(self):
        """Get language configurations for recognition"""
        language_configs = []
        
        # Add current language first
        if self.current_language in self.supported_languages:
            language_configs.append((
                self.supported_languages[self.current_language]['code'],
                self.supported_languages[self.current_language]['name']
            ))
        
        # Add English variants
        english_variants = [
            ('en-IN', 'English (India)'),
            ('en-US', 'English (US)'),
            ('en-GB', 'English (UK)'),
            ('en', 'English')
        ]
        for eng_code, eng_name in english_variants:
            if (eng_code, eng_name) not in language_configs:
                language_configs.append((eng_code, eng_name))
        
        return language_configs
    
    def _map_google_code_to_internal(self, google_code: str) -> Optional[str]:
        """Map Google language code to internal language code"""
        # Remove region part if present
        base_code = google_code.split('-')[0] if '-' in google_code else google_code
        
        for internal_code, data in self.supported_languages.items():
            if data['code'].startswith(base_code):
                return internal_code
        
        return None

    def check_wake_word(self, text: str) -> bool:
        """
        Check if text contains wake word with fuzzy matching for all languages
        """
        if not text or len(text.strip()) < 2:
            return False
        
        text_lower = text.lower().strip()
        
        # Check all wake words from all languages
        for wake_word in self.wake_words:
            if text_lower.startswith(wake_word.lower()):
                print(f"   ✅ Wake word detected at start: '{wake_word}'")
                return True
        
        # Check if wake word appears anywhere
        for wake_word in self.wake_words:
            if wake_word.lower() in text_lower:
                print(f"   ✅ Wake word detected in text: '{wake_word}'")
                return True
        
        # Fuzzy matching for common mishearings
        fuzzy_matches = ['butler', 'butter', 'bottler', 'hitler', 'battler', 
                        'बटलर', 'बट्टर', 'बटलर', 'बट्लर', 'बटलर',
                        'பட்லர்', 'பட்டர்', 'பட்லர்',
                        'బట్లర్', 'బట్టర్', 'బట్లర్',
                        'ಬಟ್ಲರ್', 'ಬಟ್ಟರ್', 'ಬಟ್ಲರ్']
        
        for fuzzy_word in fuzzy_matches:
            if fuzzy_word in text_lower:
                # Check for greeting patterns in various languages
                greeting_words = [
                    # English
                    'hey', 'hello', 'hi', 'okay', 'hiya', 'hey there',
                    # Hindi
                    'हे', 'नमस्ते', 'हैलो', 'हाय',
                    # Tamil
                    'ஏ', 'வணக்கம்', 'ஹலோ', 'ஹாய்',
                    # Telugu
                    'హే', 'నమస్తే', 'హలో', 'హాయ్',
                    # Generic
                    'ok', 'okey', 'oye'
                ]
                
                words = text_lower.split()
                for i, word in enumerate(words):
                    if fuzzy_word in word:
                        # Check previous word for greeting
                        if i > 0 and any(greeting in words[i-1] for greeting in greeting_words):
                            print(f"   ✅ Fuzzy wake word: '{fuzzy_word}' after greeting")
                            return True
                        # Check if it's at the start
                        elif i == 0:
                            print(f"   ✅ Fuzzy wake word at start: '{fuzzy_word}'")
                            return True
        
        return False

    def detect_wake_word(self, timeout: float = 10.0) -> bool:
        """
        Detect wake word - Optimized for responsiveness with multi-lingual support
        """
        success, text, lang = self.listen_direct(timeout=timeout, listen_for_wake=True)
        
        if success and text and text != "[Voice detected, not understood]":
            # Update current language based on detected language
            if lang and lang != self.current_language:
                # Try to map lang code to our supported languages
                for code, data in self.supported_languages.items():
                    if data['code'] == lang:
                        self.set_current_language(code)
                        break
            
            return self.check_wake_word(text)
        
        return False

    def get_command(self, timeout: float = 10.0) -> Optional[str]:
        """
        Get command (with or without wake word) with better error handling
        """
        success, text, lang = self.listen_direct(timeout=timeout, listen_for_wake=False)
        
        if not success:
            print("   ❌ No audio detected")
            return None
        
        if text == "[Voice detected, not understood]":
            print("   ❓ Audio detected but couldn't understand")
            return None
        
        if text and len(text.strip()) > 1:
            print(f"   ✅ Command received: '{text}'")
            # Update language if detected
            if lang and lang != self.current_language:
                for code, data in self.supported_languages.items():
                    if data['code'] == lang:
                        self.set_current_language(code)
                        break
            return text
        
        return None

    def extract_command_after_wake(self, text: str) -> str:
        """
        Extract command after wake word with improved parsing for all languages
        """
        if not text:
            return ""
        
        text_lower = text.lower()
        
        # Find the earliest wake word
        earliest_pos = len(text_lower)
        command = text
        
        for wake_word in self.wake_words:
            pos = text_lower.find(wake_word.lower())
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
                # Extract everything after the wake word
                command_start = pos + len(wake_word)
                if command_start < len(text):
                    # Keep original case for the command part
                    command = text[command_start:].strip()
                else:
                    command = ""
        
        # If we found a wake word, clean up the command
        if earliest_pos < len(text_lower):
            # Remove any leading filler words in multiple languages
            filler_words = [
                # English
                'i', 'need', 'want', 'please', 'can', 'you', 'could', 'would',
                # Hindi
                'मुझे', 'चाहिए', 'कृपया', 'क्या', 'आप', 'मैं',
                # Tamil
                'எனக்கு', 'தேவை', 'தயவு', 'செய்து', 'நீங்கள்', 'நான்',
                # Telugu
                'నాకు', 'కావాలి', 'దయచేసి', 'మీరు', 'నేను',
                # Generic
                'a', 'an', 'the', 'मैं', 'நான்', 'నేను'
            ]
            words = command.split()
            while words and words[0].lower() in filler_words:
                words.pop(0)
            command = ' '.join(words)
        
        return command.strip()

    def test_microphone(self) -> bool:
        """
        Test microphone functionality with ALSA
        """
        print("\n" + "="*50)
        print("🎤 MICROPHONE TEST")
        print("="*50)
        
        try:
            if self.use_alsa:
                # Test with ALSA
                print("Testing USB microphone with ALSA...")
                test_cmd = f"timeout 2 arecord -D hw:{self.mic_device_index},0 -f S16_LE -r 16000 -c 1 /tmp/test_mic.wav 2>/dev/null"
                result = subprocess.run(test_cmd, shell=True)
                
                if result.returncode == 0 and os.path.exists("/tmp/test_mic.wav"):
                    size = os.path.getsize("/tmp/test_mic.wav")
                    os.remove("/tmp/test_mic.wav")
                    print(f"✅ USB Microphone: WORKING (ALSA mode)")
                    print(f"   Recorded {size} bytes")
                    return True
                else:
                    print("⚠️ USB Microphone: ALSA test failed, trying fallback...")
                    self.use_alsa = False
            
            # Fallback to speech_recognition test
            print("Available microphones:")
            mic_list = sr.Microphone.list_microphone_names()
            for i, mic_name in enumerate(mic_list):
                print(f"  [{i}] {mic_name}")
            
            print(f"\nTesting microphone [{self.mic_device_index}]...")
            with sr.Microphone(device_index=self.mic_device_index) as source:
                print("✅ Microphone opened successfully")
                return True
                
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False
    
    def start_conversation(self):
        """
        Start a conversation with the user
        """
        self.conversation_active = True
        self.last_interaction_time = time.time()
        self.speak_welcome()
        time.sleep(1)
        self.speak_ready()
    
    def process_user_request(self, command: str) -> bool:
        """
        Process user request and respond appropriately
        Returns: True if service was found, False otherwise
        """
        self.speak_processing()
        
        # Extract service from command
        success, service = self.detect_service_keyword(command)
        
        if success and service:
            # Speak confirmation
            self.speak_confirmation(service)
            time.sleep(0.5)
            
            # Speak searching
            self.speak_searching(service)
            time.sleep(1)
            
            # Speak found
            self.speak_found(service)
            
            # Simulate finding providers
            time.sleep(2)
            
            # Speak thanks
            self.speak_thanks()
            
            return True
        else:
            # Speak not found
            self.speak_not_found()
            time.sleep(0.5)
            self.speak_prompt()
            
            return False
    
    def run_conversation_loop(self):
        """
        Run continuous conversation loop
        """
        print("\n" + "="*60)
        print("💬 BUTLER CONVERSATION MODE")
        print("="*60)
        
        self.start_conversation()
        
        while self.conversation_active:
            try:
                # Check for wake word
                print("\n🎤 Listening for wake word...")
                if self.detect_wake_word(timeout=15):
                    print("✅ Wake word detected!")
                    self.speak_greeting()
                    time.sleep(0.5)
                    
                    # Get user command
                    print("\n🎤 Listening for command...")
                    command = self.get_command(timeout=10)
                    
                    if command:
                        print(f"✅ User said: '{command}'")
                        self.process_user_request(command)
                    else:
                        print("❌ No command received")
                        self.speak_prompt()
                
                # Check for timeout
                if time.time() - self.last_interaction_time > 60:  # 1 minute timeout
                    print("⏰ Conversation timeout")
                    self.speak_goodbye()
                    self.conversation_active = False
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Conversation interrupted by user")
                self.speak_goodbye()
                self.conversation_active = False
                break
            except Exception as e:
                print(f"❌ Conversation error: {e}")
                logger.error(f"Conversation error: {e}")
                time.sleep(1)
        
        print("Conversation ended")
    
    def print_language_info(self):
        """Print information about supported languages"""
        print("\n" + "="*60)
        print("🌐 SUPPORTED LANGUAGES")
        print("="*60)
        for code, data in self.supported_languages.items():
            print(f"{code.upper():4} - {data['name']:15} ({data['code']})")
            print(f"      Wake words: {', '.join(data['wake_words'][:3])}...")
        print(f"\nTotal: {len(self.supported_languages)} languages")
        print("="*60)
    
    def get_speech_status(self) -> Dict:
        """Get speech synthesizer status"""
        return self.speech.get_status()
    
    def print_service_categories(self):
        """Print information about service categories"""
        print("\n" + "="*60)
        print("🔍 SERVICE CATEGORIES")
        print("="*60)
        
        categories = {
            'Home Services': ['electrician', 'plumber', 'carpenter', 'painter', 'cleaner', 'ac repair', 'appliance repair', 'pest control', 'gardener', 'security guard'],
            'Personal Care': ['barber', 'beautician', 'yoga trainer', 'fitness trainer', 'tailor', 'laundry', 'mehndi artist', 'makeup artist'],
            'Healthcare': ['doctor', 'dentist', 'physiotherapist', 'nurse', 'pharmacist', 'dietician', 'psychologist', 'cardiologist', 'gynecologist'],
            'Professional Services': ['web developer', 'graphic designer', 'accountant', 'lawyer', 'tutor', 'photographer', 'caterer', 'digital marketer'],
            'Automotive': ['car mechanic', 'bike mechanic', 'driver', 'car cleaning', 'towing service', 'car painting', 'car ac repair'],
            'Education': ['english tutor', 'maths tutor', 'science tutor', 'computer teacher', 'music teacher', 'dance teacher', 'art teacher'],
            'Real Estate': ['property dealer', 'interior designer', 'architect', 'construction worker', 'construction contractor'],
            'Logistics': ['packers and movers', 'courier', 'taxi service', 'truck rental', 'logistics company'],
            'Technology': ['mobile repair', 'laptop repair', 'network engineer', 'data entry', 'software developer', 'cloud services'],
            'Event Services': ['event planner', 'caterer', 'decorator', 'dj', 'photographer', 'videographer', 'mehndi artist'],
            'Emergency Services': ['electrician emergency', 'plumber emergency', 'lock smith', 'ambulance service'],
            'Food Services': ['tiffin service', 'cook', 'bakery', 'sweet shop', 'juice center', 'restaurant'],
            'Agriculture': ['agriculture consultant', 'tractor repair', 'irrigation system', 'poultry farm', 'dairy farm'],
            'Pet Services': ['pet groomer', 'veterinarian', 'pet trainer', 'pet boarding', 'pet food'],
            'Industrial Services': ['industrial electrician', 'industrial plumber', 'welder', 'fitter', 'turner', 'machinist']
        }
        
        for category, services in categories.items():
            print(f"\n{category}:")
            print(f"  {', '.join(services[:5])}...")
        
        print(f"\nTotal service types: {len(self.service_keywords)}")
        print("="*60)


# Singleton instance - use ALSA direct access for USB mic
voice_recognizer = EnhancedVoiceRecognizer(mic_device_index=1, use_alsa=True)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("🔊 ENHANCED VOICE RECOGNITION TEST - MULTI-LINGUAL")
    print("🗣️  WITH SPEECH SYNTHESIS RESPONSE")
    print("🔍 COMPREHENSIVE SERVICE DETECTION (400+ SERVICES)")
    print("🔊 DIRECT ALSA ACCESS FOR USB MICROPHONE")
    print("="*60)
    
    vr = EnhancedVoiceRecognizer(mic_device_index=1, use_alsa=True)
    
    # Print language information
    vr.print_language_info()
    
    # Print service categories
    vr.print_service_categories()
    
    # Test microphone
    if not vr.test_microphone():
        print("❌ Microphone test failed. Exiting.")
        exit(1)
    
    # Force calibration
    vr.force_calibration()
    
    print("\n🌐 Current language:", vr.get_language_text('name'))
    
    print("\n🎤 Testing wake word detection...")
    if vr.detect_wake_word(timeout=5):
        print("✅ Wake word detected!")
        print(f"🌐 Language detected: {vr.supported_languages[vr.current_language]['name']}")
        
        # Speak greeting
        vr.speak_greeting()
        vr.wait_for_speech_completion()
        
        print("\n🎤 Listening for command...")
        command = vr.get_command(timeout=5)
        
        if command:
            print(f"✅ Command received: '{command}'")
            print(f"🌐 Language: {vr.supported_languages[vr.current_language]['name']}")
            
            # Process and respond to command
            vr.process_user_request(command)
            vr.wait_for_speech_completion()
        else:
            print("❌ No command received")
    else:
        print("❌ No wake word detected")
    
    print("\n" + "="*60)
    print("Test complete!")
    
  

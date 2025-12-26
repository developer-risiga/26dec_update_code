import speech_recognition as sr

def get_pi_recognizer():
    """Get recognizer optimized for Raspberry Pi"""
    r = sr.Recognizer()
    
    # Pi-specific settings
    r.energy_threshold = 5000  # Higher for Pi (more background noise)
    r.dynamic_energy_threshold = False
    r.pause_threshold = 1.5
    r.non_speaking_duration = 0.5
    r.phrase_threshold = 0.3
    
    return r
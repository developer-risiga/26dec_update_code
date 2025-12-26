# utils/monitoring.py
import time
import speech_recognition as sr

class PerformanceMonitor:
    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.total_requests = 0
        
    def record_response_time(self, start_time: float):
        response_time = time.time() - start_time
        self.response_times.append(response_time)
        # Keep only last 100 measurements
        if len(self.response_times) > 100:
            self.response_times.pop(0)
            
    def get_average_latency(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

class HealthCheck:
    async def check_microphone(self) -> bool:
        try:
            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                test_audio = recognizer.listen(source, timeout=2)
                return test_audio is not None
        except:
            return False

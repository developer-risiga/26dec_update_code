# device/display_interface.py
import logging
import tkinter as tk
from tkinter import ttk
import threading
import time

logger = logging.getLogger(__name__)

class DisplayInterface:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.root = None
        self.is_running = False
        self.current_screen = None
        
    def start_display(self) -> bool:
        """Start the display interface"""
        if not self.device_manager.display_available:
            logger.warning("Display not available - running in headless mode")
            return False
        
        try:
            display_thread = threading.Thread(target=self._run_display, daemon=True)
            display_thread.start()
            time.sleep(1)
            self.is_running = True
            logger.info("Display interface started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start display: {e}")
            return False
    
    def _run_display(self):
        """Run the display interface in separate thread"""
        try:
            self.root = tk.Tk()
            self.root.title("Butler Voice Assistant")
            self.root.geometry("800x480")
            self.root.configure(bg='#2c3e50')
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            
            self._create_main_screen()
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Display runtime error: {e}")
    
    def _create_main_screen(self):
        """Create the main interface screen"""
        if self.current_screen:
            self.current_screen.destroy()
        
        self.current_screen = tk.Frame(self.root, bg='#2c3e50')
        self.current_screen.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Label(self.current_screen, text="Butler Voice Assistant", 
                         font=('Arial', 24, 'bold'), bg='#2c3e50', fg='white')
        header.pack(pady=20)
        
        # Status
        status = tk.Label(self.current_screen, text="🎤 Ready to listen", 
                         font=('Arial', 16), bg='#2c3e50', fg='#ecf0f1')
        status.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.current_screen, 
                               text="Say 'electrician', 'plumber' or touch below", 
                               font=('Arial', 14), bg='#2c3e50', fg='#bdc3c7')
        instructions.pack(pady=20)
        
        # Action buttons
        button_frame = tk.Frame(self.current_screen, bg='#2c3e50')
        button_frame.pack(pady=30)
        
        electrician_btn = tk.Button(button_frame, text="⚡ Electrician", 
                                   font=('Arial', 14), bg='#e74c3c', fg='white',
                                   width=15, height=2,
                                   command=self._on_electrician)
        electrician_btn.pack(side=tk.LEFT, padx=10)
        
        plumber_btn = tk.Button(button_frame, text="💧 Plumber", 
                               font=('Arial', 14), bg='#3498db', fg='white',
                               width=15, height=2,
                               command=self._on_plumber)
        plumber_btn.pack(side=tk.LEFT, padx=10)
    
    def _on_electrician(self):
        """Handle electrician button press"""
        logger.info("Electrician service requested via touch")
        self.show_booking_screen("electrician")
    
    def _on_plumber(self):
        """Handle plumber button press"""
        logger.info("Plumber service requested via touch")
        self.show_booking_screen("plumber")
    
    def _on_close(self):
        """Handle window close"""
        self.is_running = False
        if self.root:
            self.root.quit()
    
    def show_booking_screen(self, service_type: str):
        """Show booking confirmation screen"""
        if not self.root:
            return
        
        def update_screen():
            if self.current_screen:
                self.current_screen.destroy()
            
            self.current_screen = tk.Frame(self.root, bg='#2c3e50')
            self.current_screen.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Success icon
            icon = tk.Label(self.current_screen, text="✅", font=('Arial', 48), 
                           bg='#2c3e50', fg='#27ae60')
            icon.pack(pady=20)
            
            # Confirmation text
            confirm_text = tk.Label(self.current_screen, 
                                   text=f"Booking {service_type.title()}...", 
                                   font=('Arial', 20), bg='#2c3e50', fg='white')
            confirm_text.pack(pady=10)
            
            # Details
            details = tk.Label(self.current_screen, 
                              text="Service provider will contact you shortly", 
                              font=('Arial', 14), bg='#2c3e50', fg='#bdc3c7')
            details.pack(pady=10)
            
            # Back button
            back_btn = tk.Button(self.current_screen, text="Back to Main", 
                                font=('Arial', 14), bg='#95a5a6', fg='white',
                                command=self._create_main_screen)
            back_btn.pack(pady=20)
        
        self.root.after(0, update_screen)
    
    def show_error(self, error_message: str):
        """Show error screen"""
        if not self.root:
            logger.error(f"Display error: {error_message}")
            return
        
        def update_screen():
            if self.current_screen:
                self.current_screen.destroy()
            
            self.current_screen = tk.Frame(self.root, bg='#2c3e50')
            self.current_screen.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            error_icon = tk.Label(self.current_screen, text="❌", font=('Arial', 48), 
            bg='#2c3e50', fg='#e74c3c')
            error_icon.pack(pady=20)
            
            error_text = tk.Label(self.current_screen, text=error_message, 
                    font=('Arial', 16), bg='#2c3e50', fg='white',
                    wraplength=600)
            error_text.pack(pady=10)
            
            retry_btn = tk.Button(self.current_screen, text="Retry", 
                    font=('Arial', 14), bg='#e74c3c', fg='white',
                    command=self._create_main_screen)
            retry_btn.pack(pady=20)
        
        self.root.after(0, update_screen)
# run_on_pi.py - Simple Raspberry Pi launcher
import os
import sys

# Add src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import your main application
    from main import main  # If main.py has main() function
    print("✅ Import successful!")
    
    # Run your app
    main()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative import...")
    
    # Alternative: Run main.py directly
    import subprocess
    subprocess.run([sys.executable, "src/main.py"])
#!/usr/bin/env python3
"""
Butler Enterprise - Production Deployment Script
"""

import os
import sys
import asyncio
from datetime import datetime

class ProductionDeployer:
    def __init__(self):
        self.deployment_time = datetime.now()
        
    async def deploy(self):
        print("🚀 BUTLER ENTERPRISE - PRODUCTION DEPLOYMENT")
        print("=" * 50)
        
        steps = [self.step_1_system_check, self.step_2_configuration, self.step_3_api_readiness]
        
        for step in steps:
            success = await step()
            if not success:
                return False
                
        print("🎯 BUTLER ENTERPRISE - PRODUCTION READY!")
        print("💡 System is fully operational without external APIs")
        return True
    
    async def step_1_system_check(self):
        print("📋 Step 1: System Requirements Check...")
        essential_modules = ['aiohttp', 'speechrecognition', 'pygame', 'numpy']
        for module in essential_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module}")
                return False
        return True
    
    async def step_2_configuration(self):
        print("⚙️  Step 2: Production Configuration...")
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from config.config import Config
            config = Config()
            print(f"✅ {config.APP_NAME} v{config.VERSION}")
            return True
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False
    
    async def step_3_api_readiness(self):
        print("🔌 Step 3: API Readiness Check...")
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from config.config import Config
            from api.smart_api_manager import SmartAPIManager
            config = Config()
            api_manager = SmartAPIManager(config)
            print("🤖 Enhanced Intelligence Mode: Active")
            return True
        except Exception as e:
            print(f"❌ API setup error: {e}")
            return False

async def main():
    deployer = ProductionDeployer()
    success = await deployer.deploy()
    
    if success:
        print("\n🚀 Starting Butler Enterprise...")
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from main import main as butler_main
        await butler_main()
    else:
        print("\n❌ DEPLOYMENT FAILED")

if __name__ == "__main__":
    asyncio.run(main())

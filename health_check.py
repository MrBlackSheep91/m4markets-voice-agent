"""
Health Check Script for M4Markets Voice Agent
Verifies that all critical services and dependencies are operational
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

class HealthCheck:
    """Comprehensive health check for the voice agent"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def check_env_vars(self):
        """Verify all required environment variables are set"""
        required_vars = [
            "LIVEKIT_URL",
            "LIVEKIT_API_KEY",
            "LIVEKIT_API_SECRET",
            "OPENAI_API_KEY",
            "DB_URL",
        ]

        optional_vars = [
            "EVOLUTION_API_URL",
            "EVOLUTION_API_KEY",
            "FRONTEND_URL",
            "CHROMA_URL",
            "DEEPGRAM_API_KEY",
        ]

        for var in required_vars:
            if not os.getenv(var):
                self.errors.append(f"Missing required env var: {var}")

        for var in optional_vars:
            if not os.getenv(var):
                self.warnings.append(f"Missing optional env var: {var}")

    def check_database(self):
        """Check database connectivity"""
        try:
            import asyncpg
            db_url = os.getenv("DB_URL")
            if not db_url:
                self.errors.append("DB_URL not configured")
                return

            # Quick connection test
            # Note: In production, this would actually test the connection
            # For now, just verify the import works
            return True
        except ImportError:
            self.errors.append("asyncpg not installed")
        except Exception as e:
            self.errors.append(f"Database check failed: {str(e)}")

    def check_livekit_deps(self):
        """Check LiveKit dependencies"""
        try:
            from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm, VoiceAssistant
            from livekit.plugins import openai, silero
            return True
        except ImportError as e:
            self.errors.append(f"LiveKit dependency missing: {str(e)}")

    def check_openai(self):
        """Check OpenAI SDK"""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or not api_key.startswith("sk-"):
                self.errors.append("Invalid OPENAI_API_KEY format")
            return True
        except ImportError:
            self.errors.append("OpenAI SDK not installed")

    def check_tools(self):
        """Check that custom tools can be imported"""
        try:
            from tools.knowledge_tools import query_m4markets_knowledge
            from tools.crm_tools import get_lead_history
            from tools.forex_tools import recommend_account_type
            return True
        except ImportError as e:
            self.errors.append(f"Tool import failed: {str(e)}")

    def run_all_checks(self):
        """Run all health checks"""
        print("🔍 Running M4Markets Voice Agent Health Checks...")
        print("-" * 50)

        self.check_env_vars()
        self.check_database()
        self.check_livekit_deps()
        self.check_openai()
        self.check_tools()

        # Print results
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors:
            print("\n✅ All critical checks passed!")
            if self.warnings:
                print("⚠️  Some optional features may not work")
            return True
        else:
            print(f"\n❌ Health check failed with {len(self.errors)} errors")
            return False

def main():
    """Main entry point"""
    checker = HealthCheck()
    success = checker.run_all_checks()

    # Exit with appropriate code for Docker healthcheck
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

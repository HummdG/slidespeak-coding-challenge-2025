"""
Test runner script for the backend application.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """Run the complete test suite."""
    print("🚀 SlideSpeak Backend Test Suite")
    print("=" * 40)
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    original_dir = Path.cwd()
    
    try:
        # Commands to run
        commands = [
            (["python", "-m", "pytest", "app/tests/", "-v"], "Running unit tests"),
            (["python", "-m", "pytest", "app/tests/", "-v", "--cov=app"], "Running tests with coverage"),
            (["python", "-m", "pytest", "app/tests/test_integration.py", "-v", "-m", "integration"], "Running integration tests"),
        ]
        
        success_count = 0
        total_count = len(commands)
        
        for cmd, description in commands:
            if run_command(cmd, description):
                success_count += 1
        
        print(f"\n📊 Test Summary:")
        print(f"   Passed: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed")
            return 1
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1
    finally:
        # Return to original directory
        pass


if __name__ == "__main__":
    sys.exit(main())
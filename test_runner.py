#!/usr/bin/env python3
"""
Test Runner for Risk Game
Runs unit tests automatically on file changes and provides manual test execution
"""

import os
import sys
import time
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import webbrowser
from pathlib import Path

class TestHandler(FileSystemEventHandler):
    def __init__(self, test_runner):
        self.test_runner = test_runner
        self.last_run = 0
        self.debounce_delay = 2  # seconds
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Only run tests for relevant file changes
        relevant_extensions = ['.py', '.js', '.html']
        if not any(event.src_path.endswith(ext) for ext in relevant_extensions):
            return
            
        # Ignore test files themselves to prevent infinite loops
        if 'test_' in event.src_path or event.src_path.endswith('test_runner.py'):
            return
            
        current_time = time.time()
        if current_time - self.last_run > self.debounce_delay:
            self.last_run = current_time
            print(f"\n📁 File changed: {event.src_path}")
            self.test_runner.run_all_tests()

class RiskTestRunner:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_tests = ['test_server.py']
        self.frontend_tests = ['test_frontend.html']
        
    def run_backend_tests(self):
        """Run Python backend tests using pytest"""
        print("🐍 Running Python backend tests...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                '-v', '--tb=short', '--color=yes',
                *self.backend_tests
            ], cwd=self.root_dir, capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
                
            if result.returncode == 0:
                print("✅ Backend tests passed!")
                return True
            else:
                print("❌ Backend tests failed!")
                return False
                
        except Exception as e:
            print(f"❌ Error running backend tests: {e}")
            return False
    
    def run_frontend_tests(self):
        """Open frontend tests in browser"""
        print("🌐 Opening frontend tests in browser...")
        try:
            test_file_path = self.root_dir / 'test_frontend.html'
            webbrowser.open(f'file://{test_file_path.absolute()}')
            print("✅ Frontend tests opened in browser!")
            print("   Check the browser for test results.")
            return True
        except Exception as e:
            print(f"❌ Error opening frontend tests: {e}")
            return False
    
    def run_all_tests(self):
        """Run both backend and frontend tests"""
        print("\n" + "="*60)
        print("🧪 Running all tests...")
        print("="*60)
        
        backend_success = self.run_backend_tests()
        frontend_success = self.run_frontend_tests()
        
        print("\n" + "="*60)
        if backend_success:
            print("📊 Test Summary:")
            print("   ✅ Backend tests: PASSED")
            if frontend_success:
                print("   ✅ Frontend tests: OPENED (check browser)")
            else:
                print("   ❌ Frontend tests: FAILED TO OPEN")
        else:
            print("📊 Test Summary:")
            print("   ❌ Backend tests: FAILED")
            
        print("="*60)
        return backend_success
    
    def install_dependencies(self):
        """Install required Python dependencies"""
        print("📦 Installing Python dependencies...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], cwd=self.root_dir, check=True)
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
        except FileNotFoundError:
            print("❌ requirements.txt not found!")
            return False
    
    def start_file_watcher(self):
        """Start watching files for changes"""
        print("👀 Starting file watcher...")
        print("   Watching for changes in .py, .js, and .html files")
        print("   Press Ctrl+C to stop watching")
        
        event_handler = TestHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.root_dir), recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping file watcher...")
            observer.stop()
        observer.join()
    
    def run_server(self):
        """Start the development server"""
        print("🚀 Starting development server...")
        try:
            subprocess.run([
                sys.executable, 'server.py'
            ], cwd=self.root_dir)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
    
    def check_setup(self):
        """Check if all required files exist"""
        required_files = [
            'server.py',
            'index.html', 
            'index.js',
            'audio.js',
            'requirements.txt',
            'test_server.py',
            'test_frontend.html'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.root_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print("❌ Missing required files:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        print("✅ All required files found!")
        return True

def main():
    runner = RiskTestRunner()
    
    if len(sys.argv) < 2:
        print("🎮 Risk Game Test Runner")
        print("="*40)
        print("Usage:")
        print("  python test_runner.py [command]")
        print("")
        print("Commands:")
        print("  setup     - Install dependencies and check setup")
        print("  test      - Run all tests once")
        print("  watch     - Run tests automatically on file changes")
        print("  backend   - Run only backend tests")
        print("  frontend  - Run only frontend tests")
        print("  server    - Start development server")
        print("")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        print("🔧 Setting up development environment...")
        if runner.check_setup():
            runner.install_dependencies()
            print("\n✅ Setup complete! You can now run tests.")
            print("   Try: python test_runner.py test")
        
    elif command == 'test':
        if not runner.check_setup():
            print("❌ Setup incomplete. Run 'python test_runner.py setup' first.")
            return
        runner.run_all_tests()
        
    elif command == 'watch':
        if not runner.check_setup():
            print("❌ Setup incomplete. Run 'python test_runner.py setup' first.")
            return
        # Run tests once immediately
        runner.run_all_tests()
        # Then start watching
        runner.start_file_watcher()
        
    elif command == 'backend':
        if not runner.check_setup():
            print("❌ Setup incomplete. Run 'python test_runner.py setup' first.")
            return
        runner.run_backend_tests()
        
    elif command == 'frontend':
        if not runner.check_setup():
            print("❌ Setup incomplete. Run 'python test_runner.py setup' first.")
            return
        runner.run_frontend_tests()
        
    elif command == 'server':
        if not runner.check_setup():
            print("❌ Setup incomplete. Run 'python test_runner.py setup' first.")
            return
        runner.run_server()
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python test_runner.py' for help.")

if __name__ == "__main__":
    main()
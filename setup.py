#!/usr/bin/env python3
"""
Setup script for IPC Sunday School RAG System
Automates the initial setup process
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70 + "\n")


def check_python_version():
    """Check if Python version is adequate"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = ['pdfs', 'chroma_db']
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True)
            print(f"  ✅ Created: {directory}/")
        else:
            print(f"  ℹ️  Exists: {directory}/")
    
    return True


def setup_env_file():
    """Setup .env file from example"""
    print("\nSetting up environment file...")
    
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if not env_example.exists():
        print("  ❌ .env.example not found!")
        return False
    
    if env_file.exists():
        response = input("  .env already exists. Overwrite? (y/N): ").lower()
        if response != 'y':
            print("  ℹ️  Keeping existing .env file")
            return True
    
    # Copy .env.example to .env
    with open(env_example, 'r') as src:
        content = src.read()
    
    # Get API key from user
    print("\n  OpenAI API Key Setup:")
    print("  You can get your API key from: https://platform.openai.com/api-keys")
    
    api_key = input("  Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        content = content.replace('your_openai_api_key_here', api_key)
        print("  ✅ API key configured")
    else:
        print("  ⚠️  No API key provided - you'll need to add it manually to .env")
    
    with open(env_file, 'w') as dst:
        dst.write(content)
    
    print(f"  ✅ Created .env file")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    print("  This may take a few minutes...\n")
    
    import subprocess
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("\n  ✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Failed to install dependencies: {e}")
        return False


def check_pdfs():
    """Check if PDFs are available"""
    print("\nChecking for PDF files...")
    
    pdf_dir = Path('pdfs')
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    if not pdf_files:
        print("  ⚠️  No PDF files found in pdfs/ directory")
        print("\n  Please add your curriculum PDF files to the pdfs/ directory before running indexer.py")
        return False
    else:
        print(f"  ✅ Found {len(pdf_files)} PDF files")
        return True


def main():
    """Main setup function"""
    print_header("📖 IPC SUNDAY SCHOOL RAG SYSTEM - SETUP")
    
    print("This script will set up your RAG system.\n")
    print("Steps:")
    print("  1. Check Python version")
    print("  2. Create directories")
    print("  3. Setup environment file")
    print("  4. Install dependencies")
    print("  5. Check for PDF files")
    print()
    
    response = input("Continue? (Y/n): ").lower()
    if response == 'n':
        print("Setup cancelled.")
        return
    
    # Step 1: Check Python version
    print_header("Step 1: Checking Python Version")
    if not check_python_version():
        return
    
    # Step 2: Create directories
    print_header("Step 2: Creating Directories")
    if not create_directories():
        return
    
    # Step 3: Setup .env file
    print_header("Step 3: Setting Up Environment File")
    if not setup_env_file():
        return
    
    # Step 4: Install dependencies
    print_header("Step 4: Installing Dependencies")
    install_deps = input("Install Python dependencies? (Y/n): ").lower()
    if install_deps != 'n':
        if not install_dependencies():
            print("\n⚠️  Some dependencies failed to install.")
            print("   Try running manually: pip install -r requirements.txt")
    else:
        print("  ℹ️  Skipped dependency installation")
    
    # Step 5: Check PDFs
    print_header("Step 5: Checking PDF Files")
    has_pdfs = check_pdfs()
    
    # Final summary
    print_header("✅ SETUP COMPLETE")
    
    print("Next steps:")
    
    if not has_pdfs:
        print("\n1. Add your PDF files to the pdfs/ directory")
        print("   - IPC curriculum textbooks")
        print("   - Radiant Life materials")
        print("   - Christian Identity curriculum")
    
    print("\n2. Verify your OpenAI API key in .env file")
    print("   Open .env and check that OPENAI_API_KEY is set")
    
    print("\n3. Build the database:")
    print("   python indexer.py")
    
    print("\n4. Start querying:")
    print("   python cli.py              # Command line interface")
    print("   streamlit run app.py       # Web interface")
    
    print("\nFor detailed instructions, see README.md")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Educational Project Security Check for Bootcamp Capstone
Ensures no real credentials are accidentally committed
"""

import os
import secrets
import string
from pathlib import Path

def generate_secure_key(length=64):
    """Generate a cryptographically secure random key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_environment_file():
    """Check if .env file has secure values"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found. Copy from .env.template first!")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Check for default/weak values
    weak_values = [
        "your-super-secret-jwt-key-here",
        "sk-ant-api03-your-claude-key-here", 
        "sk-your-openai-key-here",
        "username:password@host:5432/database_name"
    ]
    
    issues = []
    for weak in weak_values:
        if weak in content:
            issues.append(f"Found default value: {weak[:20]}...")
    
    if issues:
        print("❌ Environment file contains default values:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n💡 Generate secure values:")
        print(f"JWT_SECRET_KEY={generate_secure_key()}")
        return False
    
    print("✅ Environment file looks secure")
    return True

def check_security_files():
    """Check if security documentation exists"""
    security_file = Path("SECURITY.md")
    if not security_file.exists():
        print("❌ SECURITY.md file missing")
        return False
    
    print("✅ Security documentation exists")
    return True

def check_gitignore():
    """Ensure sensitive files are in .gitignore"""
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("❌ .gitignore file missing")
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    required_entries = [".env", "*.log", "credentials/", "__pycache__/"]
    missing = []
    
    for entry in required_entries:
        if entry not in content:
            missing.append(entry)
    
    if missing:
        print(f"❌ .gitignore missing entries: {missing}")
        return False
    
    print("✅ .gitignore looks good")
    return True

def check_for_secrets():
    """Check for accidentally committed secrets"""
    common_patterns = [
        "sk-", "gsk_", "ACyour", "Bearer ", "password=", "secret="
    ]
    
    # Check main Python files
    py_files = list(Path(".").glob("*.py")) + list(Path("agents").glob("*.py"))
    
    issues = []
    for py_file in py_files:
        if py_file.exists():
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for pattern in common_patterns:
                    if pattern in content and "env" not in content.lower():
                        issues.append(f"{py_file}: possible secret pattern '{pattern}'")
    
    if issues:
        print("⚠️  Possible secrets found in code:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✅ No obvious secrets in code")
    return True

def main():
    print("🎓 Educational Project Security Check")
    print("=" * 50)
    
    checks = [
        ("Credential Protection", check_environment_file),
        ("Documentation Quality", check_security_files),
        ("Git Configuration", check_gitignore),
        ("Secret Detection", check_for_secrets)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ Ready for capstone submission!")
        print("🎓 Educational project security checks passed")
        print("📚 Great for learning and demonstration purposes")
    else:
        print("❌ Issues found - fix before submission")
        print("\n🎓 For educational projects:")
        print("  - Ensure no real API keys are committed")
        print("  - Document any security shortcuts taken")
        print("  - Focus on demonstrating technical concepts")
    
    return all_passed

if __name__ == "__main__":
    main()

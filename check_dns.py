#!/usr/bin/env python3
"""Check DNS configuration for domain"""

import socket
import sys

DOMAIN = "21days.club"
EXPECTED_IP = "195.133.63.34"

def check_dns(domain):
    """Check DNS resolution for domain"""
    try:
        ip = socket.gethostbyname(domain)
        print(f"{domain} -> {ip}")
        if ip == EXPECTED_IP:
            print(f"[OK] DNS correctly points to {EXPECTED_IP}")
            return True
        else:
            print(f"[WARNING] DNS points to {ip}, expected {EXPECTED_IP}")
            return False
    except socket.gaierror as e:
        print(f"[ERROR] DNS resolution failed: {e}")
        return False

def main():
    print(f"Checking DNS for {DOMAIN}...")
    print(f"Expected IP: {EXPECTED_IP}\n")
    
    # Check main domain
    main_ok = check_dns(DOMAIN)
    print()
    
    # Check www subdomain
    www_ok = check_dns(f"www.{DOMAIN}")
    print()
    
    if main_ok and www_ok:
        print("[OK] DNS is properly configured!")
        print("You can proceed with SSL certificate installation.")
        return True
    else:
        print("[WARNING] DNS is not properly configured.")
        print("Please configure DNS records:")
        print(f"  A record: {DOMAIN} -> {EXPECTED_IP}")
        print(f"  A record: www.{DOMAIN} -> {EXPECTED_IP}")
        return False

if __name__ == "__main__":
    main()


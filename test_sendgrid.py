#!/usr/bin/env python
"""
Test SendGrid SMTP connection from Railway
Run this to see if SMTP port 587 is blocked or misconfigured
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devblog.settings')
import django
django.setup()

from django.conf import settings
import smtplib
import socket

print("=" * 60)
print("SENDGRID SMTP CONNECTION TEST")
print("=" * 60)

# Print current settings
print(f"\n📧 Current Email Settings:")
print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"   EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"   EMAIL_HOST_PASSWORD: {'*' * 10 if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Test 1: DNS Resolution
print(f"\n🔍 Test 1: DNS Resolution")
try:
    ip = socket.gethostbyname(settings.EMAIL_HOST)
    print(f"   ✅ {settings.EMAIL_HOST} resolves to {ip}")
except Exception as e:
    print(f"   ❌ DNS resolution failed: {e}")
    sys.exit(1)

# Test 2: Port Connection
print(f"\n🔍 Test 2: TCP Connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((settings.EMAIL_HOST, settings.EMAIL_PORT))
    sock.close()
    
    if result == 0:
        print(f"   ✅ Port {settings.EMAIL_PORT} is OPEN")
    else:
        print(f"   ❌ Port {settings.EMAIL_PORT} is BLOCKED or UNREACHABLE")
        print(f"   ⚠️  Railway is blocking SMTP port {settings.EMAIL_PORT}")
        print(f"   💡 You MUST use HTTP API instead of SMTP")
        sys.exit(1)
except socket.timeout:
    print(f"   ❌ Connection timeout - port is BLOCKED")
    print(f"   ⚠️  Railway is blocking outbound connections to port {settings.EMAIL_PORT}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Test 3: SMTP Handshake
print(f"\n🔍 Test 3: SMTP Connection & Authentication")
try:
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
    server.set_debuglevel(0)
    print(f"   ✅ Connected to SMTP server")
    
    server.ehlo()
    print(f"   ✅ EHLO successful")
    
    if settings.EMAIL_USE_TLS:
        server.starttls()
        server.ehlo()
        print(f"   ✅ TLS enabled")
    
    # Test authentication
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print(f"   ✅ Authentication successful")
    
    server.quit()
    print(f"\n🎉 SUCCESS!  SendGrid SMTP is working!")
    print(f"✅ You can use SMTP for emails")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"   ❌ Authentication failed: {e}")
    print(f"   🔧 Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
    print(f"   💡 EMAIL_HOST_USER should be exactly:  'apikey'")
    print(f"   💡 EMAIL_HOST_PASSWORD should be your SendGrid API key")
    sys.exit(1)
except socket.timeout:
    print(f"   ❌ SMTP connection timeout")
    print(f"   ⚠️  Railway is blocking SMTP - you MUST use HTTP API")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ SMTP connection failed: {e}")
    print(f"   ⚠️  Railway might be blocking SMTP")
    sys.exit(1)

print("=" * 60)
#!/usr/bin/env python3
"""
Test script om te controleren of de MCP configuratie voor Cursor correct werkt.
Dit simuleert hoe Cursor de MCP server zou starten.
"""

import subprocess
import json
import time
import sys
import os

def test_mcp_server_startup():
    """Test of de MCP server correct start volgens de mcp.json configuratie."""
    
    print("🚀 Testen MCP Server Startup voor Cursor")
    print("=" * 60)
    
    # Lees de mcp.json configuratie
    try:
        with open('mcp.json', 'r') as f:
            config = json.load(f)
        
        server_config = config['mcpServers']['mcp-invoice-processor']
        print("✅ mcp.json configuratie gelezen")
        print(f"   Command: {server_config['command']}")
        print(f"   Directory: {server_config['args'][1]}")
        print(f"   Module: {server_config['args'][-1]}")
        
    except Exception as e:
        print(f"❌ Fout bij lezen mcp.json: {e}")
        return False
    
    # Test de server startup
    print("\n🔄 Testen van server startup...")
    
    try:
        # Start de server als subprocess
        process = subprocess.Popen(
            [server_config['command']] + server_config['args'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
        )
        
        # Wacht even om te zien of de server start
        time.sleep(3)
        
        # Check of de process nog leeft
        if process.poll() is None:
            print("✅ Server start succesvol")
            
            # Stop de server
            process.terminate()
            process.wait(timeout=5)
            print("✅ Server gestopt")
            return True
        else:
            # Server is gestopt, check output
            stdout, stderr = process.communicate()
            print(f"❌ Server gestopt met exit code: {process.returncode}")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Fout bij server startup: {e}")
        return False

def test_mcp_configuration():
    """Test of de MCP configuratie correct is geformatteerd."""
    
    print("\n🔧 Testen MCP Configuratie Validiteit")
    print("-" * 40)
    
    try:
        with open('mcp.json', 'r') as f:
            config = json.load(f)
        
        # Check verplichte velden
        required_fields = ['mcpServers']
        for field in required_fields:
            if field not in config:
                print(f"❌ Verplicht veld ontbreekt: {field}")
                return False
        
        servers = config['mcpServers']
        if not servers:
            print("❌ Geen MCP servers gedefinieerd")
            return False
        
        for server_name, server_config in servers.items():
            print(f"✅ Server gevonden: {server_name}")
            
            # Check server configuratie
            required_server_fields = ['command', 'args']
            for field in required_server_fields:
                if field not in server_config:
                    print(f"   ❌ Verplicht veld ontbreekt: {field}")
                    return False
            
            print(f"   ✅ Command: {server_config['command']}")
            print(f"   ✅ Args: {len(server_config['args'])} argumenten")
            
            # Check of command bestaat
            if os.path.exists(server_config['command']):
                print(f"   ✅ Command executable gevonden")
            else:
                print(f"   ⚠️  Command executable niet gevonden: {server_config['command']}")
            
            # Check directory
            if '--directory' in server_config['args']:
                dir_index = server_config['args'].index('--directory')
                if dir_index + 1 < len(server_config['args']):
                    directory = server_config['args'][dir_index + 1]
                    if os.path.exists(directory):
                        print(f"   ✅ Directory gevonden: {directory}")
                    else:
                        print(f"   ❌ Directory niet gevonden: {directory}")
                        return False
        
        print("✅ MCP configuratie is geldig")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse fout: {e}")
        return False
    except Exception as e:
        print(f"❌ Onverwachte fout: {e}")
        return False

def test_cursor_integration():
    """Test of de configuratie geschikt is voor Cursor integratie."""
    
    print("\n🎯 Testen Cursor Integratie")
    print("-" * 40)
    
    try:
        with open('mcp.json', 'r') as f:
            config = json.load(f)
        
        server_config = config['mcpServers']['mcp-invoice-processor']
        
        # Check of dit een STDIO transport is (aanbevolen voor Cursor)
        if 'stdio' in str(server_config).lower() or 'stdio' in server_config.get('transport', ''):
            print("✅ STDIO transport gedetecteerd (aanbevolen voor Cursor)")
        else:
            print("ℹ️  Geen STDIO transport gedetecteerd")
        
        # Check of de server naam duidelijk is
        server_name = list(config['mcpServers'].keys())[0]
        if 'invoice' in server_name.lower() or 'processor' in server_name.lower():
            print("✅ Server naam is duidelijk en beschrijvend")
        else:
            print("ℹ️  Overweeg een duidelijkere server naam")
        
        # Check omgevingsvariabelen
        env_vars = server_config.get('env', {})
        if 'OLLAMA_HOST' in env_vars:
            print("✅ Ollama host geconfigureerd")
        if 'OLLAMA_MODEL' in env_vars:
            print("✅ Ollama model geconfigureerd")
        
        print("✅ Configuratie geschikt voor Cursor integratie")
        return True
        
    except Exception as e:
        print(f"❌ Fout bij Cursor integratie test: {e}")
        return False

def main():
    """Hoofdfunctie."""
    
    print("🧪 MCP Configuratie Test voor Cursor")
    print("=" * 60)
    
    # Test 1: Configuratie validiteit
    config_valid = test_mcp_configuration()
    
    # Test 2: Server startup
    startup_success = test_mcp_server_startup()
    
    # Test 3: Cursor integratie
    cursor_ready = test_cursor_integration()
    
    # Samenvatting
    print("\n📊 Test Resultaten Samenvatting")
    print("=" * 40)
    print(f"Configuratie validiteit: {'✅' if config_valid else '❌'}")
    print(f"Server startup: {'✅' if startup_success else '❌'}")
    print(f"Cursor integratie: {'✅' if cursor_ready else '❌'}")
    
    if config_valid and startup_success and cursor_ready:
        print("\n🎉 Alle tests geslaagd! De MCP configuratie is klaar voor Cursor.")
        print("\n📋 Volgende stappen:")
        print("1. Kopieer mcp.json naar je Cursor configuratie directory")
        print("2. Herstart Cursor")
        print("3. De MCP server zou automatisch beschikbaar moeten zijn")
        print("4. Test met: /mcp-invoice-processor process_document_text")
    else:
        print("\n⚠️  Sommige tests gefaald. Controleer de configuratie.")
    
    return config_valid and startup_success and cursor_ready

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

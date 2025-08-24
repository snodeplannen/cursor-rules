#!/usr/bin/env python3
"""
Test Runner voor MCP Invoice Processor
=====================================

Dit script voert alle tests uit en genereert rapporten.
"""

import subprocess
import sys
import time
# Path not used in current implementation


def run_command(command, description):
    """Voer een commando uit en toon resultaat."""
    print(f"🔄 {description}...")
    print(f"   Commando: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {description} succesvol")
            return True
        else:
            print(f"❌ {description} mislukt")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timeout")
        return False
    except Exception as e:
        print(f"❌ {description} mislukt")
        print(f"   Error: {e}")
        return False


def main():
    """Hoofdfunctie voor test uitvoering."""
    print("🚀 MCP Invoice Processor Test Runner")
    print("=" * 50)
    
    start_time = time.time()
    results = {}
    
    # Controleer dependencies
    print("\n🔍 Controleren van dependencies...")
    
    # UV package manager
    uv_result = run_command(
        ["uv", "run", "python", "--version"],
        "Python via UV"
    )
    results["uv"] = uv_result
    
    # FastMCP CLI
    fastmcp_result = run_command(
        ["uv", "run", "fastmcp", "--help"],
        "FastMCP CLI"
    )
    results["fastmcp"] = fastmcp_result
    
    if all([uv_result, fastmcp_result]):
        print("✅ Alle dependencies beschikbaar")
    else:
        print("❌ Sommige dependencies ontbreken")
    
    # Voer tests uit
    print("\n🧪 Uitvoeren van tests...")
    
    # Unit tests
    unit_result = run_command(
        ["uv", "run", "pytest", "tests/test_pipeline.py", "-v", "--tb=short"],
        "Unit tests"
    )
    results["unit"] = unit_result
    
    # FastMCP tests
    fastmcp_tests_result = run_command(
        ["uv", "run", "pytest", "tests/test_fastmcp_client.py", "tests/test_fastmcp_cli.py", "-v", "--tb=short"],
        "FastMCP tests"
    )
    results["fastmcp_tests"] = fastmcp_tests_result
    
    # MCP library tests
    mcp_tests_result = run_command(
        ["uv", "run", "pytest", "tests/test_mcp_client.py", "-v", "--tb=short"],
        "MCP library tests"
    )
    results["mcp_tests"] = mcp_tests_result
    
    # Alle tests
    all_tests_result = run_command(
        ["uv", "run", "pytest", "tests/", "-v", "--tb=short", "--durations=10"],
        "Alle tests"
    )
    results["all_tests"] = all_tests_result
    
    # Genereer test rapport
    print("\n📊 Genereren van test rapport...")
    report_result = run_command(
        ["uv", "run", "pytest", "tests/", "--tb=short", "--durations=90", 
         "--junitxml=tests/results.xml", "--html=tests/report.html", "--self-contained-html"],
        "Test rapport genereren"
    )
    results["report"] = report_result
    
    # Samenvatting
    print("\n📋 Test Resultaten Samenvatting")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n📊 Totaal: {total_tests} test categorieën")
    print(f"✅ Geslaagd: {passed_tests}")
    print(f"❌ Gefaald: {failed_tests}")
    
    execution_time = time.time() - start_time
    print(f"\n⏱️  Totale uitvoeringstijd: {execution_time:.2f} seconden")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test categorie(ën) gefaald")
        sys.exit(1)
    else:
        print("\n🎉 Alle tests geslaagd!")
        sys.exit(0)


if __name__ == "__main__":
    main()

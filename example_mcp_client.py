#!/usr/bin/env python3
"""
Example MCP Client voor de MCP Document Processor.
Demonstreert hoe je de MCP server kunt aanroepen via verschillende transports.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Voeg src directory toe aan Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_invoice_processor.config import settings
from mcp_invoice_processor.logging_config import setup_logging

# Setup logging
logger = setup_logging(log_level="INFO")


class MCPClientDemo:
    """Demo client voor MCP Document Processor."""
    
    def __init__(self):
        self.logger = logger
        
    async def test_direct_tools(self):
        """Test de tools direct zonder MCP protocol."""
        print("🔧 Testing Direct Tools Integration")
        print("=" * 50)
        
        try:
            from mcp_invoice_processor import tools
            
            # Test health check
            print("1. Testing health_check...")
            health_result = await tools.health_check()
            print(f"   ✅ Health Status: {health_result.get('status', 'unknown')}")
            print(f"   🤖 Ollama: {health_result.get('ollama', {}).get('status', 'unknown')}")
            
            # Test document classification
            print("\n2. Testing document classification...")
            sample_cv_text = """
            Jan Janssen
            Software Developer
            Email: jan.janssen@example.com
            Telefoon: 06-12345678
            
            Werkervaring:
            - Senior Developer bij TechCorp (2020-2024)
            - Junior Developer bij StartupXYZ (2018-2020)
            
            Opleiding:
            - Informatica, TU Delft (2014-2018)
            
            Vaardigheden:
            - Python, JavaScript, React
            - Docker, Kubernetes
            - Agile/Scrum
            """
            
            classification = await tools.classify_document_type(sample_cv_text)
            print(f"   📋 Document Type: {classification.get('document_type', 'unknown')}")
            print(f"   🎯 Confidence: {classification.get('confidence', 0):.1f}%")
            print(f"   🔧 Processor: {classification.get('processor', 'unknown')}")
            
            # Test document processing
            print("\n3. Testing document processing...")
            processing_result = await tools.process_document_text(
                sample_cv_text, 
                extraction_method="hybrid"
            )
            
            if "error" not in processing_result:
                print(f"   ✅ Processing successful!")
                print(f"   👤 Name: {processing_result.get('full_name', 'N/A')}")
                print(f"   📧 Email: {processing_result.get('email', 'N/A')}")
                print(f"   📞 Phone: {processing_result.get('phone', 'N/A')}")
                print(f"   💼 Work Experience: {len(processing_result.get('work_experience', []))} positions")
                print(f"   ⏱️  Processing Time: {processing_result.get('processing_time', 0):.2f}s")
            else:
                print(f"   ❌ Processing failed: {processing_result.get('error')}")
            
            # Test metrics
            print("\n4. Testing metrics...")
            metrics = await tools.get_metrics()
            print(f"   📊 Total Documents Processed: {metrics.get('total_documents_processed', 0)}")
            print(f"   ✅ Success Rate: {metrics.get('success_rate', 0):.1f}%")
            print(f"   ⏱️  Average Processing Time: {metrics.get('average_processing_time', 0):.2f}s")
            
        except Exception as e:
            print(f"   ❌ Direct tools test failed: {e}")
            self.logger.error(f"Direct tools test failed: {e}", exc_info=True)
    
    async def test_http_client(self):
        """Test HTTP transport via FastMCP client."""
        print("\n🌐 Testing HTTP Transport Client")
        print("=" * 50)
        
        try:
            from fastmcp import Client
            
            # Maak HTTP client
            print("1. Connecting to HTTP server...")
            async with Client("http://127.0.0.1:8000/mcp") as client:
                print("   ✅ Connected successfully!")
                
                # Test health check via HTTP
                print("\n2. Testing health check via HTTP...")
                health_result = await client.call_tool("health_check", {})
                print(f"   ✅ Health Status: {health_result.get('status', 'unknown')}")
                
                # Test document processing via HTTP
                print("\n3. Testing document processing via HTTP...")
                sample_invoice_text = """
                FACTUUR
                
                Factuurnummer: INV-2024-001
                Datum: 15-01-2024
                Vervaldatum: 15-02-2024
                
                Van: TechCorp BV
                Naar: Klant ABC
                
                Beschrijving: Software Development
                Bedrag: €1,250.00
                BTW (21%): €262.50
                Totaal: €1,512.50
                """
                
                processing_result = await client.call_tool(
                    "process_document_text", 
                    {
                        "text": sample_invoice_text,
                        "extraction_method": "json_schema"
                    }
                )
                
                if "error" not in processing_result:
                    print(f"   ✅ Processing successful!")
                    print(f"   🧾 Invoice Number: {processing_result.get('invoice_number', 'N/A')}")
                    print(f"   💰 Total Amount: €{processing_result.get('total_amount', 0)}")
                    print(f"   📅 Date: {processing_result.get('invoice_date', 'N/A')}")
                    print(f"   ⏱️  Processing Time: {processing_result.get('processing_time', 0):.2f}s")
                else:
                    print(f"   ❌ Processing failed: {processing_result.get('error')}")
                
                # Test metrics via HTTP
                print("\n4. Testing metrics via HTTP...")
                metrics = await client.call_tool("get_metrics", {})
                print(f"   📊 Total Documents Processed: {metrics.get('total_documents_processed', 0)}")
                print(f"   ✅ Success Rate: {metrics.get('success_rate', 0):.1f}%")
                
                print("\n   ✅ HTTP client disconnected")
            
        except Exception as e:
            print(f"   ❌ HTTP client test failed: {e}")
            self.logger.error(f"HTTP client test failed: {e}", exc_info=True)
    
    async def test_stdio_client(self):
        """Test STDIO transport via subprocess."""
        print("\n📡 Testing STDIO Transport Client")
        print("=" * 50)
        
        try:
            import subprocess
            import json
            
            print("1. Starting STDIO server process...")
            
            # Start de STDIO server
            process = subprocess.Popen(
                ["uv", "run", "mcp-server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent
            )
            
            print("   ✅ STDIO server started")
            
            # Test MCP protocol handshake
            print("\n2. Testing MCP protocol handshake...")
            
            # Initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "example-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send initialize request
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"   ✅ Initialize response: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            
            # Test tool call
            print("\n3. Testing tool call via STDIO...")
            
            tool_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "health_check",
                    "arguments": {}
                }
            }
            
            process.stdin.write(json.dumps(tool_request) + "\n")
            process.stdin.flush()
            
            # Read tool response
            tool_response_line = process.stdout.readline()
            if tool_response_line:
                tool_response = json.loads(tool_response_line.strip())
                if "result" in tool_response:
                    result = tool_response["result"]
                    print(f"   ✅ Health Status: {result.get('status', 'unknown')}")
                    print(f"   🤖 Ollama: {result.get('ollama', {}).get('status', 'unknown')}")
                else:
                    print(f"   ❌ Tool call failed: {tool_response}")
            
            # Cleanup
            process.stdin.close()
            process.terminate()
            process.wait()
            
            print("\n   ✅ STDIO client test completed")
            
        except Exception as e:
            print(f"   ❌ STDIO client test failed: {e}")
            self.logger.error(f"STDIO client test failed: {e}", exc_info=True)
    
    async def test_file_processing(self):
        """Test bestand verwerking."""
        print("\n📁 Testing File Processing")
        print("=" * 50)
        
        try:
            from mcp_invoice_processor import tools
            
            # Maak een test bestand
            test_file_path = Path("test_document.txt")
            test_content = """
            CURRICULUM VITAE
            
            Naam: Maria van der Berg
            Email: maria.vandenberg@example.com
            Telefoon: 06-98765432
            
            PROFESSIONELE ERVARING:
            - Lead Developer bij InnovateTech (2021-heden)
            - Senior Developer bij WebSolutions (2019-2021)
            - Developer bij CodeCraft (2017-2019)
            
            OPLEIDING:
            - Master Computer Science, Universiteit van Amsterdam (2015-2017)
            - Bachelor Informatica, Hogeschool van Amsterdam (2012-2015)
            
            VAARDIGHEDEN:
            - Python, Java, C#
            - React, Angular, Vue.js
            - AWS, Azure, Docker
            - Machine Learning, Data Science
            """
            
            # Schrijf test bestand
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            print(f"1. Created test file: {test_file_path}")
            
            # Test bestand verwerking
            print("\n2. Processing test file...")
            result = await tools.process_document_file(
                str(test_file_path), 
                extraction_method="hybrid"
            )
            
            if "error" not in result:
                print(f"   ✅ File processing successful!")
                print(f"   👤 Name: {result.get('full_name', 'N/A')}")
                print(f"   📧 Email: {result.get('email', 'N/A')}")
                print(f"   📞 Phone: {result.get('phone', 'N/A')}")
                print(f"   💼 Work Experience: {len(result.get('work_experience', []))} positions")
                print(f"   🎓 Education: {len(result.get('education', []))} entries")
                print(f"   🔧 Skills: {len(result.get('skills', []))} skills")
                print(f"   ⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
            else:
                print(f"   ❌ File processing failed: {result.get('error')}")
            
            # Cleanup
            test_file_path.unlink()
            print(f"\n3. Cleaned up test file: {test_file_path}")
            
        except Exception as e:
            print(f"   ❌ File processing test failed: {e}")
            self.logger.error(f"File processing test failed: {e}", exc_info=True)
    
    async def run_all_tests(self):
        """Voer alle tests uit."""
        print("🚀 MCP Document Processor Client Demo")
        print("=" * 60)
        print(f"📊 Ollama Host: {settings.ollama.HOST}")
        print(f"🤖 Ollama Model: {settings.ollama.MODEL}")
        print("=" * 60)
        
        # Test direct tools (altijd mogelijk)
        await self.test_direct_tools()
        
        # Test bestand verwerking
        await self.test_file_processing()
        
        # Test HTTP client (als server draait)
        try:
            await self.test_http_client()
        except Exception as e:
            print(f"\n⚠️  HTTP client test skipped (server not running): {e}")
            print("   💡 Start HTTP server with: uv run mcp-http-server-async")
        
        # Test STDIO client
        try:
            await self.test_stdio_client()
        except Exception as e:
            print(f"\n⚠️  STDIO client test skipped: {e}")
            print("   💡 Make sure STDIO server is available")
        
        print("\n🎉 Demo completed!")
        print("=" * 60)


async def main():
    """Hoofdfunctie voor de demo."""
    demo = MCPClientDemo()
    await demo.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

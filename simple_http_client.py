#!/usr/bin/env python3
"""
Simple HTTP MCP Client voor de MCP Document Processor.
Demonstreert HTTP transport gebruik met FastMCP client.
"""

import asyncio
import json
from pathlib import Path

from fastmcp import Client


async def test_http_mcp_client():
    """Test HTTP MCP client tegen de server."""
    
    print("🌐 HTTP MCP Client Demo")
    print("=" * 40)
    
    # Server URL
    server_url = "http://127.0.0.1:8000/mcp"
    
    try:
        # Maak client en verbind
        print(f"1. Connecting to {server_url}...")
        async with Client(server_url) as client:
            print("   ✅ Connected successfully!")
            
            # Test health check
            print("\n2. Testing health check...")
            health_result = await client.call_tool("health_check", {})
            print(f"   Health Result Type: {type(health_result)}")
            print(f"   Health Result: {health_result}")
            
            # Extract status from CallToolResult
            if hasattr(health_result, 'content'):
                if health_result.content:
                    content = health_result.content[0] if health_result.content else {}
                    if hasattr(content, 'text'):
                        import json
                        try:
                            health_data = json.loads(content.text)
                            print(f"   Status: {health_data.get('status', 'unknown')}")
                            print(f"   Ollama: {health_data.get('ollama', {}).get('status', 'unknown')}")
                        except:
                            print(f"   Raw content: {content.text}")
                    else:
                        print(f"   Content: {content}")
                else:
                    print("   No content in response")
            else:
                print(f"   Raw result: {health_result}")
            
            # Test invoice processing
            print("\n3. Testing invoice processing...")
            
            invoice_text = """
            FACTUUR
            
            Factuurnummer: INV-2024-001
            Datum: 15-01-2024
            
            Van: TechCorp BV
            Naar: Klant ABC
            
            Beschrijving: Software Development
            Bedrag: €1,250.00
            BTW (21%): €262.50
            Totaal: €1,512.50
            """
            
            invoice_result = await client.call_tool(
                "process_document_text",
                {
                    "text": invoice_text,
                    "extraction_method": "json_schema"
                }
            )
            
            print(f"   Invoice Processing Result Type: {type(invoice_result)}")
            
            # Extract invoice data from CallToolResult
            if hasattr(invoice_result, 'content') and invoice_result.content:
                content = invoice_result.content[0] if invoice_result.content else {}
                if hasattr(content, 'text'):
                    import json
                    try:
                        invoice_data = json.loads(content.text)
                        if "error" not in invoice_data:
                            print("   ✅ Invoice processing successful!")
                            print(f"   Invoice Number: {invoice_data.get('invoice_number', 'N/A')}")
                            print(f"   Total Amount: €{invoice_data.get('total_amount', 0)}")
                            print(f"   Date: {invoice_data.get('invoice_date', 'N/A')}")
                            print(f"   Document Type: {invoice_data.get('document_type', 'unknown')}")
                            print(f"   Confidence: {invoice_data.get('confidence', 0)}%")
                        else:
                            print(f"   ❌ Invoice processing failed: {invoice_data.get('error')}")
                    except Exception as e:
                        print(f"   Raw content: {content.text}")
                        print(f"   JSON parse error: {e}")
                else:
                    print(f"   Content: {content}")
            else:
                print(f"   Raw result: {invoice_result}")
            
            # Test CV processing
            print("\n4. Testing CV processing...")
            
            cv_text = """
            CURRICULUM VITAE
            
            Jan de Vries
            Email: jan.devries@email.com
            Telefoon: +31 6 12345678
            
            PROFESSIONELE SAMENVATTING
            Ervaren software developer met 5 jaar ervaring in web development en database management.
            
            WERKERVARING
            
            Senior Developer - TechCorp BV (2020-2024)
            - Ontwikkeling van web applicaties met Python en JavaScript
            - Database design en optimalisatie
            - Team leiderschap van 3 developers
            
            Junior Developer - StartupXYZ (2019-2020)
            - Frontend development met React
            - API integratie en testing
            
            OPLEIDING
            
            Bachelor Computer Science - Universiteit van Amsterdam (2015-2019)
            - Specialisatie: Software Engineering
            - Cum Laude afgestudeerd
            
            VAARDIGHEDEN
            - Python, JavaScript, React, Node.js
            - PostgreSQL, MongoDB
            - Docker, Kubernetes
            - Agile/Scrum methodologieën
            """
            
            cv_result = await client.call_tool(
                "process_document_text",
                {
                    "text": cv_text,
                    "extraction_method": "hybrid"
                }
            )
            
            print(f"   CV Processing Result Type: {type(cv_result)}")
            
            # Extract CV data from CallToolResult
            if hasattr(cv_result, 'content') and cv_result.content:
                content = cv_result.content[0] if cv_result.content else {}
                if hasattr(content, 'text'):
                    import json
                    try:
                        cv_data = json.loads(content.text)
                        if "error" not in cv_data:
                            print("   ✅ CV processing successful!")
                            print(f"   Full Name: {cv_data.get('full_name', 'N/A')}")
                            print(f"   Email: {cv_data.get('email', 'N/A')}")
                            print(f"   Phone: {cv_data.get('phone_number', 'N/A')}")
                            print(f"   Work Experience: {len(cv_data.get('work_experience', []))} positions")
                            print(f"   Education: {len(cv_data.get('education', []))} degrees")
                            print(f"   Skills: {len(cv_data.get('skills', []))} skills")
                            print(f"   Document Type: {cv_data.get('document_type', 'unknown')}")
                            print(f"   Confidence: {cv_data.get('confidence', 0)}%")
                            
                            # Show first work experience
                            if cv_data.get('work_experience'):
                                first_job = cv_data['work_experience'][0]
                                print(f"   First Job: {first_job.get('job_title', 'N/A')} at {first_job.get('company', 'N/A')}")
                            
                            # Show first skill
                            if cv_data.get('skills'):
                                print(f"   First Skill: {cv_data['skills'][0]}")
                                
                        else:
                            print(f"   ❌ CV processing failed: {cv_data.get('error')}")
                    except Exception as e:
                        print(f"   Raw content: {content.text}")
                        print(f"   JSON parse error: {e}")
                else:
                    print(f"   Content: {content}")
            else:
                print(f"   Raw result: {cv_result}")
            
            # Test PDF CV processing
            print("\n5. Testing PDF CV processing...")
            
            pdf_file_path = "martin-ingescande-CV-losvanbrief-sikkieversie5.pdf"
            
            # Check if PDF file exists
            import os
            if not os.path.exists(pdf_file_path):
                print(f"   ⚠️  PDF file not found: {pdf_file_path}")
                print("   Skipping PDF test...")
            else:
                print(f"   📄 Processing PDF file: {pdf_file_path}")
                
                pdf_result = await client.call_tool(
                    "process_document_file",
                    {
                        "file_path": pdf_file_path,
                        "extraction_method": "hybrid"
                    }
                )
                
                print(f"   PDF Processing Result Type: {type(pdf_result)}")
                
                # Extract PDF data from CallToolResult
                if hasattr(pdf_result, 'content') and pdf_result.content:
                    content = pdf_result.content[0] if pdf_result.content else {}
                    if hasattr(content, 'text'):
                        import json
                        try:
                            pdf_data = json.loads(content.text)
                            if "error" not in pdf_data:
                                print("   ✅ PDF processing successful!")
                                print(f"   Full Name: {pdf_data.get('full_name', 'N/A')}")
                                print(f"   Email: {pdf_data.get('email', 'N/A')}")
                                print(f"   Phone: {pdf_data.get('phone_number', 'N/A')}")
                                print(f"   Work Experience: {len(pdf_data.get('work_experience', []))} positions")
                                print(f"   Education: {len(pdf_data.get('education', []))} degrees")
                                print(f"   Skills: {len(pdf_data.get('skills', []))} skills")
                                print(f"   Document Type: {pdf_data.get('document_type', 'unknown')}")
                                print(f"   Confidence: {pdf_data.get('confidence', 0)}%")
                                print(f"   Processing Time: {pdf_data.get('processing_time', 0):.2f}s")
                                
                                # Show first work experience if available
                                if pdf_data.get('work_experience'):
                                    first_job = pdf_data['work_experience'][0]
                                    print(f"   First Job: {first_job.get('job_title', 'N/A')} at {first_job.get('company', 'N/A')}")
                                
                                # Show first skill if available
                                if pdf_data.get('skills'):
                                    print(f"   First Skill: {pdf_data['skills'][0]}")
                                    
                            else:
                                print(f"   ❌ PDF processing failed: {pdf_data.get('error')}")
                        except Exception as e:
                            print(f"   Raw content: {content.text}")
                            print(f"   JSON parse error: {e}")
                    else:
                        print(f"   Content: {content}")
                else:
                    print(f"   Raw result: {pdf_result}")
            
            # Test PDF Invoice processing
            print("\n6. Testing PDF Invoice processing...")
            
            invoice_pdf_path = "amazon_rugtas-factuur.pdf"
            
            # Check if PDF file exists
            if not os.path.exists(invoice_pdf_path):
                print(f"   ⚠️  PDF file not found: {invoice_pdf_path}")
                print("   Skipping PDF invoice test...")
            else:
                print(f"   📄 Processing PDF invoice: {invoice_pdf_path}")
                
                invoice_pdf_result = await client.call_tool(
                    "process_document_file",
                    {
                        "file_path": invoice_pdf_path,
                        "extraction_method": "hybrid"
                    }
                )
                
                print(f"   PDF Invoice Result Type: {type(invoice_pdf_result)}")
                
                # Extract PDF invoice data from CallToolResult
                if hasattr(invoice_pdf_result, 'content') and invoice_pdf_result.content:
                    content = invoice_pdf_result.content[0] if invoice_pdf_result.content else {}
                    if hasattr(content, 'text'):
                        import json
                        try:
                            invoice_pdf_data = json.loads(content.text)
                            if "error" not in invoice_pdf_data:
                                print("   ✅ PDF invoice processing successful!")
                                print(f"   Invoice ID: {invoice_pdf_data.get('invoice_id', 'N/A')}")
                                print(f"   Invoice Number: {invoice_pdf_data.get('invoice_number', 'N/A')}")
                                print(f"   Supplier: {invoice_pdf_data.get('supplier_name', 'N/A')}")
                                print(f"   Customer: {invoice_pdf_data.get('customer_name', 'N/A')}")
                                print(f"   Invoice Date: {invoice_pdf_data.get('invoice_date', 'N/A')}")
                                print(f"   Due Date: {invoice_pdf_data.get('due_date', 'N/A')}")
                                print(f"   Subtotal: €{invoice_pdf_data.get('subtotal', 0)}")
                                print(f"   VAT Amount: €{invoice_pdf_data.get('vat_amount', 0)}")
                                print(f"   Total Amount: €{invoice_pdf_data.get('total_amount', 0)}")
                                print(f"   Currency: {invoice_pdf_data.get('currency', 'N/A')}")
                                print(f"   Line Items: {len(invoice_pdf_data.get('line_items', []))} items")
                                print(f"   Document Type: {invoice_pdf_data.get('document_type', 'unknown')}")
                                print(f"   Confidence: {invoice_pdf_data.get('confidence', 0)}%")
                                print(f"   Processing Time: {invoice_pdf_data.get('processing_time', 0):.2f}s")
                                
                                # Show first line item if available
                                if invoice_pdf_data.get('line_items'):
                                    first_item = invoice_pdf_data['line_items'][0]
                                    print(f"   First Item: {first_item.get('description', 'N/A')} - €{first_item.get('line_total', 0)}")
                                
                                # Show payment terms if available
                                if invoice_pdf_data.get('payment_terms'):
                                    print(f"   Payment Terms: {invoice_pdf_data['payment_terms']}")
                                    
                            else:
                                print(f"   ❌ PDF invoice processing failed: {invoice_pdf_data.get('error')}")
                        except Exception as e:
                            print(f"   Raw content: {content.text}")
                            print(f"   JSON parse error: {e}")
                    else:
                        print(f"   Content: {content}")
                else:
                    print(f"   Raw result: {invoice_pdf_result}")
            
            # Test metrics
            print("\n7. Testing metrics...")
            metrics = await client.call_tool("get_metrics", {})
            print(f"   Metrics Result Type: {type(metrics)}")
            print(f"   Metrics Result: {metrics}")
            
            # Extract metrics from CallToolResult
            if hasattr(metrics, 'content') and metrics.content:
                content = metrics.content[0] if metrics.content else {}
                if hasattr(content, 'text'):
                    import json
                    try:
                        metrics_data = json.loads(content.text)
                        print(f"   Total Documents: {metrics_data.get('total_documents_processed', 0)}")
                        print(f"   Success Rate: {metrics_data.get('success_rate', 0):.1f}%")
                    except Exception as e:
                        print(f"   Raw content: {content.text}")
                        print(f"   JSON parse error: {e}")
                else:
                    print(f"   Content: {content}")
            else:
                print(f"   Raw result: {metrics}")
            
            print("\n✅ Client disconnected")
        
    except Exception as e:
        print(f"❌ Client test failed: {e}")
        print("\n💡 Make sure the HTTP server is running:")
        print("   uv run mcp-http-server-async")


if __name__ == "__main__":
    asyncio.run(test_http_mcp_client())

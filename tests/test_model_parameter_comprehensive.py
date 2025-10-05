#!/usr/bin/env python3
"""
Uitgebreide test voor model parameter functionaliteit in MCP tools.

Deze test:
1. Haalt beschikbare Ollama modellen op
2. Kiest 2 verschillende modellen voor testing
3. Test alle extractie methoden met beide modellen
4. Test zowel tekst als bestand verwerking
5. Verifieert dat het juiste model wordt gebruikt
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Voeg src toe aan Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import ollama
from mcp_invoice_processor.tools import process_document_text, process_document_file
from mcp_invoice_processor.config import settings


class ModelParameterTest:
    """Test class voor model parameter functionaliteit."""
    
    def __init__(self):
        self.available_models: List[str] = []
        self.test_models: List[str] = []
        self.test_results: Dict[str, Any] = {}
        
    async def get_available_models(self) -> List[str]:
        """Haal beschikbare Ollama modellen op."""
        try:
            print("🔍 Ophalen beschikbare Ollama modellen...")
            models_response = ollama.list()
            
            models = []
            
            # Ollama ListResponse heeft een 'models' attribuut
            if hasattr(models_response, 'models'):
                for model_info in models_response.models:
                    if hasattr(model_info, 'name'):
                        models.append(model_info.name)
                    elif isinstance(model_info, dict) and 'name' in model_info:
                        models.append(model_info['name'])
                    elif isinstance(model_info, str):
                        models.append(model_info)
            
            # Probeer ook als dict
            elif isinstance(models_response, dict):
                if 'models' in models_response:
                    for model_info in models_response['models']:
                        if isinstance(model_info, dict) and 'name' in model_info:
                            models.append(model_info['name'])
                        elif isinstance(model_info, str):
                            models.append(model_info)
            
            if not models:
                print("   Geen modellen gevonden, gebruik default")
                return [settings.ollama.MODEL]
                
            print(f"   Gevonden {len(models)} modellen: {', '.join(models[:5])}{'...' if len(models) > 5 else ''}")
            return models
        except Exception as e:
            print(f"❌ Fout bij ophalen modellen: {e}")
            # Fallback naar default model
            return [settings.ollama.MODEL]
    
    def select_test_models(self, available_models: List[str]) -> List[str]:
        """Selecteer 2 verschillende modellen voor testing."""
        selected = []
        
        # Als er 2+ modellen zijn, gebruik die
        if len(available_models) >= 2:
            # Prioriteit: llama3 varianten
            llama3_models = [m for m in available_models if 'llama3' in m.lower()]
            if llama3_models:
                selected.append(llama3_models[0])
            
            # Prioriteit: andere modellen
            other_models = [m for m in available_models if 'llama3' not in m.lower()]
            if other_models:
                selected.append(other_models[0])
            
            # Als we nog niet genoeg hebben, voeg meer toe
            if len(selected) < 2:
                remaining = [m for m in available_models if m not in selected]
                selected.extend(remaining[:2-len(selected)])
        
        # Als er maar 1 model is, probeer verschillende varianten
        elif len(available_models) == 1:
            base_model = available_models[0]
            selected.append(base_model)
            
            # Probeer verschillende varianten van hetzelfde model
            if 'llama3:8b' in base_model:
                selected.append('llama3.1:8b')
            elif 'llama3.1:8b' in base_model:
                selected.append('llama3:8b')
            elif 'llama3' in base_model:
                # Probeer andere sizes
                if ':8b' in base_model:
                    selected.append(base_model.replace(':8b', ':7b'))
                elif ':7b' in base_model:
                    selected.append(base_model.replace(':7b', ':8b'))
                else:
                    selected.append('llama3:8b')
            else:
                # Voor andere modellen, probeer llama3 als tweede optie
                selected.append('llama3:8b')
        
        # Als er geen modellen zijn, gebruik defaults
        else:
            selected = ['llama3:8b', 'llama3.1:8b']
        
        # Zorg dat we precies 2 unieke modellen hebben
        unique_selected = []
        for model in selected:
            if model not in unique_selected:
                unique_selected.append(model)
            if len(unique_selected) == 2:
                break
        
        # Als we nog steeds niet genoeg hebben, voeg fallback toe
        while len(unique_selected) < 2:
            if 'llama3:8b' not in unique_selected:
                unique_selected.append('llama3:8b')
            elif 'llama3.1:8b' not in unique_selected:
                unique_selected.append('llama3.1:8b')
            else:
                unique_selected.append('llama3:7b')
        
        print(f"✅ Geselecteerde test modellen: {', '.join(unique_selected)}")
        return unique_selected[:2]
    
    def get_test_documents(self) -> Dict[str, str]:
        """Haal test documenten op."""
        return {
            "invoice": """
            Factuur #12345
            Datum: 2024-01-15
            Van: Test Bedrijf BV
            Naar: Klant Bedrijf NV
            Bedrag: €1,234.56
            BTW: €258.26
            Totaal: €1,492.82
            
            Beschrijving: Web development services
            """,
            "cv": """
            Curriculum Vitae
            
            Naam: Jan de Vries
            Email: jan.devries@email.com
            Telefoon: +31 6 12345678
            
            Werkervaring:
            - Software Developer bij TechCorp (2020-2024)
            - Junior Developer bij StartupXYZ (2018-2020)
            
            Opleiding:
            - HBO Informatica, Hogeschool Amsterdam (2014-2018)
            - VWO, Gymnasium Amsterdam (2008-2014)
            
            Vaardigheden:
            - Python, JavaScript, Java
            - React, Node.js, Django
            - Docker, Kubernetes, AWS
            """
        }
    
    async def test_model_parameter_text(self, text: str, doc_type: str, model: str) -> Dict[str, Any]:
        """Test model parameter met tekst verwerking."""
        print(f"\n📝 Test tekst verwerking ({doc_type}) met model '{model}':")
        
        results = {}
        
        # Test alle extractie methoden
        methods = ["hybrid", "json_schema", "prompt_parsing"]
        
        for method in methods:
            try:
                print(f"   🔄 Testen {method} methode...")
                result = await process_document_text(text, method, model)
                
                # Verifieer resultaat
                success = "error" not in result
                model_used = result.get("model_used", "unknown")
                processing_time = result.get("processing_time", 0)
                
                results[method] = {
                    "success": success,
                    "model_used": model_used,
                    "processing_time": processing_time,
                    "document_type": result.get("document_type", "unknown"),
                    "confidence": result.get("confidence", 0)
                }
                
                if success:
                    print(f"      ✅ {method}: {model_used} ({processing_time:.2f}s)")
                else:
                    print(f"      ❌ {method}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"      ❌ {method}: Exception - {e}")
                results[method] = {
                    "success": False,
                    "error": str(e),
                    "model_used": model
                }
        
        return results
    
    async def test_model_parameter_file(self, doc_type: str, model: str) -> Dict[str, Any]:
        """Test model parameter met bestand verwerking."""
        print(f"\n📁 Test bestand verwerking ({doc_type}) met model '{model}':")
        
        # Maak tijdelijk test bestand
        test_file = Path(f"test_{doc_type}.txt")
        test_content = self.get_test_documents()[doc_type]
        
        try:
            # Schrijf test bestand
            test_file.write_text(test_content, encoding='utf-8')
            
            # Test bestand verwerking
            result = await process_document_file(str(test_file), "hybrid", model)
            
            # Verifieer resultaat
            success = "error" not in result
            model_used = result.get("model_used", "unknown")
            processing_time = result.get("processing_time", 0)
            
            print(f"   📁 Bestand verwerking: {model_used} ({processing_time:.2f}s)")
            
            return {
                "success": success,
                "model_used": model_used,
                "processing_time": processing_time,
                "document_type": result.get("document_type", "unknown"),
                "confidence": result.get("confidence", 0)
            }
            
        except Exception as e:
            print(f"   ❌ Bestand verwerking: Exception - {e}")
            return {
                "success": False,
                "error": str(e),
                "model_used": model
            }
        finally:
            # Opruimen test bestand
            if test_file.exists():
                test_file.unlink()
    
    async def run_comprehensive_test(self):
        """Voer uitgebreide test uit."""
        print("🧪 Start uitgebreide model parameter test")
        print("=" * 60)
        
        # Stap 1: Haal modellen op
        self.available_models = await self.get_available_models()
        self.test_models = self.select_test_models(self.available_models)
        
        # Stap 2: Test documenten
        test_docs = self.get_test_documents()
        
        # Stap 3: Test alle combinaties
        for model in self.test_models:
            print(f"\n🤖 Testen met model: {model}")
            print("-" * 40)
            
            model_results = {}
            
            # Test tekst verwerking voor alle document types
            for doc_type, text in test_docs.items():
                text_results = await self.test_model_parameter_text(text, doc_type, model)
                model_results[f"text_{doc_type}"] = text_results
                
                # Test bestand verwerking
                file_results = await self.test_model_parameter_file(doc_type, model)
                model_results[f"file_{doc_type}"] = file_results
            
            self.test_results[model] = model_results
        
        # Stap 4: Samenvatting
        self.print_summary()
    
    def print_summary(self):
        """Print test samenvatting."""
        print("\n" + "=" * 60)
        print("📊 TEST SAMENVATTING")
        print("=" * 60)
        
        for model, results in self.test_results.items():
            print(f"\n🤖 Model: {model}")
            
            total_tests = 0
            successful_tests = 0
            
            for test_name, test_result in results.items():
                if isinstance(test_result, dict) and "success" in test_result:
                    total_tests += 1
                    if test_result["success"]:
                        successful_tests += 1
                elif isinstance(test_result, dict):
                    # Dit is een dict met methoden
                    for method, method_result in test_result.items():
                        if isinstance(method_result, dict) and "success" in method_result:
                            total_tests += 1
                            if method_result["success"]:
                                successful_tests += 1
            
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            print(f"   ✅ Succesvol: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
            
            # Toon model verificatie
            model_verification = []
            for test_name, test_result in results.items():
                if isinstance(test_result, dict) and "model_used" in test_result:
                    model_verification.append(test_result["model_used"])
                elif isinstance(test_result, dict):
                    for method, method_result in test_result.items():
                        if isinstance(method_result, dict) and "model_used" in method_result:
                            model_verification.append(method_result["model_used"])
            
            unique_models = set(model_verification)
            if len(unique_models) == 1 and list(unique_models)[0] == model:
                print(f"   ✅ Model verificatie: Correct ({model})")
            else:
                print(f"   ❌ Model verificatie: Probleem ({unique_models})")
        
        print("\n🎯 CONCLUSIE:")
        all_models_correct = True
        for model, results in self.test_results.items():
            for test_name, test_result in results.items():
                if isinstance(test_result, dict) and "model_used" in test_result:
                    if test_result["model_used"] != model:
                        all_models_correct = False
                        break
                elif isinstance(test_result, dict):
                    for method, method_result in test_result.items():
                        if isinstance(method_result, dict) and "model_used" in method_result:
                            if method_result["model_used"] != model:
                                all_models_correct = False
                                break
        
        if all_models_correct:
            print("✅ Model parameter werkt correct voor alle tests!")
        else:
            print("❌ Er zijn problemen met model parameter doorgeving")


async def main():
    """Hoofdfunctie voor test uitvoering."""
    test = ModelParameterTest()
    await test.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())

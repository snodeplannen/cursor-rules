# Test script voor de MCP Invoice Processor (PowerShell)
# Dit script test de verbinding en functionaliteit van de MCP server

Write-Host "🚀 MCP Invoice Processor Test Script" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Controleer of uv beschikbaar is
try {
    $uvVersion = uv --version
    Write-Host "✅ uv gevonden: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ uv is niet geïnstalleerd. Installeer eerst uv." -ForegroundColor Red
    exit 1
}

# Controleer of alle bestanden bestaan
if (-not (Test-Path "src/mcp_invoice_processor/main.py")) {
    Write-Host "❌ Kan main.py niet vinden. Controleer de projectstructuur." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Projectstructuur gecontroleerd" -ForegroundColor Green

# Test de server start
Write-Host "🔌 Testen van server start..." -ForegroundColor Yellow
try {
    # Test of de server module kan worden geïmporteerd
    $null = uv run python -c "import src.mcp_invoice_processor.main; print('✅ MCP server module succesvol geïmporteerd')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MCP server module werkt correct" -ForegroundColor Green
    } else {
        Write-Host "❌ MCP server module import mislukt" -ForegroundColor Red
        exit 1
    }
    
    # Test of de server kan starten (timeout na 5 seconden)
    Write-Host "🔄 Testen van server startup..." -ForegroundColor Yellow
    $job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        uv run python -m src.mcp_invoice_processor.main
    }
    
    # Wacht even tot de server opstart
    Start-Sleep -Seconds 3
    
    # Controleer of de job nog draait
    if ($job.State -eq "Running") {
        Write-Host "✅ Server start succesvol (STDIO mode)" -ForegroundColor Green
        
        # Stop de job
        Stop-Job $job
        Remove-Job $job
    } else {
        # Controleer de output voor mogelijke fouten
        $jobOutput = Receive-Job $job
        if ($jobOutput -match "error|Error|ERROR") {
            Write-Host "❌ Server start mislukt met fout:" -ForegroundColor Red
            Write-Host $jobOutput -ForegroundColor Red
        } else {
            Write-Host "✅ Server start succesvol (mogelijk direct gestopt in STDIO mode)" -ForegroundColor Green
        }
        
        # Ruim de job op
        if ($job.State -ne "Completed") {
            Stop-Job $job -ErrorAction SilentlyContinue
        }
        Remove-Job $job -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "❌ Server test mislukt: $($_.Exception.Message)" -ForegroundColor Red
}

# Test de FastMCP CLI
Write-Host "🛠️  Testen van FastMCP CLI..." -ForegroundColor Yellow
try {
    $null = uv run fastmcp --help 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ FastMCP CLI werkt" -ForegroundColor Green
    } else {
        Write-Host "❌ FastMCP CLI werkt niet" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ FastMCP CLI test mislukt: $($_.Exception.Message)" -ForegroundColor Red
}

# Test de dependencies
Write-Host "📦 Testen van dependencies..." -ForegroundColor Yellow
try {
    $null = uv run python -c "import fastmcp, ollama, pydantic; print('✅ Alle dependencies geïmporteerd')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies werken correct" -ForegroundColor Green
    } else {
        Write-Host "❌ Probleem met dependencies" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Dependencies test mislukt: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Alle tests voltooid!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Volgende stappen:" -ForegroundColor Cyan
Write-Host "1. Start Ollama op je systeem" -ForegroundColor White
Write-Host "2. Kopieer .env.example naar .env en pas aan" -ForegroundColor White
Write-Host "3. Gebruik de MCP configuratie bestanden" -ForegroundColor White
Write-Host "4. Test met echte PDF documenten" -ForegroundColor White
Write-Host ""
Write-Host "📚 Zie MCP_USAGE.md voor gedetailleerde instructies" -ForegroundColor Cyan

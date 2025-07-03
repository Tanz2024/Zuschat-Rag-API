# ZUS Chatbot API - PowerShell Testing Commands

## Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

## Chat - Product Query
```powershell
$body = @{
    message = "What coffee drinks do you have?"
    session_id = "test123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

## Chat - KL Outlets Count
```powershell
$body = @{
    message = "How many outlets in Kuala Lumpur?"
    session_id = "test123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

## Chat - Selangor Outlets
```powershell
$body = @{
    message = "Find outlets in Selangor"
    session_id = "test123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

## Product Search
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/products?query=iced%20coffee&top_k=5" -Method Get
```

## Outlet Search
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/outlets?query=kuala%20lumpur" -Method Get
```

## Calculator
```powershell
$body = @{
    expression = "15 * 2 + 5"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/calculate" -Method Post -Body $body -ContentType "application/json"
```

## Debug - Sessions
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/debug/sessions" -Method Get
```

## Debug - Vector Store Status
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/debug/vector-store-status" -Method Get
```

---

## Alternative: Using Invoke-WebRequest (More Verbose Output)

If you want to see headers and more details, use `Invoke-WebRequest` instead of `Invoke-RestMethod`:

```powershell
# Health check with full response details
$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get
$response.Content | ConvertFrom-Json | Format-Table
```

## One-Liner Test Script

```powershell
# Quick test of all endpoints
Write-Host "Testing ZUS Chatbot API..." -ForegroundColor Green

Write-Host "`n1. Health Check:" -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

Write-Host "`n2. Chat - KL Outlets:" -ForegroundColor Yellow
$klBody = @{message = "How many outlets in Kuala Lumpur?"; session_id = "test123"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $klBody -ContentType "application/json"

Write-Host "`n3. Chat - Selangor Outlets:" -ForegroundColor Yellow  
$selangorBody = @{message = "Find outlets in Selangor"; session_id = "test123"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $selangorBody -ContentType "application/json"

Write-Host "`n4. Product Search:" -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/products?query=iced%20coffee&top_k=3" -Method Get

Write-Host "`nAPI testing completed!" -ForegroundColor Green
```

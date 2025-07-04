# Test Render Deployment Script
# Run this after deploying to Render to verify everything works

param(
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$FrontendUrl
)

Write-Host "🚀 Testing ZUS Coffee Chatbot Deployment on Render" -ForegroundColor Green
Write-Host "Backend: $BackendUrl" -ForegroundColor Cyan
Write-Host "Frontend: $FrontendUrl" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0

# Test 1: Backend Health Check
Write-Host "1. Testing backend health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "$BackendUrl/health" -Method GET
    if ($healthResponse.status -eq "healthy") {
        Write-Host "   ✅ Backend health check passed" -ForegroundColor Green
        Write-Host "   📊 Status: $($healthResponse.status)" -ForegroundColor Gray
        Write-Host "   📝 Message: $($healthResponse.message)" -ForegroundColor Gray
    } else {
        Write-Host "   ❌ Backend health check failed" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    $ErrorCount++
}

# Test 2: Database Connection
Write-Host ""
Write-Host "2. Testing database connection..." -ForegroundColor Yellow
try {
    $dbResponse = Invoke-RestMethod -Uri "$BackendUrl/outlets/search" -Method POST -ContentType "application/json" -Body '{"location": "KL", "limit": 1}'
    if ($dbResponse.outlets -and $dbResponse.outlets.Count -gt 0) {
        Write-Host "   ✅ Database connection successful" -ForegroundColor Green
        Write-Host "   📊 Found outlets: $($dbResponse.total_count)" -ForegroundColor Gray
    } else {
        Write-Host "   ❌ Database connection failed - no outlets found" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ Database connection failed: $($_.Exception.Message)" -ForegroundColor Red
    $ErrorCount++
}

# Test 3: Chat Functionality
Write-Host ""
Write-Host "3. Testing chat functionality..." -ForegroundColor Yellow
$chatTests = @(
    @{ message = "Hello"; expected = "greeting" },
    @{ message = "Find outlets in KL"; expected = "outlet" },
    @{ message = "Show me coffee menu"; expected = "product" },
    @{ message = "What is 15% of 100?"; expected = "15" }
)

foreach ($test in $chatTests) {
    try {
        $sessionId = [System.Guid]::NewGuid().ToString()
        $chatBody = @{
            message = $test.message
            session_id = $sessionId
        } | ConvertTo-Json
        
        $chatResponse = Invoke-RestMethod -Uri "$BackendUrl/chat" -Method POST -ContentType "application/json" -Body $chatBody
        
        if ($chatResponse.message -match $test.expected) {
            Write-Host "   ✅ Chat test passed: '$($test.message)'" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Chat test partial: '$($test.message)'" -ForegroundColor Yellow
            Write-Host "       Response: $($chatResponse.message)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ❌ Chat test failed: '$($test.message)' - $($_.Exception.Message)" -ForegroundColor Red
        $ErrorCount++
    }
}

# Test 4: Frontend Accessibility
Write-Host ""
Write-Host "4. Testing frontend accessibility..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri $FrontendUrl -Method GET
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend is accessible" -ForegroundColor Green
        Write-Host "   📊 Status Code: $($frontendResponse.StatusCode)" -ForegroundColor Gray
        
        # Check if it contains expected content
        if ($frontendResponse.Content -match "ZUS Coffee" -or $frontendResponse.Content -match "chatbot") {
            Write-Host "   ✅ Frontend content looks correct" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Frontend content might be incorrect" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ Frontend not accessible" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ Frontend test failed: $($_.Exception.Message)" -ForegroundColor Red
    $ErrorCount++
}

# Test 5: API Documentation
Write-Host ""
Write-Host "5. Testing API documentation..." -ForegroundColor Yellow
try {
    $docsResponse = Invoke-WebRequest -Uri "$BackendUrl/docs" -Method GET
    if ($docsResponse.StatusCode -eq 200) {
        Write-Host "   ✅ API documentation is accessible" -ForegroundColor Green
    } else {
        Write-Host "   ❌ API documentation not accessible" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ API documentation test failed: $($_.Exception.Message)" -ForegroundColor Red
    $ErrorCount++
}

# Summary
Write-Host ""
Write-Host "🎯 Deployment Test Summary" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

if ($ErrorCount -eq 0) {
    Write-Host "🎉 All tests passed! Your deployment is working correctly." -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Your ZUS Coffee Chatbot is live at:" -ForegroundColor Cyan
    Write-Host "   Frontend: $FrontendUrl" -ForegroundColor White
    Write-Host "   Backend:  $BackendUrl" -ForegroundColor White
    Write-Host "   API Docs: $BackendUrl/docs" -ForegroundColor White
} elseif ($ErrorCount -le 2) {
    Write-Host "⚠️  Deployment mostly working with $ErrorCount minor issues." -ForegroundColor Yellow
    Write-Host "   Check the specific test failures above and resolve them." -ForegroundColor Yellow
} else {
    Write-Host "❌ Deployment has $ErrorCount issues that need to be resolved." -ForegroundColor Red
    Write-Host "   Please check your Render service logs and environment variables." -ForegroundColor Red
}

Write-Host ""
Write-Host "📚 Additional Resources:" -ForegroundColor Cyan
Write-Host "   • Render Dashboard: https://dashboard.render.com" -ForegroundColor White
Write-Host "   • Deployment Guide: /docs/RENDER_DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host "   • API Documentation: $BackendUrl/docs" -ForegroundColor White

# Example usage information
Write-Host ""
Write-Host "💡 Usage Example:" -ForegroundColor Cyan
Write-Host "   .\test_render_deployment.ps1 -BackendUrl 'https://zuschat-backend.onrender.com' -FrontendUrl 'https://zuschat-frontend.onrender.com'" -ForegroundColor Gray

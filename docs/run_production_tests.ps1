# ZUS Chatbot Production Test Suite
# PowerShell script for comprehensive API testing

param(
    [string]$BaseUrl = "http://localhost:8000",
    [switch]$Verbose
)

Write-Host "🧪 ZUS Chatbot Production Test Suite" -ForegroundColor Green
Write-Host "Testing API at: $BaseUrl" -ForegroundColor Cyan
Write-Host "=" * 60

$TestResults = @()
$TotalTests = 0
$PassedTests = 0
$FailedTests = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [hashtable]$Body = $null,
        [scriptblock]$Validator,
        [string]$Description
    )
    
    $global:TotalTests++
    Write-Host "`n📋 Test: $Name" -ForegroundColor Yellow
    if ($Description) {
        Write-Host "   Description: $Description" -ForegroundColor Gray
    }
    
    try {
        $startTime = Get-Date
        
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            if ($Verbose) {
                Write-Host "   Request Body: $jsonBody" -ForegroundColor Gray
            }
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body $jsonBody -ContentType "application/json" -ErrorAction Stop
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -ErrorAction Stop
        }
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMilliseconds
        
        if ($Verbose) {
            Write-Host "   Response: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Gray
        }
        
        # Run custom validation
        $validationResult = & $Validator $response
        
        if ($validationResult.Passed) {
            Write-Host "   ✅ PASSED" -ForegroundColor Green
            Write-Host "   ⏱️  Duration: $([math]::Round($duration, 2))ms" -ForegroundColor Gray
            if ($validationResult.Message) {
                Write-Host "   📝 $($validationResult.Message)" -ForegroundColor Gray
            }
            $global:PassedTests++
            $status = "PASSED"
        } else {
            Write-Host "   ❌ FAILED: $($validationResult.Message)" -ForegroundColor Red
            $global:FailedTests++
            $status = "FAILED"
        }
        
        $global:TestResults += [PSCustomObject]@{
            Test = $Name
            Status = $status
            Duration = "$([math]::Round($duration, 2))ms"
            Message = $validationResult.Message
        }
        
    } catch {
        Write-Host "   ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $global:FailedTests++
        $global:TestResults += [PSCustomObject]@{
            Test = $Name
            Status = "ERROR"
            Duration = "N/A"
            Message = $_.Exception.Message
        }
    }
}

# Test 1: Health Check
Test-Endpoint -Name "Health Check" -Method "GET" -Url "$BaseUrl/health" -Description "Verify API server is running and healthy" -Validator {
    param($response)
    if ($response.status -eq "healthy" -and $response.version) {
        return @{ Passed = $true; Message = "Server is healthy, version: $($response.version)" }
    }
    return @{ Passed = $false; Message = "Invalid health response" }
}

# Test 2: Product Search (RAG)
Test-Endpoint -Name "Product Search - RAG Engine" -Method "GET" -Url "$BaseUrl/products?query=coffee&top_k=5" -Description "Test vector-based product search using RAG" -Validator {
    param($response)
    if ($response.products -and $response.products.Count -gt 0 -and $response.total_found -ge 0) {
        $productCount = $response.products.Count
        $hasValidProducts = $response.products | Where-Object { $_.name -and $_.name.Length -gt 0 }
        if ($hasValidProducts.Count -eq $productCount) {
            return @{ Passed = $true; Message = "Found $productCount products with valid data" }
        }
    }
    return @{ Passed = $false; Message = "Invalid product search response" }
}

# Test 3: Outlet Search - KL (Text2SQL)
Test-Endpoint -Name "Outlet Search - KL (Text2SQL)" -Method "GET" -Url "$BaseUrl/outlets?query=kuala%20lumpur" -Description "Test Text2SQL for KL outlets (expected: 80)" -Validator {
    param($response)
    if ($response.outlets -and $response.total_found -eq 80) {
        return @{ Passed = $true; Message = "Correctly found 80 KL outlets" }
    } elseif ($response.total_found) {
        return @{ Passed = $false; Message = "Expected 80 KL outlets, got $($response.total_found)" }
    }
    return @{ Passed = $false; Message = "Invalid outlet search response" }
}

# Test 4: Outlet Search - Selangor (Text2SQL)  
Test-Endpoint -Name "Outlet Search - Selangor (Text2SQL)" -Method "GET" -Url "$BaseUrl/outlets?query=selangor" -Description "Test Text2SQL for Selangor outlets (expected: 132)" -Validator {
    param($response)
    if ($response.outlets -and $response.total_found -eq 132) {
        return @{ Passed = $true; Message = "Correctly found 132 Selangor outlets" }
    } elseif ($response.total_found) {
        return @{ Passed = $false; Message = "Expected 132 Selangor outlets, got $($response.total_found)" }
    }
    return @{ Passed = $false; Message = "Invalid outlet search response" }
}

# Test 5: Calculator Tool
Test-Endpoint -Name "Calculator Tool" -Method "POST" -Url "$BaseUrl/calculate" -Body @{ expression = "15 * 2 + 5" } -Description "Test mathematical calculation tool" -Validator {
    param($response)
    if ($response.result -eq 35 -and $response.is_valid -eq $true) {
        return @{ Passed = $true; Message = "Calculation correct: 15 * 2 + 5 = 35" }
    }
    return @{ Passed = $false; Message = "Incorrect calculation result: expected 35, got $($response.result)" }
}

# Test 6: Chat - Product Intent (RAG Integration)
Test-Endpoint -Name "Chat - Product Intent (RAG)" -Method "POST" -Url "$BaseUrl/chat" -Body @{ message = "What coffee drinks do you have?"; session_id = "test_rag" } -Description "Test chat integration with RAG for products" -Validator {
    param($response)
    if ($response.intent -eq "product_search" -and $response.message -and $response.products) {
        $productCount = if ($response.products) { $response.products.Count } else { 0 }
        return @{ Passed = $true; Message = "Product intent detected, returned $productCount products" }
    }
    return @{ Passed = $false; Message = "Failed to detect product intent or return products" }
}

# Test 7: Chat - Outlet Intent (Text2SQL Integration)
Test-Endpoint -Name "Chat - Outlet Intent (Text2SQL)" -Method "POST" -Url "$BaseUrl/chat" -Body @{ message = "How many outlets in Kuala Lumpur?"; session_id = "test_sql" } -Description "Test chat integration with Text2SQL for outlets" -Validator {
    param($response)
    if ($response.intent -eq "outlet_search" -and $response.message -match "80") {
        return @{ Passed = $true; Message = "Outlet intent detected, correctly reported 80 KL outlets" }
    } elseif ($response.intent -eq "outlet_search") {
        return @{ Passed = $false; Message = "Outlet intent detected but incorrect count in response" }
    }
    return @{ Passed = $false; Message = "Failed to detect outlet intent" }
}

# Test 8: Chat - Calculation Intent
Test-Endpoint -Name "Chat - Calculation Intent" -Method "POST" -Url "$BaseUrl/chat" -Body @{ message = "Calculate 25 + 15"; session_id = "test_calc" } -Description "Test chat integration with calculator tool" -Validator {
    param($response)
    if ($response.intent -eq "calculation" -and ($response.message -match "40" -or $response.calculation_result -eq 40)) {
        return @{ Passed = $true; Message = "Calculation intent detected, result: 40" }
    }
    return @{ Passed = $false; Message = "Failed to detect calculation intent or incorrect result" }
}

# Test 9: Multi-turn Conversation
Test-Endpoint -Name "Multi-turn Conversation" -Method "POST" -Url "$BaseUrl/chat" -Body @{ message = "What about the prices?"; session_id = "test_rag" } -Description "Test conversation context maintenance" -Validator {
    param($response)
    if ($response.session_id -eq "test_rag" -and $response.message) {
        return @{ Passed = $true; Message = "Session context maintained" }
    }
    return @{ Passed = $false; Message = "Session context not maintained" }
}

# Test 10: Error Handling - Empty Message
Test-Endpoint -Name "Error Handling - Empty Message" -Method "POST" -Url "$BaseUrl/chat" -Body @{ message = ""; session_id = "test_error" } -Description "Test API error handling for invalid input" -Validator {
    param($response)
    # This should fail with 400, so we catch the exception in the main try-catch
    return @{ Passed = $false; Message = "Should have returned 400 error" }
}

# Test 11: Performance - Rapid Requests
Write-Host "`n📋 Test: Performance - Rapid Requests" -ForegroundColor Yellow
Write-Host "   Description: Test handling of multiple concurrent requests" -ForegroundColor Gray

$TotalTests++
$startTime = Get-Date
$jobs = @()

for ($i = 1; $i -le 10; $i++) {
    $jobs += Start-Job -ScriptBlock {
        param($url)
        try {
            Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 5
        } catch {
            $null
        }
    } -ArgumentList "$BaseUrl/health"
}

$results = $jobs | Wait-Job | Receive-Job
$jobs | Remove-Job

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalMilliseconds
$successCount = ($results | Where-Object { $_.status -eq "healthy" }).Count

if ($successCount -ge 8) {
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    Write-Host "   📝 Successfully handled $successCount/10 concurrent requests in $([math]::Round($duration, 2))ms" -ForegroundColor Gray
    $PassedTests++
    $TestResults += [PSCustomObject]@{
        Test = "Performance - Rapid Requests"
        Status = "PASSED"
        Duration = "$([math]::Round($duration, 2))ms"
        Message = "$successCount/10 requests successful"
    }
} else {
    Write-Host "   ❌ FAILED" -ForegroundColor Red
    Write-Host "   📝 Only $successCount/10 requests successful" -ForegroundColor Red
    $FailedTests++
    $TestResults += [PSCustomObject]@{
        Test = "Performance - Rapid Requests"
        Status = "FAILED"
        Duration = "$([math]::Round($duration, 2))ms"
        Message = "Only $successCount/10 requests successful"
    }
}

# Test 12: Debug Endpoints
Test-Endpoint -Name "Debug - Vector Store Status" -Method "GET" -Url "$BaseUrl/debug/vector-store-status" -Description "Test vector store health and statistics" -Validator {
    param($response)
    if ($response.index_loaded -eq $true -and $response.total_products -gt 0) {
        return @{ Passed = $true; Message = "Vector store loaded with $($response.total_products) products" }
    }
    return @{ Passed = $false; Message = "Vector store not properly loaded" }
}

Test-Endpoint -Name "Debug - Sessions" -Method "GET" -Url "$BaseUrl/debug/sessions" -Description "Test session management status" -Validator {
    param($response)
    if ($response.total_sessions -ge 0 -and $response.session_ids) {
        return @{ Passed = $true; Message = "Session manager working, $($response.total_sessions) active sessions" }
    }
    return @{ Passed = $false; Message = "Session manager not responding correctly" }
}

# Final Results Summary
Write-Host "`n" + "=" * 60
Write-Host "📊 TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host "Total Tests: $TotalTests" -ForegroundColor White
Write-Host "Passed: $PassedTests" -ForegroundColor Green  
Write-Host "Failed: $FailedTests" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($PassedTests / $TotalTests) * 100, 1))%" -ForegroundColor $(if ($PassedTests -eq $TotalTests) { "Green" } else { "Yellow" })

Write-Host "`n📋 Detailed Results:" -ForegroundColor White
$TestResults | Format-Table -AutoSize

# Production Readiness Assessment
Write-Host "`n🎯 PRODUCTION READINESS ASSESSMENT" -ForegroundColor Cyan
Write-Host "=" * 60

$criticalTests = @(
    "Health Check",
    "Product Search - RAG Engine", 
    "Outlet Search - KL (Text2SQL)",
    "Outlet Search - Selangor (Text2SQL)",
    "Chat - Product Intent (RAG)",
    "Chat - Outlet Intent (Text2SQL)"
)

$criticalPassed = ($TestResults | Where-Object { $_.Test -in $criticalTests -and $_.Status -eq "PASSED" }).Count
$criticalTotal = $criticalTests.Count

if ($criticalPassed -eq $criticalTotal) {
    Write-Host "✅ PRODUCTION READY" -ForegroundColor Green
    Write-Host "All critical systems (RAG, Text2SQL, Chat) are functioning correctly." -ForegroundColor Green
} else {
    Write-Host "❌ NOT PRODUCTION READY" -ForegroundColor Red
    Write-Host "Critical test failures detected. Review failed tests before deployment." -ForegroundColor Red
}

Write-Host "`nCritical Systems Status:" -ForegroundColor White
Write-Host "• RAG Engine: $(if (($TestResults | Where-Object { $_.Test -like "*RAG*" -and $_.Status -eq "PASSED" }).Count -gt 0) { "✅ OK" } else { "❌ FAILED" })"
Write-Host "• Text2SQL Engine: $(if (($TestResults | Where-Object { $_.Test -like "*Text2SQL*" -and $_.Status -eq "PASSED" }).Count -ge 2) { "✅ OK" } else { "❌ FAILED" })"
Write-Host "• Chat Integration: $(if (($TestResults | Where-Object { $_.Test -like "Chat -*" -and $_.Status -eq "PASSED" }).Count -ge 2) { "✅ OK" } else { "❌ FAILED" })"
Write-Host "• Data Accuracy: $(if (($TestResults | Where-Object { ($_.Test -like "*KL*" -or $_.Test -like "*Selangor*") -and $_.Status -eq "PASSED" }).Count -ge 2) { "✅ OK" } else { "❌ FAILED" })"

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
if ($FailedTests -eq 0) {
    Write-Host "• System is ready for production deployment"
    Write-Host "• Consider setting up monitoring and alerting"
    Write-Host "• Schedule regular health checks"
} else {
    Write-Host "• Review and fix failed tests"
    Write-Host "• Re-run test suite after fixes"
    Write-Host "• Verify data accuracy for failed outlet counts"
}

Write-Host "`n" + "=" * 60
Write-Host "Test completed at: $(Get-Date)" -ForegroundColor Gray

# Return exit code based on test results
if ($FailedTests -eq 0) {
    exit 0
} else {
    exit 1
}

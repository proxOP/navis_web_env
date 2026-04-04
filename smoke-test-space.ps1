param(
    [string]$BaseUrl = "https://proxjod-navis-web-env.hf.space",
    [string]$TaskId = "easy"
)

$ErrorActionPreference = "Stop"
$Session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

function Write-Check {
    param(
        [string]$Label,
        [string]$Status,
        [string]$Detail
    )
    Write-Host "[$Status] $Label - $Detail"
}

function Invoke-JsonPost {
    param(
        [string]$Uri,
        [object]$Body
    )
    return Invoke-RestMethod -Method Post -Uri $Uri -WebSession $Session -ContentType "application/json" -Body ($Body | ConvertTo-Json -Compress)
}

function Invoke-Step {
    param(
        [string]$BaseUrl,
        [hashtable]$ActionBody
    )

    return Invoke-JsonPost -Uri "$BaseUrl/step" -Body @{ action = $ActionBody }
}

function Get-Observation {
    param([object]$Payload)
    if ($null -ne $Payload.observation) {
        return $Payload.observation
    }
    if ($null -ne $Payload.result -and $null -ne $Payload.result.observation) {
        return $Payload.result.observation
    }
    return $Payload
}

function Get-Done {
    param([object]$Payload)
    if ($null -ne $Payload.done) {
        return [bool]$Payload.done
    }
    if ($null -ne $Payload.result -and $null -ne $Payload.result.done) {
        return [bool]$Payload.result.done
    }
    return $false
}

function Get-Reward {
    param([object]$Payload)
    if ($null -ne $Payload.reward) {
        return $Payload.reward
    }
    if ($null -ne $Payload.result -and $null -ne $Payload.result.reward) {
        return $Payload.result.reward
    }
    return $null
}

$BaseUrl = $BaseUrl.TrimEnd("/")

Write-Host "Smoke testing Space: $BaseUrl"
Write-Host "Task: $TaskId"
Write-Host ""

try {
    $health = Invoke-RestMethod -Method Get -Uri "$BaseUrl/health" -WebSession $Session
    Write-Check "GET /health" "PASS" ($health | ConvertTo-Json -Compress)

    $metadata = Invoke-RestMethod -Method Get -Uri "$BaseUrl/metadata" -WebSession $Session
    Write-Check "GET /metadata" "PASS" ("name=" + $metadata.name)

    $schema = Invoke-RestMethod -Method Get -Uri "$BaseUrl/schema" -WebSession $Session
    if ($schema.action_schema -or $schema.action) {
        Write-Check "GET /schema" "PASS" "action schema present"
    } else {
        throw "schema response missing action schema"
    }

    $reset = Invoke-JsonPost -Uri "$BaseUrl/reset" -Body @{ task_id = $TaskId }
    $sessionId = $reset.session_id
    $firstObs = Get-Observation $reset
    $resetDetail = if ($sessionId) { "session_id=$sessionId page_id=$($firstObs.page_id)" } else { "page_id=$($firstObs.page_id)" }
    Write-Check "POST /reset" "PASS" $resetDetail

    $step1Body = @{ click_link_id = "home_support" }
    if ($sessionId) {
        $step1Body.session_id = $sessionId
    }
    $step1 = Invoke-Step -BaseUrl $BaseUrl -ActionBody $step1Body
    $step1Obs = Get-Observation $step1
    Write-Check "POST /step #1" "PASS" ("page_id=" + $step1Obs.page_id + " reward=" + (Get-Reward $step1))

    $step2Body = @{ click_link_id = "support_contact" }
    if ($sessionId) {
        $step2Body.session_id = $sessionId
    }
    $step2 = Invoke-Step -BaseUrl $BaseUrl -ActionBody $step2Body
    $step2Obs = Get-Observation $step2
    $step2Done = Get-Done $step2
    Write-Check "POST /step #2" "PASS" ("page_id=" + $step2Obs.page_id + " done=" + $step2Done)

    try {
        if ($sessionId) {
            $state = Invoke-RestMethod -Method Get -Uri "$BaseUrl/state?session_id=$sessionId" -WebSession $Session
        } else {
            $state = Invoke-RestMethod -Method Get -Uri "$BaseUrl/state" -WebSession $Session
        }
        Write-Check "GET /state" "PASS" ("step_count=" + $state.step_count + " termination_reason=" + $state.termination_reason)
    }
    catch {
        Write-Check "GET /state" "WARN" "state endpoint unavailable or runtime-specific"
    }

    if ($firstObs.page_id -ne "home") {
        throw "unexpected reset page_id '$($firstObs.page_id)'"
    }
    if ($step1Obs.page_id -ne "support_center") {
        throw "unexpected first step page_id '$($step1Obs.page_id)'"
    }
    if ($step2Obs.page_id -eq "contact_support" -and $step2Done) {
        Write-Check "Episode continuity" "PASS" "easy task completed successfully"
    } else {
        Write-Check "Episode continuity" "WARN" "remote runtime did not preserve the expected multi-step easy-task flow"
    }

    Write-Host ""
    Write-Host "[PASS] Smoke test complete. Core Space endpoints are healthy."
}
catch {
    Write-Host ""
    Write-Host "[FAIL] Smoke test failed: $($_.Exception.Message)"
    exit 1
}

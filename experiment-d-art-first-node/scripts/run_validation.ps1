param()

$ErrorActionPreference = "Stop"
$experimentRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$diagnostics = Join-Path $experimentRoot "diagnostics"
$godotConsole = (Get-Command godot_console -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $diagnostics | Out-Null

python (Join-Path $PSScriptRoot "preflight.py")
if ($LASTEXITCODE -ne 0) { throw "Preflight failed" }

python (Join-Path $PSScriptRoot "render_geometry_diagnostic.py")
if ($LASTEXITCODE -ne 0) { throw "Diagnostic rendering failed" }

& $godotConsole --headless --editor --path $experimentRoot --quit --log-file (Join-Path $diagnostics "godot_import.log")
if ($LASTEXITCODE -ne 0) { throw "Godot import failed" }

$normalResult = Join-Path $diagnostics "test_results.json"
if (Test-Path -LiteralPath $normalResult) { Remove-Item -LiteralPath $normalResult -Force }
& $godotConsole --headless --path $experimentRoot --scene res://tests/test_node.tscn --log-file (Join-Path $diagnostics "godot_test.log")
if ($LASTEXITCODE -ne 0) { throw "Normal playability suite exited nonzero" }
if (-not (Test-Path -LiteralPath $normalResult)) { throw "Normal suite produced no result file; engine exit code alone is not proof" }
$normalPayload = Get-Content -LiteralPath $normalResult -Raw | ConvertFrom-Json
if (-not $normalPayload.passed) { throw "Normal playability assertions failed" }

$mutations = @("shift_fountain", "corridor_blocker")
foreach ($mutation in $mutations) {
    $mutationResult = Join-Path $diagnostics "test_results_$mutation.json"
    if (Test-Path -LiteralPath $mutationResult) { Remove-Item -LiteralPath $mutationResult -Force }
    & $godotConsole --headless --path $experimentRoot --scene res://tests/test_node.tscn --log-file (Join-Path $diagnostics "godot_test_$mutation.log") -- "--mutation=$mutation"
    if ($LASTEXITCODE -eq 0) { throw "Mutation was not detected: $mutation" }
    if (-not (Test-Path -LiteralPath $mutationResult)) { throw "Mutation run produced no result file: $mutation" }
    $mutationPayload = Get-Content -LiteralPath $mutationResult -Raw | ConvertFrom-Json
    if ($mutationPayload.passed) { throw "Mutation incorrectly reported passed: $mutation" }
    if ($mutationPayload.mutation -ne $mutation) { throw "Mutation result identity mismatch: $mutation" }
    $failedTests = @($mutationPayload.results | Where-Object { $_.status -eq "FAIL" } | ForEach-Object { $_.test })
    if ($mutation -eq "shift_fountain") {
        if (-not $failedTests.Contains("collision_probe_contract") -or -not $failedTests.Contains("fountain_blocking")) {
            throw "Shifted fountain did not fail the required geometry checks"
        }
        $fountainResult = $mutationPayload.results | Where-Object { $_.test -eq "fountain_blocking" }
        if ($fountainResult.evidence.movement.outcome -ne "REACHED") {
            throw "Shifted fountain was not detected through an incorrectly reachable art-space center"
        }
    }
    if ($mutation -eq "corridor_blocker") {
        if (-not $failedTests.Contains("lower_court_outbound")) {
            throw "Corridor blocker did not fail lower_court_outbound"
        }
        $corridorResult = $mutationPayload.results | Where-Object { $_.test -eq "lower_court_outbound" }
        $blockedLegs = @($corridorResult.evidence.legs | Where-Object { $_.outcome -eq "BLOCKED" -and $_.collider_name -eq "MutationCorridorBlocker" })
        if ($blockedLegs.Count -lt 1) {
            throw "Corridor mutation failed for the wrong collider"
        }
    }
    Write-Output "[EXPECTED FAILURE DETECTED] $mutation"
}

Write-Output "VALIDATION_OK: normal suite passed and both deliberate mutations were rejected."

param()

$ErrorActionPreference = "Stop"
$experimentRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$diagnostics = Join-Path $experimentRoot "diagnostics"
$godotConsole = (Get-Command godot_console -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $diagnostics | Out-Null

$requiredTests = @(
    "asset_integrity",
    "node_001_regression",
    "portal_gating",
    "piazza_route_to_portal",
    "transition_to_belvedere",
    "belvedere_route",
    "belvedere_boundary",
    "round_trip_return"
)

$sourcePaths = [ordered]@{
    piazza_art = Join-Path $experimentRoot "assets\piazza.png"
    belvedere_art = Join-Path $experimentRoot "assets\belvedere.png"
    atlas = Join-Path $experimentRoot "assets\traveler_walk_sheet.png"
    foreground = Join-Path $experimentRoot "assets\southwest_planter_foreground.png"
    piazza_geometry = Join-Path $experimentRoot "data\node_001_geometry.json"
    belvedere_geometry = Join-Path $experimentRoot "data\node_002_geometry.json"
    world_script = Join-Path $experimentRoot "scripts\node_world.gd"
    player_script = Join-Path $experimentRoot "scripts\player_controller.gd"
    test_script = Join-Path $experimentRoot "tests\test_node.gd"
    main_scene = Join-Path $experimentRoot "scenes\main.tscn"
}

function Assert-SourceHashes {
    param([Parameter(Mandatory = $true)]$Payload)
    foreach ($entry in $sourcePaths.GetEnumerator()) {
        $actual = (Get-FileHash -LiteralPath $entry.Value -Algorithm SHA256).Hash
        $recorded = $Payload.source_hashes.($entry.Key)
        if ($recorded -ne $actual) {
            throw "Source hash mismatch for $($entry.Key): result=$recorded current=$actual"
        }
    }
}

function Assert-TestInventory {
    param([Parameter(Mandatory = $true)]$Payload)
    $names = @($Payload.results | ForEach-Object { $_.test })
    if ($names.Count -ne $requiredTests.Count) {
        throw "Test inventory count mismatch: expected $($requiredTests.Count), got $($names.Count)"
    }
    foreach ($required in $requiredTests) {
        if (@($names | Where-Object { $_ -eq $required }).Count -ne 1) {
            throw "Required test missing or duplicated: $required"
        }
    }
}

function Get-TestResult {
    param(
        [Parameter(Mandatory = $true)]$Payload,
        [Parameter(Mandatory = $true)][string]$Name
    )
    return $Payload.results | Where-Object { $_.test -eq $Name } | Select-Object -First 1
}

function Assert-ExactFailures {
    param(
        [Parameter(Mandatory = $true)]$Payload,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$ExpectedFailures
    )
    $actual = @($Payload.results | Where-Object { $_.status -eq "FAIL" } | ForEach-Object { $_.test } | Sort-Object)
    $expected = @($ExpectedFailures | Sort-Object)
    if ($actual.Count -ne $expected.Count) {
        throw "Failure count mismatch: expected [$($expected -join ', ')], got [$($actual -join ', ')]"
    }
    for ($index = 0; $index -lt $expected.Count; $index++) {
        if ($actual[$index] -ne $expected[$index]) {
            throw "Failure set mismatch: expected [$($expected -join ', ')], got [$($actual -join ', ')]"
        }
    }
    if ([int]$Payload.failure_count -ne $actual.Count) {
        throw "Payload failure_count disagrees with failed result count"
    }
}

function Assert-MutationCause {
    param(
        [Parameter(Mandatory = $true)][string]$Mutation,
        [Parameter(Mandatory = $true)]$Payload
    )
    switch ($Mutation) {
        "wrong_belvedere_spawn" {
            $result = Get-TestResult -Payload $Payload -Name "transition_to_belvedere"
            if ([double]$result.evidence.actual_spawn[0] -ne 976.0 -or [double]$result.evidence.actual_spawn[1] -ne 850.0) {
                throw "Wrong-spawn mutation did not apply the declared +140 px X offset"
            }
        }
        "broken_return" {
            $result = Get-TestResult -Payload $Payload -Name "round_trip_return"
            if ($result.evidence.accepted) { throw "Broken-return mutation unexpectedly accepted the return" }
            if ($result.evidence.current_node -ne "belvedere") { throw "Broken-return mutation failed for an unexpected state" }
        }
        "shift_piazza_portal_x100" {
            $result = Get-TestResult -Payload $Payload -Name "portal_gating"
            if ($result.evidence.expected_anchor_active) { throw "Shifted portal still accepted the declared source-space anchor" }
        }
        "belvedere_corridor_blocker" {
            $result = Get-TestResult -Payload $Payload -Name "belvedere_route"
            $blocked = @($result.evidence.legs | Where-Object { $_.outcome -eq "BLOCKED" -and $_.collider_name -eq "MutationBelvedereBlocker" })
            if ($blocked.Count -lt 1) { throw "Belvedere blocker mutation did not collide with MutationBelvedereBlocker" }
        }
        default { throw "No causal assertion is defined for mutation: $Mutation" }
    }
}

python (Join-Path $PSScriptRoot "preflight.py")
if ($LASTEXITCODE -ne 0) { throw "Preflight failed" }

python (Join-Path $PSScriptRoot "render_geometry_diagnostic.py")
if ($LASTEXITCODE -ne 0) { throw "Diagnostic rendering failed" }

$importLog = Join-Path $diagnostics "godot_import.log"
& $godotConsole --headless --editor --path $experimentRoot --quit --log-file $importLog
if ($LASTEXITCODE -ne 0) { throw "Godot import failed" }
$importFailures = @(Select-String -LiteralPath $importLog -Pattern "SCRIPT ERROR", "Parse Error", "Failed to load script")
if ($importFailures.Count -gt 0) { throw "Godot import log contains script failures" }

$normalResult = Join-Path $diagnostics "test_results.json"
if (Test-Path -LiteralPath $normalResult) { Remove-Item -LiteralPath $normalResult -Force }
& $godotConsole --headless --path $experimentRoot --scene res://tests/test_node.tscn --log-file (Join-Path $diagnostics "godot_test.log")
if ($LASTEXITCODE -ne 0) { throw "Normal Experiment F suite exited nonzero" }
if (-not (Test-Path -LiteralPath $normalResult)) { throw "Normal suite produced no fresh result file" }
$normalPayload = Get-Content -LiteralPath $normalResult -Raw | ConvertFrom-Json
if (-not $normalPayload.passed) { throw "Normal Experiment F assertions failed" }
Assert-TestInventory -Payload $normalPayload
Assert-ExactFailures -Payload $normalPayload -ExpectedFailures @()
Assert-SourceHashes -Payload $normalPayload

$expectedMutationFailures = [ordered]@{
    wrong_belvedere_spawn = @("transition_to_belvedere")
    broken_return = @("round_trip_return")
    shift_piazza_portal_x100 = @("portal_gating")
    belvedere_corridor_blocker = @("belvedere_route")
}

foreach ($mutation in $expectedMutationFailures.Keys) {
    $mutationResult = Join-Path $diagnostics "test_results_$mutation.json"
    if (Test-Path -LiteralPath $mutationResult) { Remove-Item -LiteralPath $mutationResult -Force }
    & $godotConsole --headless --path $experimentRoot --scene res://tests/test_node.tscn --log-file (Join-Path $diagnostics "godot_test_$mutation.log") -- "--mutation=$mutation"
    if ($LASTEXITCODE -eq 0) { throw "Mutation was not detected: $mutation" }
    if (-not (Test-Path -LiteralPath $mutationResult)) { throw "Mutation produced no fresh result file: $mutation" }
    $payload = Get-Content -LiteralPath $mutationResult -Raw | ConvertFrom-Json
    if ($payload.passed) { throw "Mutation incorrectly reported passed: $mutation" }
    if ($payload.mutation -ne $mutation) { throw "Mutation result identity mismatch: $mutation" }
    Assert-TestInventory -Payload $payload
    Assert-ExactFailures -Payload $payload -ExpectedFailures $expectedMutationFailures[$mutation]
    Assert-MutationCause -Mutation $mutation -Payload $payload
    Assert-SourceHashes -Payload $payload
    Write-Output "[EXPECTED CAUSAL FAILURE] $mutation"
}

$renderCapturePaths = @(
    (Join-Path $diagnostics "runtime_belvedere_capture.png"),
    (Join-Path $diagnostics "runtime_belvedere_baseline.png"),
    (Join-Path $diagnostics "render_capture_verification.json")
)
foreach ($path in $renderCapturePaths) {
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}
$captureArguments = @(
    "--path", ".",
    "--scene", "res://tests/capture_render.tscn",
    "--audio-driver", "Dummy",
    "--log-file", "diagnostics/capture_render_real.log"
)
$captureProcess = Start-Process -FilePath $godotConsole -ArgumentList $captureArguments -WorkingDirectory $experimentRoot -WindowStyle Hidden -Wait -PassThru
if ($captureProcess.ExitCode -ne 0) { throw "Real-renderer belvedere capture exited nonzero" }
foreach ($path in $renderCapturePaths[0..1]) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Real renderer produced no fresh capture: $path" }
}
python (Join-Path $PSScriptRoot "verify_belvedere_capture.py")
if ($LASTEXITCODE -ne 0) { throw "Belvedere capture failed independent pixel verification" }
if (-not (Test-Path -LiteralPath $renderCapturePaths[2])) { throw "Render verifier produced no fresh report" }
$renderPayload = Get-Content -LiteralPath $renderCapturePaths[2] -Raw | ConvertFrom-Json
if (-not $renderPayload.passed) { throw "Render verification payload is not passing" }

Write-Output "VALIDATION_OK: Experiment F passed 8 normal checks, 4 causal mutations, and real-renderer verification."

param()

$ErrorActionPreference = "Stop"
$experimentRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$diagnostics = Join-Path $experimentRoot "diagnostics"
$godotConsole = (Get-Command godot_console -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $diagnostics | Out-Null

$requiredTests = @(
    "asset_integrity",
    "visible_art_policy",
    "runtime_contract",
    "quest_order_contract",
    "complete_quest_loop",
    "well_collision",
    "outer_boundary"
)

$sourcePaths = [ordered]@{
    town = Join-Path $experimentRoot "assets\moonroot_hollow.png"
    traveler = Join-Path $experimentRoot "assets\traveler_walk_sheet.png"
    geometry = Join-Path $experimentRoot "data\town_geometry.json"
    world_script = Join-Path $experimentRoot "scripts\town_world.gd"
    player_script = Join-Path $experimentRoot "scripts\player_controller.gd"
    test_script = Join-Path $experimentRoot "tests\test_town.gd"
    main_scene = Join-Path $experimentRoot "scenes\main.tscn"
}

function Assert-SourceHashes {
    param([Parameter(Mandatory = $true)]$Payload)
    foreach ($entry in $sourcePaths.GetEnumerator()) {
        $actual = (Get-FileHash -LiteralPath $entry.Value -Algorithm SHA256).Hash
        if ($Payload.source_hashes.($entry.Key) -ne $actual) {
            throw "Source hash mismatch for $($entry.Key)"
        }
    }
}

function Assert-TestInventory {
    param([Parameter(Mandatory = $true)]$Payload)
    $names = @($Payload.results | ForEach-Object { $_.test })
    if ($names.Count -ne $requiredTests.Count) { throw "Test inventory count mismatch" }
    foreach ($required in $requiredTests) {
        if (@($names | Where-Object { $_ -eq $required }).Count -ne 1) {
            throw "Required test missing or duplicated: $required"
        }
    }
}

function Get-TestResult {
    param([Parameter(Mandatory = $true)]$Payload, [Parameter(Mandatory = $true)][string]$Name)
    return $Payload.results | Where-Object { $_.test -eq $Name } | Select-Object -First 1
}

function Assert-ExactFailures {
    param(
        [Parameter(Mandatory = $true)]$Payload,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$ExpectedFailures
    )
    $actual = @($Payload.results | Where-Object { $_.status -eq "FAIL" } | ForEach-Object { $_.test } | Sort-Object)
    $expected = @($ExpectedFailures | Sort-Object)
    if (($actual -join "|") -ne ($expected -join "|")) {
        throw "Failure set mismatch: expected [$($expected -join ', ')], got [$($actual -join ', ')]"
    }
    if ([int]$Payload.failure_count -ne $actual.Count) { throw "Failure count disagrees with results" }
}

function Assert-MutationCause {
    param([Parameter(Mandatory = $true)][string]$Mutation, [Parameter(Mandatory = $true)]$Payload)
    switch ($Mutation) {
        "allow_early_well" {
            $result = Get-TestResult -Payload $Payload -Name "quest_order_contract"
            if (-not $result.evidence.accepted_before_apothecary -or $result.evidence.quest_state_after_attempt -ne "deliver_moonwater") {
                throw "Early-well mutation failed for an unexpected cause"
            }
        }
        "shift_apothecary_x180" {
            $result = Get-TestResult -Payload $Payload -Name "complete_quest_loop"
            $firstStage = $result.evidence.stages | Select-Object -First 1
            if ($firstStage.landmark -ne "apothecary" -or $firstStage.accepted) {
                throw "Shifted-apothecary mutation failed for an unexpected cause"
            }
        }
        "missing_completion" {
            $result = Get-TestResult -Payload $Payload -Name "complete_quest_loop"
            if ($result.evidence.final_state -ne "deliver_moonwater") {
                throw "Missing-completion mutation did not leave the quest in delivery state"
            }
        }
        "corridor_blocker" {
            $result = Get-TestResult -Payload $Payload -Name "complete_quest_loop"
            $blocked = @($result.evidence.routes.legs | Where-Object { $_.outcome -eq "BLOCKED" -and $_.collider_name -eq "MutationCorridorBlocker" })
            if ($blocked.Count -lt 1) { throw "Corridor mutation did not collide with MutationCorridorBlocker" }
        }
        default { throw "No causal assertion for mutation: $Mutation" }
    }
}

python (Join-Path $PSScriptRoot "preflight.py")
if ($LASTEXITCODE -ne 0) { throw "Preflight failed" }

$importLog = Join-Path $diagnostics "godot_import.log"
& $godotConsole --headless --editor --path $experimentRoot --quit --log-file $importLog
if ($LASTEXITCODE -ne 0) { throw "Godot import failed" }
$importFailures = @(Select-String -LiteralPath $importLog -Pattern "SCRIPT ERROR", "Parse Error", "Failed to load script")
if ($importFailures.Count -gt 0) { throw "Godot import log contains script failures" }

$normalResult = Join-Path $diagnostics "test_results.json"
if (Test-Path -LiteralPath $normalResult) { Remove-Item -LiteralPath $normalResult -Force }
& $godotConsole --headless --path $experimentRoot --scene res://tests/test_town.tscn --log-file (Join-Path $diagnostics "godot_test.log")
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $normalResult)) { throw "Normal suite failed or produced no fresh result" }
$normalPayload = Get-Content -LiteralPath $normalResult -Raw | ConvertFrom-Json
if (-not $normalPayload.passed) { throw "Normal assertions failed" }
Assert-TestInventory -Payload $normalPayload
Assert-ExactFailures -Payload $normalPayload -ExpectedFailures @()
Assert-SourceHashes -Payload $normalPayload

$expectedMutationFailures = [ordered]@{
    allow_early_well = @("quest_order_contract")
    shift_apothecary_x180 = @("complete_quest_loop")
    missing_completion = @("complete_quest_loop")
    corridor_blocker = @("complete_quest_loop")
}

foreach ($mutation in $expectedMutationFailures.Keys) {
    $mutationResult = Join-Path $diagnostics "test_results_$mutation.json"
    if (Test-Path -LiteralPath $mutationResult) { Remove-Item -LiteralPath $mutationResult -Force }
    & $godotConsole --headless --path $experimentRoot --scene res://tests/test_town.tscn --log-file (Join-Path $diagnostics "godot_test_$mutation.log") -- "--mutation=$mutation"
    if ($LASTEXITCODE -eq 0 -or -not (Test-Path -LiteralPath $mutationResult)) { throw "Mutation was not detected: $mutation" }
    $payload = Get-Content -LiteralPath $mutationResult -Raw | ConvertFrom-Json
    if ($payload.passed -or $payload.mutation -ne $mutation) { throw "Mutation payload is invalid: $mutation" }
    Assert-TestInventory -Payload $payload
    Assert-ExactFailures -Payload $payload -ExpectedFailures $expectedMutationFailures[$mutation]
    Assert-MutationCause -Mutation $mutation -Payload $payload
    Assert-SourceHashes -Payload $payload
    Write-Output "[EXPECTED CAUSAL FAILURE] $mutation"
}

$capturePaths = @(
    (Join-Path $diagnostics "runtime_town_capture.png"),
    (Join-Path $diagnostics "runtime_town_baseline.png"),
    (Join-Path $diagnostics "render_capture_verification.json")
)
foreach ($path in $capturePaths) {
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}
$captureArguments = @("--path", ".", "--scene", "res://tests/capture_render.tscn", "--audio-driver", "Dummy", "--log-file", "diagnostics/capture_render_real.log")
$captureProcess = Start-Process -FilePath $godotConsole -ArgumentList $captureArguments -WorkingDirectory $experimentRoot -WindowStyle Hidden -Wait -PassThru
if ($captureProcess.ExitCode -ne 0) { throw "Real-render capture exited nonzero" }
foreach ($path in $capturePaths[0..1]) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing fresh capture: $path" }
}
python (Join-Path $PSScriptRoot "verify_render_capture.py")
if ($LASTEXITCODE -ne 0) { throw "Render verification failed" }

Write-Output "VALIDATION_OK: Moonroot Hollow passed 7 normal checks, 4 causal mutations, raster-only policy, and real-render verification."

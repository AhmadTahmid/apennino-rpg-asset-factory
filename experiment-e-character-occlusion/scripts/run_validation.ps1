param()

$ErrorActionPreference = "Stop"
$experimentRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$diagnostics = Join-Path $experimentRoot "diagnostics"
$godotConsole = (Get-Command godot_console -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $diagnostics | Out-Null

$requiredTests = @(
    "asset_integrity",
    "atlas_integrity",
    "direction_mapping",
    "temporal_animation",
    "foreground_asset_contract",
    "foreground_transform_contract",
    "occlusion_state_contract",
    "collision_probe_contract",
    "fountain_blocking",
    "lower_court_outbound",
    "lower_court_return",
    "outer_boundary"
)

$sourcePaths = [ordered]@{
    scene_art = Join-Path $experimentRoot "assets\control_01.png"
    atlas = Join-Path $experimentRoot "assets\traveler_walk_sheet.png"
    mask = Join-Path $experimentRoot "assets\southwest_planter_mask.png"
    foreground = Join-Path $experimentRoot "assets\southwest_planter_foreground.png"
    geometry = Join-Path $experimentRoot "data\node_001_geometry.json"
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
        "freeze_animation" {
            $result = Get-TestResult -Payload $Payload -Name "temporal_animation"
            if ($result.evidence.complete_cycle) { throw "Frozen animation unexpectedly completed a frame cycle" }
            if (@($result.evidence.distinct_columns).Count -ge 3) { throw "Frozen animation exposed all three frame columns" }
        }
        "swap_left_right_rows" {
            $result = Get-TestResult -Payload $Payload -Name "direction_mapping"
            $left = $result.evidence.cases | Where-Object { $_.direction -eq "left" }
            $right = $result.evidence.cases | Where-Object { $_.direction -eq "right" }
            if ($left.observed_row -ne 2 -or $right.observed_row -ne 1) {
                throw "Row-swap mutation failed for an unexpected mapping: left=$($left.observed_row), right=$($right.observed_row)"
            }
        }
        "occluder_below_player" {
            $result = Get-TestResult -Payload $Payload -Name "occlusion_state_contract"
            if ([int]$result.evidence.foreground_z_index -ge [int]$result.evidence.player_z_index) {
                throw "Occluder-below mutation did not put the foreground below the player"
            }
        }
        "occluder_shift_x20" {
            $result = Get-TestResult -Payload $Payload -Name "foreground_transform_contract"
            $expectedX = [double]$result.evidence.expected_position[0]
            $actualX = [double]$result.evidence.actual_position[0]
            if ([math]::Abs(($expectedX + 20.0) - $actualX) -gt 0.01) {
                throw "Occluder shift was not the declared +20 px: expected $($expectedX + 20.0), got $actualX"
            }
        }
        "full_rectangle_mask" {
            $result = Get-TestResult -Payload $Payload -Name "foreground_asset_contract"
            if ([int]$result.evidence.runtime_alpha_pixel_count -le [int]$result.evidence.expected_alpha_pixel_count) {
                throw "Full-rectangle mutation did not broaden the runtime alpha mask"
            }
        }
        "shift_fountain" {
            $result = Get-TestResult -Payload $Payload -Name "fountain_blocking"
            if ($result.evidence.movement.outcome -ne "REACHED") {
                throw "Shifted fountain was not detected through an incorrectly reachable art-space center"
            }
        }
        "corridor_blocker" {
            $result = Get-TestResult -Payload $Payload -Name "lower_court_outbound"
            $blocked = @($result.evidence.legs | Where-Object { $_.outcome -eq "BLOCKED" -and $_.collider_name -eq "MutationCorridorBlocker" })
            if ($blocked.Count -lt 1) {
                throw "Corridor mutation did not fail on MutationCorridorBlocker"
            }
        }
        default { throw "No causal assertion is defined for mutation: $Mutation" }
    }
}

python (Join-Path $PSScriptRoot "prepare_assets.py")
if ($LASTEXITCODE -ne 0) { throw "Deterministic asset preparation failed" }

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
if ($LASTEXITCODE -ne 0) { throw "Normal Experiment E suite exited nonzero" }
if (-not (Test-Path -LiteralPath $normalResult)) { throw "Normal suite produced no fresh result file" }
$normalPayload = Get-Content -LiteralPath $normalResult -Raw | ConvertFrom-Json
if (-not $normalPayload.passed) { throw "Normal Experiment E assertions failed" }
Assert-TestInventory -Payload $normalPayload
Assert-ExactFailures -Payload $normalPayload -ExpectedFailures @()
Assert-SourceHashes -Payload $normalPayload

$expectedMutationFailures = [ordered]@{
    freeze_animation = @("temporal_animation")
    swap_left_right_rows = @("direction_mapping")
    occluder_below_player = @("occlusion_state_contract")
    occluder_shift_x20 = @("foreground_transform_contract", "occlusion_state_contract")
    full_rectangle_mask = @("foreground_asset_contract", "occlusion_state_contract")
    shift_fountain = @("collision_probe_contract", "fountain_blocking", "lower_court_outbound", "lower_court_return")
    corridor_blocker = @("collision_probe_contract", "lower_court_outbound", "lower_court_return")
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
    (Join-Path $diagnostics "runtime_occlusion_capture.png"),
    (Join-Path $diagnostics "runtime_occlusion_capture_player_above.png"),
    (Join-Path $diagnostics "runtime_occlusion_baseline.png"),
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
if ($captureProcess.ExitCode -ne 0) { throw "Real-renderer occlusion capture exited nonzero" }
foreach ($path in $renderCapturePaths[0..2]) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Real renderer produced no fresh capture: $path" }
}
python (Join-Path $PSScriptRoot "verify_render_captures.py")
if ($LASTEXITCODE -ne 0) { throw "Real-renderer occlusion evidence failed independent pixel verification" }
if (-not (Test-Path -LiteralPath $renderCapturePaths[3])) { throw "Render verifier produced no fresh report" }
$renderPayload = Get-Content -LiteralPath $renderCapturePaths[3] -Raw | ConvertFrom-Json
if (-not $renderPayload.passed) { throw "Render verification payload is not passing" }

Write-Output "VALIDATION_OK: normal Experiment E suite passed and all seven mutations failed only for their declared causes."

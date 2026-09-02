$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$diagnostics = Join-Path $projectRoot "diagnostics"
$godotCommand = Get-Command godot_console.exe -ErrorAction Stop
$godot = $godotCommand.Source

New-Item -ItemType Directory -Force -Path $diagnostics | Out-Null
Push-Location $projectRoot
try {
    & python scripts\preflight.py *>&1 | Tee-Object -FilePath diagnostics\preflight.log
    if ($LASTEXITCODE -ne 0) { throw "Preflight failed" }

    & $godot --headless --path . --editor --quit *>&1 | Tee-Object -FilePath diagnostics\godot_import.log
    if ($LASTEXITCODE -ne 0) { throw "Godot import failed" }

    & $godot --headless --path . --scene res://tests/test_vertical_slice.tscn *>&1 | Tee-Object -FilePath diagnostics\godot_test.log
    if ($LASTEXITCODE -ne 0) { throw "Normal runtime suite failed" }

    $mutations = @("portal_bypass", "missing_star_seed", "missing_completion", "wrong_forest_spawn", "forest_corridor_blocker", "save_state_drift")
    foreach ($mutation in $mutations) {
        & $godot --headless --path . --scene res://tests/test_vertical_slice.tscn -- --mutation=$mutation *>&1 | Tee-Object -FilePath ("diagnostics\godot_test_{0}.log" -f $mutation)
        if ($LASTEXITCODE -eq 0) { throw "Mutation unexpectedly passed: $mutation" }
    }

    & python scripts\verify_mutations.py *>&1 | Tee-Object -FilePath diagnostics\mutation_verification.log
    if ($LASTEXITCODE -ne 0) { throw "Mutation verification failed" }

    foreach ($location in @("town", "forest", "sanctuary")) {
        foreach ($mode in @("baseline", "player")) {
            & $godot --path . --scene res://tests/capture_render.tscn -- --location=$location --mode=$mode *>&1 | Tee-Object -FilePath ("diagnostics\capture_{0}_{1}.log" -f $location, $mode)
            if ($LASTEXITCODE -ne 0) { throw "Real render capture failed: $location/$mode" }
        }
    }

    & python scripts\verify_render_captures.py *>&1 | Tee-Object -FilePath diagnostics\render_capture_verification.log
    if ($LASTEXITCODE -ne 0) { throw "Real render verification failed" }

    Write-Host "Experiment H validation passed: 12 contracts, 6 mutations, 3 exact real-render baselines."
}
finally {
    Pop-Location
}

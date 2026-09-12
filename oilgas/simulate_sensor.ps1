$equipment = @(
    "Crude Oil Pump P-101",
    "Gas Compressor C-101",
    "Separator V-101",
    "Heat Exchanger E-101"
)

$counter = 0

while ($true) {

    $counter++

    $id = Get-Random -InputObject $equipment

    # Normal values
    $temperature = (Get-Random -Minimum 700 -Maximum 951) / 10.0
    $pressure = (Get-Random -Minimum 1300 -Maximum 1601) / 10.0
    $flow = (Get-Random -Minimum 2800 -Maximum 3501) / 10.0
    $vibration = (Get-Random -Minimum 20 -Maximum 71) / 10.0

    # Every 5th reading create an abnormal condition
    if ($counter % 5 -eq 0) {

        $alertType = Get-Random -Minimum 1 -Maximum 3

        if ($alertType -eq 1) {
            # High temperature
            $temperature = (Get-Random -Minimum 960 -Maximum 1101) / 10.0
        }
        else {
            # High vibration
            $vibration = (Get-Random -Minimum 80 -Maximum 121) / 10.0
        }
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $record = "$id,$temperature,$pressure,$flow,$vibration,$timestamp"

    Add-Content `
        -Path "C:\LAB_CODE\3rdsem\oilgas\sensor_stream.txt" `
        -Value $record

    Write-Host $record

    Start-Sleep -Seconds 2
}
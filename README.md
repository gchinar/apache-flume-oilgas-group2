# Apache Flume: Oil & Gas Equipment Monitoring

Contributors:
<img width="934" height="406" alt="image" src="https://github.com/user-attachments/assets/6ee249a3-caed-4c4b-84b5-08ad820788b2" />


Group 2, Stream Processing and Analytics assignment.

A PowerShell simulator generates CSV sensor readings for four assets. Apache Flume reads the source file with an Exec Source, buffers events in a Memory Channel, and writes local files through a File Roll Sink. A Python Streamlit dashboard displays the latest readings and threshold alerts.

## Files

- `oilgas/simulate_sensor.ps1`: simulator, one event approximately every two seconds.
- `oilgas/app/dashboard.py`: parser, latest-state selection, threshold checks and dashboard.
- `apache-flume-1.11.0-bin/conf/oilgas.conf`: agent `a1` configuration.
- `oilgas/sensor_stream.txt` and `oilgas/output/`: supplied historical simulation data from 4 September 2026.
- `requirements.txt`: Python dependencies.

The Apache Flume binary distribution is a separate dependency. Download Apache Flume 1.11.0 from the [Apache archive](https://archive.apache.org/dist/flume/1.11.0/). Preserve the vendor's license and notice files with its installation. This repository contains the assignment configuration, not the Flume runtime JARs.

## Windows setup

Install Java compatible with Apache Flume 1.11.0, Python, and PowerShell. Use the [Flume user guide](https://flume.apache.org/FlumeUserGuide.html) for runtime prerequisites.

Place this project's `oilgas` folder at `C:\LAB_CODE\3rdsem\oilgas`. Extract the Flume binary distribution so its `lib` folder is at `C:\LAB_CODE\3rdsem\apache-flume-1.11.0-bin\lib`, then copy this repository's `conf\oilgas.conf` into that installation.

If choosing a different location, update the paths together in `oilgas.conf`, `simulate_sensor.ps1`, and `dashboard.py`.

Install Python dependencies from this repository's root:

```powershell
python -m pip install -r requirements.txt
```


### Terminal 1: Flume agent

```powershell
cd C:\LAB_CODE\3rdsem\apache-flume-1.11.0-bin
java -cp "lib\*" org.apache.flume.node.Application -n a1 -f conf\oilgas.conf
```

### Terminal 2: simulator

```powershell
cd C:\LAB_CODE\3rdsem\oilgas
powershell -ExecutionPolicy Bypass -File .\simulate_sensor.ps1
```

### Terminal 3: dashboard

```powershell
cd C:\LAB_CODE\3rdsem\oilgas\app
python -m streamlit run dashboard.py
```

Open the local address printed by Streamlit. Stop each process with Ctrl+C.

## Event format and behavior

CSV fields: `Equipment,Temperature,Pressure,Flow,Vibration,Timestamp`.

| Parameter | Archive normal range |
|---|---|
| Temperature | 70–95 °C |
| Pressure | 130–160 bar |
| Flow | 280–350 m³/h |
| Vibration | 2–7 mm/s |

Every fifth generated event injects a high temperature or high vibration. Flume's memory capacity is 1000 events, transaction capacity is 100, and file roll interval is 30 seconds. The dashboard rescans sink files after a two-second sleep and selects the latest timestamp per equipment.

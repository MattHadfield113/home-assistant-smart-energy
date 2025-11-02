# Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Home Assistant Add-on                        │
│                  Smart Energy Controller v1.0                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Web Frontend                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │ Devices  │  │ Heating  │  │Automation│       │
│  │  Tab     │  │   Tab    │  │   Tab    │  │   Tab    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │             │              │
│       └─────────────┴──────────────┴─────────────┘              │
│                          │                                       │
│                    JavaScript (app.js)                           │
│                     Auto-refresh (30s)                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼─────────────────────────────────────┐
│                      Flask Web Server                            │
│                       (main.py)                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   REST API Endpoints                      │   │
│  │  • GET  /api/devices                                     │   │
│  │  • GET  /api/devices/managed                             │   │
│  │  • POST /api/devices/managed                             │   │
│  │  • DEL  /api/devices/managed/{id}                        │   │
│  │  • GET  /api/energy/status                               │   │
│  │  • GET  /api/heating/comparison                          │   │
│  │  • GET  /api/automation/status                           │   │
│  │  • POST /api/automation/toggle                           │   │
│  │  • GET  /api/config                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────┬────────────────────────────────┬─────────────────────┘
            │                                │
            │                                │
┌───────────▼────────────────┐   ┌───────────▼─────────────────────┐
│   Energy Manager           │   │   Home Assistant Client         │
│   (energy_manager.py)      │   │   (ha_client.py)                │
│                            │   │                                 │
│  • Device Management       │   │  • API Communication            │
│  • Automation Logic        │◄──┤  • Device Control               │
│  • COP/EER Calculation     │   │  • State Retrieval              │
│  • Cost Comparison         │   │  • Sensor Reading               │
│  • Priority Control        │   │                                 │
│  • Session Detection       │   └─────────────┬───────────────────┘
│                            │                 │
│  ┌──────────────────────┐  │                 │
│  │ Automation Thread    │  │                 │ HTTP/REST
│  │ (30s loop)          │  │                 │
│  │                     │  │                 │
│  │ 1. Check Sessions   │  │                 │
│  │ 2. Check Solar      │  │                 │
│  │ 3. Check Costs      │  │                 │
│  │ 4. Control Devices  │  │                 │
│  └──────────────────────┘  │                 │
│                            │                 │
│  ┌──────────────────────┐  │                 │
│  │ Persistent Storage   │  │                 │
│  │ /data/               │  │                 │
│  │ managed_devices.json │  │                 │
│  │ options.json         │  │                 │
│  └──────────────────────┘  │                 │
└────────────────────────────┘                 │
                                               │
┌──────────────────────────────────────────────▼─────────────────┐
│                    Home Assistant Core                          │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │  Switches  │  │   Lights   │  │  Buttons   │              │
│  └────────────┘  └────────────┘  └────────────┘              │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │Solar Sensor│  │Cost Sensors│  │Session     │              │
│  │            │  │            │  │Sensors     │              │
│  └────────────┘  └────────────┘  └────────────┘              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Decision Flow                               │
│                                                                  │
│  Start                                                           │
│    │                                                             │
│    ▼                                                             │
│  Automation Enabled? ────No───► Skip                            │
│    │                                                             │
│    │Yes                                                          │
│    ▼                                                             │
│  Saving Session? ────Yes───► Turn Off Priority >3               │
│    │                                                             │
│    │No                                                           │
│    ▼                                                             │
│  Free Session? ──────Yes───► Turn On All Devices                │
│    │                                                             │
│    │No                                                           │
│    ▼                                                             │
│  Solar >1kW? ────────Yes───► Turn On Devices                    │
│    │                                                             │
│    │No                                                           │
│    ▼                                                             │
│  Cost >0.30? ────────Yes───► Turn Off Priority >5               │
│    │                                                             │
│    │No                                                           │
│    ▼                                                             │
│  Wait 30s                                                        │
│    │                                                             │
│    └──────► Loop                                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Data Flow                                     │
│                                                                  │
│  User ──► Web UI ──► API ──► Energy Manager ──► HA Client ──►  │
│                                     │                            │
│                                     ▼                            │
│                               Persistent Storage                 │
│                                     │                            │
│  User ◄── Web UI ◄── API ◄── Energy Manager ◄── HA Client ◄──  │
└─────────────────────────────────────────────────────────────────┘

Key Technologies:
├── Frontend: HTML5, CSS3, Vanilla JavaScript
├── Backend: Python 3, Flask, Threading
├── Storage: JSON files in /data/
├── Container: Docker (Alpine Linux)
└── Testing: unittest, Mock objects
```

## Component Interactions

### User Actions
1. User opens web interface
2. Browser loads HTML/CSS/JS
3. JavaScript makes API calls
4. Flask returns JSON responses
5. UI updates with current data

### Automation Loop
1. Thread runs every 30 seconds
2. Energy Manager checks conditions
3. Decisions made based on priority
4. HA Client executes device commands
5. State changes persisted to disk

### Device Management
1. User adds device via UI
2. API receives POST request
3. Energy Manager stores configuration
4. Device added to automation
5. Changes saved to JSON file

### Cost Comparison
1. API request received
2. Energy Manager reads sensor values
3. COP/EER calculations performed
4. Comparison computed
5. Recommendation returned

## Security Layers

```
┌─────────────────────────────────────┐
│   Generic Error Messages (User)    │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Detailed Logs (Administrator)     │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Exception Handling (Application)  │
└─────────────────────────────────────┘
```

## Deployment Architecture

```
Home Assistant Host
│
├── Add-on Container (Docker)
│   ├── Alpine Linux
│   ├── Python 3
│   ├── Flask Server (Port 8099)
│   └── /data (Persistent Volume)
│
├── Home Assistant Core
│   └── REST API
│
└── Ingress Proxy (Optional)
    └── Integrated UI Access
```

// API helper functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API call error:', error);
        return { success: false, error: error.message };
    }
}

// Tab management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load data for the tab
    if (tabName === 'dashboard') {
        loadDashboard();
    } else if (tabName === 'devices') {
        loadManagedDevices();
    } else if (tabName === 'scheduling') {
        // Scheduling tab - data loaded on demand via buttons
    } else if (tabName === 'heating') {
        loadHeatingComparison();
    } else if (tabName === 'automation') {
        loadAutomationStatus();
    }
}

// Dashboard functions
async function loadDashboard() {
    const result = await apiCall('/api/energy/status');
    if (result.success) {
        const status = result.status;
        document.getElementById('solar-generation').textContent = status.solar_generation.toFixed(0);
        document.getElementById('electricity-cost').textContent = status.electricity_cost.toFixed(4);
        document.getElementById('gas-cost').textContent = status.gas_cost.toFixed(4);
        document.getElementById('free-session').textContent = status.is_free_session ? 'Active' : 'Inactive';
        document.getElementById('saving-session').textContent = status.is_saving_session ? 'Active' : 'Inactive';
        document.getElementById('managed-count').textContent = status.managed_device_count;
        
        // Show battery info if available
        if (status.battery_level !== undefined) {
            const batteryCard = document.getElementById('battery-card');
            batteryCard.style.display = 'block';
            document.getElementById('battery-level').textContent = status.battery_level.toFixed(0);
            const batteryState = document.getElementById('battery-state');
            if (status.battery_state) {
                batteryState.textContent = `% (${status.battery_state})`;
            } else {
                batteryState.textContent = '%';
            }
        }
    }
}

// Device management functions
async function loadManagedDevices() {
    const result = await apiCall('/api/devices/managed');
    const container = document.getElementById('managed-devices-list');
    
    if (result.success && result.devices.length > 0) {
        container.innerHTML = result.devices.map(device => `
            <div class="device-card managed">
                <div class="device-info">
                    <div class="device-name">${device.name}</div>
                    <div class="device-id">${device.entity_id}</div>
                    <div class="device-meta">
                        <span class="badge">Priority: ${device.priority}</span>
                        <span class="badge">Power: ${device.power_consumption}W</span>
                        <span class="badge state-${device.state}">${device.state}</span>
                    </div>
                </div>
                <button class="btn btn-danger" onclick="removeDevice('${device.entity_id}')">Remove</button>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p class="info">No managed devices. Add devices from the available list below.</p>';
    }
}

async function loadAvailableDevices() {
    const result = await apiCall('/api/devices');
    const container = document.getElementById('available-devices-list');
    
    if (result.success && result.devices.length > 0) {
        container.innerHTML = result.devices.map(device => `
            <div class="device-card available">
                <div class="device-info">
                    <div class="device-name">${device.name}</div>
                    <div class="device-id">${device.entity_id}</div>
                    <div class="device-meta">
                        <span class="badge">${device.domain}</span>
                        <span class="badge state-${device.state}">${device.state}</span>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="showAddDeviceDialog('${device.entity_id}', '${device.name}')">Add</button>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p class="info">No devices available</p>';
    }
}

function showAddDeviceDialog(entityId, name) {
    const priority = prompt(`Add "${name}" to energy management.\n\nEnter priority (1-10, lower = higher priority):`, '5');
    if (priority === null) return;
    
    const power = prompt(`Enter estimated power consumption (Watts):`, '100');
    if (power === null) return;
    
    addDevice(entityId, parseInt(priority), parseFloat(power));
}

async function addDevice(entityId, priority, powerConsumption) {
    const result = await apiCall('/api/devices/managed', 'POST', {
        entity_id: entityId,
        priority: priority,
        power_consumption: powerConsumption
    });
    
    if (result.success) {
        alert('Device added successfully!');
        loadManagedDevices();
        loadDashboard();
    } else {
        alert('Error adding device: ' + result.error);
    }
}

async function removeDevice(entityId) {
    if (!confirm('Remove this device from energy management?')) return;
    
    const result = await apiCall(`/api/devices/managed/${entityId}`, 'DELETE');
    
    if (result.success) {
        alert('Device removed successfully!');
        loadManagedDevices();
        loadDashboard();
    } else {
        alert('Error removing device: ' + result.error);
    }
}

// Heating comparison functions
async function loadHeatingComparison() {
    const result = await apiCall('/api/heating/comparison');
    
    if (result.success) {
        const comp = result.comparison;
        document.getElementById('heat-pump-cost').textContent = comp.heat_pump_cost_per_kwh.toFixed(4);
        document.getElementById('heat-pump-cop').textContent = comp.cop.toFixed(2);
        document.getElementById('gas-heating-cost').textContent = comp.gas_cost_per_kwh.toFixed(4);
        
        const recommendation = document.getElementById('heating-recommendation');
        if (comp.recommended === 'heat_pump') {
            recommendation.innerHTML = `
                <strong>✅ Recommendation: Heat Pump</strong><br>
                Heat pump is ${Math.abs(comp.savings_percentage).toFixed(1)}% cheaper than gas heating
            `;
            recommendation.className = 'recommendation success';
        } else {
            recommendation.innerHTML = `
                <strong>⚠️ Recommendation: Gas Heating</strong><br>
                Gas heating is ${Math.abs(comp.savings_percentage).toFixed(1)}% cheaper than heat pump
            `;
            recommendation.className = 'recommendation warning';
        }
    }
}

// Automation functions
async function loadAutomationStatus() {
    const result = await apiCall('/api/automation/status');
    
    if (result.success) {
        updateAutomationButton(result.status.enabled);
    }
}

async function toggleAutomation() {
    const currentStatus = document.getElementById('automation-toggle').classList.contains('active');
    const newStatus = !currentStatus;
    
    const result = await apiCall('/api/automation/toggle', 'POST', {
        enabled: newStatus
    });
    
    if (result.success) {
        updateAutomationButton(newStatus);
    } else {
        alert('Error toggling automation: ' + result.error);
    }
}

function updateAutomationButton(enabled) {
    const button = document.getElementById('automation-toggle');
    const status = document.getElementById('automation-status');
    
    if (enabled) {
        button.classList.add('active');
        status.textContent = '✓ Enabled';
    } else {
        button.classList.remove('active');
        status.textContent = '✗ Disabled';
    }
}

// Scheduling and forecast functions
async function loadSolarForecast() {
    const result = await apiCall('/api/forecast/solar');
    const container = document.getElementById('solar-forecast-list');
    
    if (result.success && result.forecast && result.forecast.length > 0) {
        container.innerHTML = '<h4>Solar Generation Forecast</h4>';
        result.forecast.slice(0, 24).forEach(item => {
            const time = new Date(item.timestamp).toLocaleString();
            container.innerHTML += `
                <div class="forecast-item">
                    <span class="forecast-time">${time}</span>
                    <span class="forecast-value">${item.power}W</span>
                </div>
            `;
        });
    } else {
        container.innerHTML = '<p class="info">No solar forecast data available. Configure solar_forecast_sensor in settings.</p>';
    }
}

async function loadCostForecast() {
    const result = await apiCall('/api/forecast/cost');
    const container = document.getElementById('cost-forecast-list');
    
    if (result.success && result.forecast && result.forecast.length > 0) {
        container.innerHTML = '<h4>Energy Cost Forecast</h4>';
        result.forecast.slice(0, 24).forEach(item => {
            const time = new Date(item.timestamp).toLocaleString();
            const costClass = item.cost_per_kwh < 0.15 ? 'cost-low' : item.cost_per_kwh > 0.30 ? 'cost-high' : 'cost-medium';
            container.innerHTML += `
                <div class="forecast-item ${costClass}">
                    <span class="forecast-time">${time}</span>
                    <span class="forecast-value">${item.cost_per_kwh.toFixed(4)}/kWh</span>
                </div>
            `;
        });
    } else {
        container.innerHTML = '<p class="info">No cost forecast data available. Configure electricity_forecast_sensor in settings.</p>';
    }
}

async function showDeviceScheduleDialog(entityId, deviceName) {
    const scheduleHTML = `
        <div class="modal">
            <div class="modal-content">
                <h3>Configure Schedule for ${deviceName}</h3>
                <form id="schedule-form">
                    <div class="form-group">
                        <label>Start Time:</label>
                        <input type="time" id="schedule-start" value="08:00">
                    </div>
                    <div class="form-group">
                        <label>End Time:</label>
                        <input type="time" id="schedule-end" value="22:00">
                    </div>
                    <div class="form-group">
                        <label>Active Days:</label>
                        <div class="day-selector">
                            <label><input type="checkbox" value="0" checked> Mon</label>
                            <label><input type="checkbox" value="1" checked> Tue</label>
                            <label><input type="checkbox" value="2" checked> Wed</label>
                            <label><input type="checkbox" value="3" checked> Thu</label>
                            <label><input type="checkbox" value="4" checked> Fri</label>
                            <label><input type="checkbox" value="5"> Sat</label>
                            <label><input type="checkbox" value="6"> Sun</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="allow-control" checked> Allow automatic control</label>
                    </div>
                    <div class="form-group">
                        <label>Required Run Duration (minutes):</label>
                        <input type="number" id="run-duration" value="0" min="0">
                    </div>
                    <div class="form-group">
                        <label>Auto-start Automation/Script:</label>
                        <input type="text" id="auto-start" placeholder="automation.start_device or script.device_start">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-primary" onclick="saveDeviceSchedule('${entityId}')">Save</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', scheduleHTML);
}

async function saveDeviceSchedule(entityId) {
    const start = document.getElementById('schedule-start').value;
    const end = document.getElementById('schedule-end').value;
    const days = Array.from(document.querySelectorAll('.day-selector input:checked')).map(cb => parseInt(cb.value));
    const allowControl = document.getElementById('allow-control').checked;
    const runDuration = parseInt(document.getElementById('run-duration').value);
    const autoStart = document.getElementById('auto-start').value;
    
    const data = {
        schedule: { start, end, days },
        allow_direct_control: allowControl,
        required_run_duration: runDuration,
        auto_start_automation: autoStart || null
    };
    
    const result = await apiCall(`/api/devices/managed/${entityId}`, 'PUT', data);
    
    if (result.success) {
        alert('Schedule saved successfully!');
        closeModal();
        loadManagedDevices();
    } else {
        alert('Error saving schedule: ' + result.error);
    }
}

function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

async function getDeviceOptimalSchedule(entityId, deviceName) {
    const result = await apiCall(`/api/devices/schedule/${entityId}`);
    
    if (result.success && result.schedule) {
        const schedule = result.schedule;
        let html = `<div class="optimal-schedule"><h4>Optimal Schedule for ${deviceName}</h4>`;
        
        if (schedule.optimal_solar_slots && schedule.optimal_solar_slots.length > 0) {
            html += '<h5>Best Solar Generation Slots:</h5><div class="slot-list">';
            schedule.optimal_solar_slots.slice(0, 5).forEach(slot => {
                const time = new Date(slot.start_time).toLocaleString();
                html += `
                    <div class="slot-item">
                        <span>${time}</span>
                        <span>${slot.duration_minutes} min</span>
                        <span>Avg: ${slot.avg_solar_power.toFixed(0)}W</span>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        if (schedule.cheapest_cost_slots && schedule.cheapest_cost_slots.length > 0) {
            html += '<h5>Cheapest Cost Slots:</h5><div class="slot-list">';
            schedule.cheapest_cost_slots.slice(0, 5).forEach(slot => {
                const time = new Date(slot.start_time).toLocaleString();
                html += `
                    <div class="slot-item">
                        <span>${time}</span>
                        <span>${slot.duration_minutes} min</span>
                        <span>Avg: ${slot.avg_cost_per_kwh.toFixed(4)}/kWh</span>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        html += '</div>';
        
        // Display in a modal or alert
        alert(html.replace(/<[^>]*>/g, '\n'));
    } else {
        alert('No optimal schedule available for this device');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadManagedDevices();
    
    // Auto-refresh dashboard every 30 seconds
    setInterval(() => {
        if (document.querySelector('#dashboard.active')) {
            loadDashboard();
        }
    }, 30000);
});

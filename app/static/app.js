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

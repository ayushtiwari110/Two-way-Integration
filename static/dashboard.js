// Global chart instance
let syncChart = null;

document.addEventListener('DOMContentLoaded', function() {
    // Load dashboard data on page load
    loadDashboardData();
    
    // Set up refresh button
    const refreshButton = document.getElementById('refreshDashboard');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            loadDashboardData();
        });
    }
});

function loadDashboardData() {
    console.log("Loading dashboard data...");
    
    // Simple fetch with no caching issues
    fetch('/api/customers')
        .then(response => {
            console.log("Customers API response received");
            return response.json();
        })
        .then(customers => {
            console.log(`Found ${customers.length} customers`);
            
            // Now fetch integration status for each customer
            return Promise.all(customers.map(customer => {
                return fetch(`/api/customers/${customer.id}/integration-status`)
                    .then(response => response.json())
                    .then(status => {
                        return {
                            ...customer,
                            has_integration: status.has_integration
                        };
                    });
            }));
        })
        .then(customersWithStatus => {
            console.log("Processing customers with status:", customersWithStatus);
            
            // Update UI with retrieved data
            updateDashboardUI(customersWithStatus);
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
        });
}

function updateDashboardUI(customers) {
    // Update all UI elements
    updateStatistics(customers);
    updateRecentList(customers);
    updateSyncChart(customers);
    
    console.log("Dashboard UI updated successfully");
}

function updateSyncChart(customers) {
    const synced = customers.filter(c => c.has_integration).length;
    const notSynced = customers.length - synced;
    
    const ctx = document.getElementById('syncChart').getContext('2d');
    
    // Properly destroy existing chart
    if (syncChart) {
        syncChart.destroy();
    }
    
    // Create new chart
    syncChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Synced with Stripe', 'Not Synced'],
            datasets: [{
                data: [synced, notSynced],
                backgroundColor: ['#28a745', '#ffc107']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    console.log(`Chart updated - Synced: ${synced}, Not synced: ${notSynced}`);
}

function updateRecentList(customers) {
    const recentList = document.getElementById('recentSyncs');
    
    // Clear existing content
    recentList.innerHTML = '';
    
    // Sort customers by ID (most recent first) since we don't have updated_at in the response
    const recentCustomers = [...customers].sort((a, b) => b.id - a.id).slice(0, 5);
    
    if (recentCustomers.length === 0) {
        const li = document.createElement('li');
        li.className = 'list-group-item text-center text-muted';
        li.textContent = 'No customers found';
        recentList.appendChild(li);
        return;
    }
    
    recentCustomers.forEach(customer => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        const nameSpan = document.createElement('span');
        nameSpan.innerHTML = `<strong>${customer.name}</strong><br><small>${customer.email}</small>`;
        
        const badge = document.createElement('span');
        badge.className = `badge ${customer.has_integration ? 'bg-success' : 'bg-warning'}`;
        badge.textContent = customer.has_integration ? 'Synced' : 'Not synced';
        
        li.appendChild(nameSpan);
        li.appendChild(badge);
        recentList.appendChild(li);
    });
    
    console.log("Recent list updated with", recentCustomers.length, "customers");
}

function updateStatistics(customers) {
    const totalCustomers = customers.length;
    const syncedCustomers = customers.filter(c => c.has_integration).length;
    const pendingCustomers = totalCustomers - syncedCustomers;
    
    document.getElementById('totalCustomers').textContent = totalCustomers;
    document.getElementById('syncedCustomers').textContent = syncedCustomers;
    document.getElementById('pendingCustomers').textContent = pendingCustomers;
    
    console.log(`Statistics updated - Total: ${totalCustomers}, Synced: ${syncedCustomers}, Pending: ${pendingCustomers}`);
}
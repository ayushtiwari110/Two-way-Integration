document.addEventListener("DOMContentLoaded", function () {
    // Load all integrations
    loadIntegrations();
  
    // Set up refresh button
    const refreshButton = document.getElementById("refreshButton");
    if (refreshButton) {
      refreshButton.addEventListener("click", function () {
        loadIntegrations();
      });
    }
  });
  
  function loadIntegrations() {
    // Add a timestamp to prevent caching
    const timestamp = new Date().getTime();
  
    // Fetch all integrations
    fetch(`/api/integrations?t=${timestamp}`)
      .then((response) => response.json())
      .then((integrations) => {
        renderIntegrationsTable(integrations);
      })
      .catch((error) => {
        console.error("Error loading integrations:", error);
      });
  }
  
  function renderIntegrationsTable(integrations) {
    const tbody = document.getElementById("integrations-table-body");
    tbody.innerHTML = ""; // Clear existing rows
  
    if (integrations.length === 0) {
      const row = document.createElement("tr");
      row.innerHTML = '<td colspan="4" class="text-center">No integrations found</td>';
      tbody.appendChild(row);
      return;
    }
  
    integrations.forEach((integration) => {
      const row = document.createElement("tr");
  
      // Changed from integration.catalog_item_id to display the customer ID correctly
      row.innerHTML = `
          <td>${integration.catalog_item_id}</td>
          <td>
              <strong>${integration.customer_name || "Unknown"}</strong><br>
              <small>${integration.customer_email || "No email"}</small>
          </td>
          <td>
              <span class="badge bg-info">${integration.integration_type}</span>
          </td>
          <td>
              <code>${integration.integration_id}</code>
          </td>
      `;
  
      tbody.appendChild(row);
    });
  }
document.addEventListener("DOMContentLoaded", function () {
  // Load customers with integration status
  loadCustomersWithIntegrationStatus();

  // Set up event handlers for the form
  setupFormHandlers();
});

function loadCustomersWithIntegrationStatus() {
  fetch("/api/customers")
    .then((response) => response.json())
    .then((customers) => {
      // For each customer, fetch integration status
      return Promise.all(
        customers.map((customer) => {
          return fetch(`/api/customers/${customer.id}/integration-status`)
            .then((response) => response.json())
            .then((status) => {
              return { ...customer, has_integration: status.has_integration };
            });
        })
      );
    })
    .then((customersWithStatus) => {
      // Update the table with customer data
      renderCustomerTable(customersWithStatus);
    })
    .catch((error) => console.error("Error loading customers:", error));
}

function renderCustomerTable(customers) {
  const tbody = document.querySelector("table tbody");
  tbody.innerHTML = ""; // Clear existing rows

  customers.forEach((customer) => {
    const row = document.createElement("tr");

    row.innerHTML = `
            <td>${customer.id}</td>
            <td>${customer.name}</td>
            <td>${customer.email}</td>
            <td>
                <span class="badge ${customer.has_integration ? "bg-success" : "bg-warning"}">
                    ${customer.has_integration ? "Synced" : "Not synced"}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-warning" data-bs-toggle="modal" data-bs-target="#editCustomerModal" 
                    data-id="${customer.id}" data-name="${customer.name}" data-email="${customer.email}">Edit</button>
                <button class="btn btn-sm btn-danger btn-delete" data-id="${customer.id}">Delete</button>
            </td>
        `;

    tbody.appendChild(row);
  });

  // Add event listeners to the new buttons
  addButtonEventListeners();
}

function setupFormHandlers() {
  const addForm = document.getElementById("addCustomerForm");
  if (addForm) {
    addForm.addEventListener("submit", function (event) {
      event.preventDefault();

      const name = document.getElementById("customerName").value;
      const email = document.getElementById("customerEmail").value;

      fetch("/api/customers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Failed to add customer");
          }
          return response.json();
        })
        .then(() => {
          const modal = bootstrap.Modal.getInstance(document.getElementById("addCustomerModal"));
          modal.hide();

          // Clear the form fields
          document.getElementById("customerName").value = "";
          document.getElementById("customerEmail").value = "";

          // First immediate refresh to see the new customer
          loadCustomersWithIntegrationStatus();

          // Then refresh again after a delay to check integration status
          setTimeout(() => {
            loadCustomersWithIntegrationStatus();
          }, 2000); // 2-second delay to allow worker to process
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("Failed to add customer: " + error.message);
        });
    });
  }

  // Edit customer modal population
  document.querySelectorAll('[data-bs-target="#editCustomerModal"]').forEach((button) => {
    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      const name = this.getAttribute("data-name");
      const email = this.getAttribute("data-email");

      document.getElementById("editCustomerId").value = id;
      document.getElementById("editCustomerName").value = name;
      document.getElementById("editCustomerEmail").value = email;
    });
  });

  // Edit customer form submission
  const editForm = document.getElementById("editCustomerForm");
  if (editForm) {
    editForm.addEventListener("submit", function (event) {
      event.preventDefault();

      const id = document.getElementById("editCustomerId").value;
      const name = document.getElementById("editCustomerName").value;
      const email = document.getElementById("editCustomerEmail").value;

      fetch(`/api/customers/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Failed to update customer");
          }
          return response.json();
        })
        .then(() => {
          const modal = bootstrap.Modal.getInstance(document.getElementById("editCustomerModal"));
          modal.hide();
          loadCustomersWithIntegrationStatus(); // Reload the customer list
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("Failed to update customer: " + error.message);
        });
    });
  }
}

function addButtonEventListeners() {
  // Add event listeners for edit/delete buttons
  document.querySelectorAll('[data-bs-target="#editCustomerModal"]').forEach((button) => {
    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      const name = this.getAttribute("data-name");
      const email = this.getAttribute("data-email");

      document.getElementById("editCustomerId").value = id;
      document.getElementById("editCustomerName").value = name;
      document.getElementById("editCustomerEmail").value = email;
    });
  });
  // Add event listeners for delete buttons
  document.querySelectorAll('.btn-delete').forEach(button => {
    button.addEventListener('click', function() {
        const customerId = this.getAttribute('data-id');
        if (confirm('Are you sure you want to delete this customer?')) {
            fetch(`/api/customers/${customerId}`, {
                method: 'DELETE'
            })
            .then(() => loadCustomersWithIntegrationStatus())  // Reload data after deletion
            .catch(error => console.error('Error deleting customer:', error));
        }
    });
});
}

// Set up refresh button
const refreshButton = document.getElementById('refreshButton');
if (refreshButton) {
    refreshButton.addEventListener('click', function() {
        loadCustomersWithIntegrationStatus();
    });
}
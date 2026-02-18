const API_URL = '/api/products';
let products = [];
let editingId = null;

// DOM Elements
const productTableBody = document.getElementById('product-table-body');
const productForm = document.getElementById('product-form');
const modal = document.getElementById('product-modal');
const modalTitle = document.getElementById('modal-title');
const totalProductsEl = document.getElementById('total-products');
const totalValueEl = document.getElementById('total-value');
const lowStockEl = document.getElementById('low-stock');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchProducts();
});

// Fetch Products
async function fetchProducts() {
    try {
        const response = await fetch(API_URL);
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }
        products = await response.json();
        renderProducts();
        updateStats();
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

// Render Products Table
function renderProducts() {
    productTableBody.innerHTML = '';
    products.forEach(product => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.category}</td>
            <td>${product.quantity}</td>
            <td>Rs ${product.price.toFixed(2)}</td>
            <td>
                <button class="action-btn edit-btn" onclick="editProduct(${product.id})">
                    <i class="fa-solid fa-pen"></i>
                </button>
                <button class="action-btn delete-btn" onclick="deleteProduct(${product.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;
        productTableBody.appendChild(tr);
    });
}

// Update Dashboard Stats
function updateStats() {
    const totalCount = products.length;
    const totalValue = products.reduce((sum, p) => sum + (p.price * p.quantity), 0);
    const lowStock = products.filter(p => p.quantity < 5).length;

    totalProductsEl.textContent = totalCount;
    totalValueEl.textContent = `Rs ${totalValue.toFixed(2)}`;
    lowStockEl.textContent = lowStock;
}

// Add/Edit Product
productForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const productData = {
        name: document.getElementById('name').value,
        category: document.getElementById('category').value,
        quantity: parseInt(document.getElementById('quantity').value),
        price: parseFloat(document.getElementById('price').value)
    };

    try {
        if (editingId) {
            await fetch(`${API_URL}/${editingId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(productData)
            });
        } else {
            await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(productData)
            });
        }
        closeModal();
        fetchProducts();
    } catch (error) {
        console.error('Error saving product:', error);
    }
});

// Delete Product
async function deleteProduct(id) {
    if (confirm('Are you sure you want to delete this product?')) {
        try {
            await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
            fetchProducts();
        } catch (error) {
            console.error('Error deleting product:', error);
        }
    }
}

// Modal Functions
function openModal() {
    editingId = null;
    modalTitle.textContent = 'Add Product';
    productForm.reset();
    modal.style.display = 'flex';
}

function editProduct(id) {
    const product = products.find(p => p.id === id);
    if (product) {
        editingId = id;
        modalTitle.textContent = 'Edit Product';
        document.getElementById('product-id').value = product.id;
        document.getElementById('name').value = product.name;
        document.getElementById('category').value = product.category;
        document.getElementById('quantity').value = product.quantity;
        document.getElementById('price').value = product.price;
        modal.style.display = 'flex';
    }
}

function closeModal() {
    modal.style.display = 'none';
}

window.onclick = function (event) {
    if (event.target == modal) {
        closeModal();
    }
}

// Navigation
function showSection(sectionId) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.querySelectorAll('.sidebar li').forEach(li => {
        li.classList.remove('active');
    });

    document.getElementById(sectionId).classList.add('active');

    // Highlight active menu item
    if (sectionId === 'dashboard') {
        document.querySelector('.sidebar li:nth-child(1)').classList.add('active');
        updateStats(); // Refresh stats/charts when switching to dashboard
    } else {
        document.querySelector('.sidebar li:nth-child(2)').classList.add('active');
    }
}

// Analytics & History
let stockChart = null;

async function updateStats() {
    const totalCount = products.length;
    const totalValue = products.reduce((sum, p) => sum + (p.price * p.quantity), 0);
    const lowStock = products.filter(p => p.quantity < 5).length;

    totalProductsEl.textContent = totalCount;
    totalValueEl.textContent = `Rs ${totalValue.toFixed(2)}`;
    lowStockEl.textContent = lowStock;

    updateChart();
    fetchHistory();
}

function updateChart() {
    const ctx = document.getElementById('stockChart').getContext('2d');

    // Group by category
    const categories = {};
    products.forEach(p => {
        categories[p.category] = (categories[p.category] || 0) + p.quantity;
    });

    if (stockChart) {
        stockChart.destroy();
    }

    stockChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categories),
            datasets: [{
                data: Object.values(categories),
                backgroundColor: [
                    '#3b82f6', '#ef4444', '#22c55e', '#eab308', '#a855f7', '#ec4899'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right', labels: { color: '#94a3b8' } }
            }
        }
    });
}

async function fetchHistory() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();
        const list = document.getElementById('history-list');
        list.innerHTML = '';

        transactions.forEach(t => {
            const li = document.createElement('li');
            li.style.padding = '10px';
            li.style.borderBottom = '1px solid var(--border-color)';
            li.style.color = 'var(--text-secondary)';
            li.style.fontSize = '14px';

            const color = t.type === 'IN' ? 'var(--success-color)' : 'var(--danger-color)';
            const icon = t.type === 'IN' ? 'fa-arrow-down' : 'fa-arrow-up';

            li.innerHTML = `
                <span style="color: ${color}; margin-right: 10px;"><i class="fa-solid ${icon}"></i> ${t.type}</span>
                <strong>${t.product_name}</strong> - ${t.quantity} units
                <br><small>${new Date(t.timestamp).toLocaleString()}</small>
            `;
            list.appendChild(li);
        });
    } catch (error) {
        console.error('Error fetching history:', error);
    }
}

function exportCSV() {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "ID,Name,Category,Quantity,Price\n";

    products.forEach(p => {
        csvContent += `${p.id},${p.name},${p.category},${p.quantity},${p.price}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "inventory_export.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Personal Finance Tracker - Main JavaScript

// Utility Functions
const Utils = {
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Format date
    formatDate(date) {
        return new Intl.DateTimeFormat('en-US').format(new Date(date));
    },

    // Show toast notification
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        const toast = this.createToast(message, type);
        toastContainer.appendChild(toast);

        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove from DOM after hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    },

    createToast(message, type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        const colors = {
            success: 'text-success',
            error: 'text-danger',
            warning: 'text-warning',
            info: 'text-primary'
        };

        const toast = document.createElement('div');
        toast.className = 'toast fade';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-header">
                <i class="bi ${icons[type]} ${colors[type]} me-2"></i>
                <strong class="me-auto">Finance Tracker</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        return toast;
    },

    // Animate counter
    animateCounter(element, start, end, duration = 1000) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = this.formatCurrency(end);
                clearInterval(timer);
            } else {
                element.textContent = this.formatCurrency(current);
            }
        }, 16);
    }
};

// Form Handling
const FormHandler = {
    // Initialize form enhancements
    init() {
        this.addFormValidation();
        this.addLoadingStates();
        this.addDatePickers();
        this.addNumberFormatting();
    },

    addFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },

    addLoadingStates() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>Processing...';
                    submitBtn.disabled = true;

                    // Re-enable after timeout (fallback)
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 10000);
                }
            });
        });
    },

    addDatePickers() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            if (!input.value) {
                input.value = new Date().toISOString().split('T')[0];
            }
        });
    },

    addNumberFormatting() {
        const numberInputs = document.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                if (e.target.step === '0.01' && e.target.value) {
                    e.target.value = parseFloat(e.target.value).toFixed(2);
                }
            });
        });
    }
};

// Chart Utilities
const ChartUtils = {
    // Default chart options
    getDefaultOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        };
    },

    // Color schemes
    colors: {
        primary: ['#667eea', '#764ba2', '#4facfe', '#00f2fe'],
        success: ['#4facfe', '#00f2fe'],
        danger: ['#fa709a', '#fee140'],
        warning: ['#ffeaa7', '#fdcb6e'],
        info: ['#a8edea', '#fed6e3']
    },

    // Create pie chart
    createPieChart(canvas, data, options = {}) {
        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: this.colors.primary,
                    borderWidth: 0
                }]
            },
            options: {
                ...this.getDefaultOptions(),
                ...options
            }
        });
    },

    // Create bar chart
    createBarChart(canvas, data, options = {}) {
        return new Chart(canvas, {
            type: 'bar',
            data: data,
            options: {
                ...this.getDefaultOptions(),
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return Utils.formatCurrency(value);
                            }
                        }
                    }
                },
                ...options
            }
        });
    },

    // Create line chart
    createLineChart(canvas, data, options = {}) {
        return new Chart(canvas, {
            type: 'line',
            data: data,
            options: {
                ...this.getDefaultOptions(),
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return Utils.formatCurrency(value);
                            }
                        }
                    }
                },
                ...options
            }
        });
    }
};

// Navigation Enhancement
const Navigation = {
    init() {
        this.highlightActiveNav();
        this.addMobileMenuToggle();
    },

    highlightActiveNav() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    },

    addMobileMenuToggle() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');

        if (navbarToggler && navbarCollapse) {
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navbarToggler.contains(e.target) &&
                    !navbarCollapse.contains(e.target) &&
                    navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        }
    }
};

// Dashboard Enhancements
const Dashboard = {
    init() {
        this.animateStatCards();
        this.loadCharts();
        this.setupRefreshButton();
    },

    animateStatCards() {
        const statCards = document.querySelectorAll('.stat-card h3');
        statCards.forEach(card => {
            const value = parseFloat(card.textContent.replace(/[$,]/g, ''));
            if (!isNaN(value)) {
                card.textContent = '$0.00';
                Utils.animateCounter(card, 0, value, 1500);
            }
        });
    },

    loadCharts() {
        // This will be called by individual page scripts
        if (typeof loadDashboardCharts === 'function') {
            loadDashboardCharts();
        }
    },

    setupRefreshButton() {
        const refreshBtn = document.getElementById('refreshData');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                window.location.reload();
            });
        }
    }
};

// Table Enhancements
const TableUtils = {
    init() {
        this.addSortableHeaders();
        this.addRowHoverEffects();
        this.addDeleteConfirmations();
    },

    addSortableHeaders() {
        const sortableHeaders = document.querySelectorAll('th[data-sort]');
        sortableHeaders.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(header);
            });
        });
    },

    sortTable(header) {
        // Basic table sorting implementation
        const table = header.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const column = header.cellIndex;
        const isAscending = header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aVal = a.cells[column].textContent.trim();
            const bVal = b.cells[column].textContent.trim();

            if (isAscending) {
                return bVal.localeCompare(aVal, undefined, {numeric: true});
            } else {
                return aVal.localeCompare(bVal, undefined, {numeric: true});
            }
        });

        // Update header classes
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');

        // Rebuild table
        rows.forEach(row => tbody.appendChild(row));
    },

    addRowHoverEffects() {
        const tableRows = document.querySelectorAll('tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.backgroundColor = '#f8f9fa';
            });
            row.addEventListener('mouseleave', () => {
                row.style.backgroundColor = '';
            });
        });
    },

    addDeleteConfirmations() {
        const deleteButtons = document.querySelectorAll('.btn-danger[href*="delete"], .btn-danger[onclick*="delete"]');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    e.preventDefault();
                }
            });
        });
    }
};

// Modal Enhancements
const ModalUtils = {
    init() {
        this.addModalEnhancements();
    },

    addModalEnhancements() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                const firstInput = modal.querySelector('input:not([type="hidden"])');
                if (firstInput) {
                    firstInput.focus();
                }
            });
        });
    }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    FormHandler.init();
    Navigation.init();
    TableUtils.init();
    ModalUtils.init();

    // Initialize dashboard if on dashboard page
    if (document.querySelector('.stat-card')) {
        Dashboard.init();
    }

    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
});

// Export utilities for global use
window.Utils = Utils;
window.ChartUtils = ChartUtils;
window.FormHandler = FormHandler;

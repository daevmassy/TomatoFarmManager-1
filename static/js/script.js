// Tomato Farm Management System - Main JavaScript

// Calculate expected harvest date based on variety
function calculateHarvestDate() {
    const varietySelect = document.getElementById('variety');
    const plantingDateInput = document.getElementById('planting_date');
    const expectedHarvestInput = document.getElementById('expected_harvest');

    if (!varietySelect || !plantingDateInput || !expectedHarvestInput) {
        return;
    }

    const selectedOption = varietySelect.options[varietySelect.selectedIndex];
    const daysToHarvest = parseInt(selectedOption.getAttribute('data-days'));
    const plantingDate = plantingDateInput.value;

    if (daysToHarvest && plantingDate) {
        const planting = new Date(plantingDate);
        planting.setDate(planting.getDate() + daysToHarvest);

        // Format date as YYYY-MM-DD
        const year = planting.getFullYear();
        const month = String(planting.getMonth() + 1).padStart(2, '0');
        const day = String(planting.getDate()).padStart(2, '0');

        expectedHarvestInput.value = `${year}-${month}-${day}`;
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value && input.id !== 'expected_harvest') {
            input.value = today;
        }
    });

    // Auto-calculate total amount in sales form
    const quantityInput = document.getElementById('quantity');
    const priceInput = document.getElementById('price_per_unit');

    if (quantityInput && priceInput) {
        function calculateTotal() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            const total = quantity * price;
            console.log('Total calculated:', total);
        }

        quantityInput.addEventListener('input', calculateTotal);
        priceInput.addEventListener('input', calculateTotal);
    }

    // Event listeners for harvest date calculation
    const varietySelect = document.getElementById('variety');
    const plantingDateInput = document.getElementById('planting_date');

    if (varietySelect) {
        varietySelect.addEventListener('change', calculateHarvestDate);
    }
    if (plantingDateInput) {
        plantingDateInput.addEventListener('input', calculateHarvestDate);
    }
});
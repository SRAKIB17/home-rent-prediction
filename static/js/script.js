/**
 * Home Rent Prediction System - Frontend JavaScript Helper
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Preset Profiles for quick testing (Mymensingh, Bangladesh)
    const presets = {
        'charpara-family': {
            location: 'Charpara',
            property_type: 'Apartment',
            bedrooms: 3,
            bathrooms: 2,
            house_size: 1250,
            floor: 4,
            total_floors: 7,
            furnished: 'No',
            parking: 'Yes',
            balcony: 'Yes',
            age: 3
        },
        'kachijhuli-luxury': {
            location: 'Kachijhuli',
            property_type: 'Duplex',
            bedrooms: 4,
            bathrooms: 4,
            house_size: 2600,
            floor: 6,
            total_floors: 10,
            furnished: 'Yes',
            parking: 'Yes',
            balcony: 'Yes',
            age: 2
        },
        'townhall-3bhk': {
            location: 'Town Hall',
            property_type: 'Apartment',
            bedrooms: 3,
            bathrooms: 2,
            house_size: 1450,
            floor: 3,
            total_floors: 6,
            furnished: 'Yes',
            parking: 'Yes',
            balcony: 'Yes',
            age: 4
        },
        'shehora-studio': {
            location: 'Shehora',
            property_type: 'Studio',
            bedrooms: 1,
            bathrooms: 1,
            house_size: 450,
            floor: 2,
            total_floors: 5,
            furnished: 'No',
            parking: 'No',
            balcony: 'No',
            age: 1
        }
    };

    // Preset button click listener
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const key = btn.getAttribute('data-preset');
            const data = presets[key];
            if (data) {
                for (const [field, value] of Object.entries(data)) {
                    const el = document.getElementById(field);
                    if (el) {
                        el.value = value;
                        el.dispatchEvent(new Event('change'));
                    }
                }
                
                // Visual feedback
                btn.style.transform = 'scale(0.95)';
                setTimeout(() => btn.style.transform = 'none', 150);
            }
        });
    });

    // 2. Real-time floor validation
    const floorInput = document.getElementById('floor');
    const totalFloorsInput = document.getElementById('total_floors');

    function checkFloors() {
        if (floorInput && totalFloorsInput) {
            const f = parseInt(floorInput.value) || 1;
            const tf = parseInt(totalFloorsInput.value) || 1;
            if (f > tf) {
                totalFloorsInput.setCustomValidity('Total floors must be at least equal to current floor.');
            } else {
                totalFloorsInput.setCustomValidity('');
            }
        }
    }

    if (floorInput && totalFloorsInput) {
        floorInput.addEventListener('input', checkFloors);
        totalFloorsInput.addEventListener('input', checkFloors);
    }

    // 3. Form submission button loading state
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('submitBtn');

    if (form && submitBtn) {
        form.addEventListener('submit', (e) => {
            if (form.checkValidity()) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <svg class="spinner" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="animation: spin 1s linear infinite; margin-right: 8px;">
                        <line x1="12" y1="2" x2="12" y2="6"></line>
                        <line x1="12" y1="18" x2="12" y2="22"></line>
                        <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                        <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                        <line x1="2" y1="12" x2="6" y2="12"></line>
                        <line x1="18" y1="12" x2="22" y2="12"></line>
                        <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                        <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
                    </svg>
                    Predicting Rent with ML Model...
                `;
            }
        });
    }
});

// Add spin keyframe dynamically
const style = document.createElement('style');
style.innerHTML = `@keyframes spin { 100% { transform: rotate(360deg); } }`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const imagePreview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('preview-container');
    const scanBtn = document.getElementById('scan-btn');
    const registerBtn = document.getElementById('register-btn');
    const manualAddBtn = document.getElementById('manual-add-btn');
    const manualCheckBtn = document.getElementById('manual-check-btn');
    
    const registrationCard = document.getElementById('registration-card');
    const interactionCard = document.getElementById('interaction-card');
    const interactionText = document.getElementById('interaction-text');
    
    const medNameInput = document.getElementById('med-name');
    const medQuantityInput = document.getElementById('med-quantity');
    const medFrequencyInput = document.getElementById('med-frequency');
    const medTimingInput = document.getElementById('med-timing');
    const medExpiryInput = document.getElementById('med-expiry');
    const medInstructionsInput = document.getElementById('med-instructions');
    
    const medicineList = document.getElementById('medicine-list');
    const medCount = document.getElementById('med-count');
    const loader = document.getElementById('loader');
    const toastContainer = document.getElementById('toast-container');

    let selectedFile = null;

    fetchMedicines();

    // File Upload
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            previewContainer.style.display = 'block';
            scanBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    // OCR & Interaction Check
    scanBtn.addEventListener('click', async () => {
        const vitalsCard = document.getElementById('vitals-card');
        const vitalsTitle = document.getElementById('vitals-title');
        const vitalsIcon = document.getElementById('vitals-icon');
        const vitalsBody = document.getElementById('vitals-body');
        const vitalsInterpretation = document.getElementById('vitals-interpretation');

        if (!selectedFile) return;
        const formData = new FormData();
        formData.append('file', selectedFile);

        loader.style.display = 'flex';
        scanBtn.disabled = true;

        // Reset cards
        registrationCard.style.display = 'none';
        interactionCard.style.display = 'none';
        vitalsCard.style.display = 'none';

        try {
            const response = await fetch('/api/ocr', { method: 'POST', body: formData });
            const result = await response.json();

            if (result.success) {
                if (result.detected_type === 'medicine') {
                    // Medicine Logic
                    medNameInput.value = result.data['medication name'] || result.data.name || '';
                    medQuantityInput.value = result.data.number || '';
                    medExpiryInput.value = result.data.expiry || '';
                    
                    if (Array.isArray(result.data.frequency)) {
                        medFrequencyInput.value = result.data.frequency.join(', ');
                    } else {
                        medFrequencyInput.value = result.data.frequency || '';
                    }
                    
                    if (Array.isArray(result.data['time of taking'])) {
                        medTimingInput.value = result.data['time of taking'].join(', ');
                    } else {
                        medTimingInput.value = result.data['time of taking'] || '';
                    }

                    medInstructionsInput.value = result.data.instructions || '';
                    
                    registrationCard.style.display = 'block';
                    interactionText.innerHTML = result.interaction_report.replace(/\n/g, '<br>');
                    interactionCard.style.display = 'block';
                    
                    if (result.interaction_report.includes('WARNING') || result.interaction_report.includes('อันตราย')) {
                        interactionCard.style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
                        interactionCard.style.borderLeftColor = '#ef4444';
                    } else {
                        interactionCard.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
                        interactionCard.style.borderLeftColor = '#10b981';
                    }
                    registrationCard.scrollIntoView({ behavior: 'smooth' });

                } else if (result.detected_type === 'blood_pressure' || result.detected_type === 'blood_glucose') {
                    // Vitals Logic
                    vitalsCard.style.display = 'block';
                    vitalsInterpretation.textContent = result.interpretation || '';
                    
                    if (result.detected_type === 'blood_pressure') {
                        vitalsTitle.textContent = 'สรุปผลการวัดความดัน';
                        vitalsIcon.className = 'fas fa-heartbeat';
                        vitalsBody.innerHTML = `
                            <div class="vitals-grid">
                                <div class="vitals-item">
                                    <span class="vitals-label">ค่าบน (SYS)</span>
                                    <span class="vitals-value">${result.data.systolic || '--'}</span>
                                    <span class="vitals-unit">mmHg</span>
                                </div>
                                <div class="vitals-item">
                                    <span class="vitals-label">ค่าล่าง (DIA)</span>
                                    <span class="vitals-value">${result.data.diastolic || '--'}</span>
                                    <span class="vitals-unit">mmHg</span>
                                </div>
                                <div class="vitals-item">
                                    <span class="vitals-label">ชีพจร (Pulse)</span>
                                    <span class="vitals-value">${result.data.pulse || '--'}</span>
                                    <span class="vitals-unit">bpm</span>
                                </div>
                            </div>
                        `;
                    } else {
                        vitalsTitle.textContent = 'สรุปผลระดับน้ำตาล';
                        vitalsIcon.className = 'fas fa-tint';
                        vitalsBody.innerHTML = `
                            <div class="vitals-grid">
                                <div class="vitals-item full-width">
                                    <span class="vitals-label">ระดับน้ำตาลในเลือด</span>
                                    <span class="vitals-value">${result.data.value || '--'}</span>
                                    <span class="vitals-unit">${result.data.unit || 'mg/dL'}</span>
                                    <p class="vitals-context">${result.data.context || ''}</p>
                                </div>
                            </div>
                        `;
                    }
                    vitalsCard.scrollIntoView({ behavior: 'smooth' });
                } else if (result.detected_type === 'food') {
                    // Food Nutrition Logic
                    vitalsCard.style.display = 'block';
                    vitalsTitle.textContent = 'ข้อมูลโภชนาการอาหาร';
                    vitalsIcon.className = 'fas fa-utensils';
                    vitalsInterpretation.textContent = result.data.advice || '';
                    
                    const ratingStars = '⭐'.repeat(result.data.rating || 0);
                    
                    vitalsBody.innerHTML = `
                        <div class="food-info">
                            <h4 class="dish-name">${result.data.dish_name || 'ไม่ทราบชื่ออาหาร'}</h4>
                            <div class="rating-box">${ratingStars}</div>
                        </div>
                        <div class="vitals-grid">
                            <div class="vitals-item highlight">
                                <span class="vitals-label">พลังงาน</span>
                                <span class="vitals-value">${result.data.calories || '--'}</span>
                                <span class="vitals-unit">kcal</span>
                            </div>
                            <div class="vitals-item">
                                <span class="vitals-label">โปรตีน</span>
                                <span class="vitals-value">${result.data.protein || '--'}</span>
                            </div>
                            <div class="vitals-item">
                                <span class="vitals-label">ไขมัน</span>
                                <span class="vitals-value">${result.data.fat || '--'}</span>
                            </div>
                            <div class="vitals-item">
                                <span class="vitals-label">คาร์บ</span>
                                <span class="vitals-value">${result.data.carbs || '--'}</span>
                            </div>
                        </div>
                    `;
                    vitalsCard.scrollIntoView({ behavior: 'smooth' });
                } else if (result.detected_type === 'appointment') {
                    // Appointment Logic
                    vitalsCard.style.display = 'block';
                    vitalsTitle.textContent = 'ข้อมูลการนัดหมายแพทย์';
                    vitalsIcon.className = 'fas fa-calendar-check';
                    vitalsInterpretation.textContent = result.interpretation || '';
                    
                    vitalsBody.innerHTML = `
                        <div class="appointment-info">
                            <h4 class="hospital-name"><i class="fas fa-hospital"></i> ${result.data.hospital || 'โรงพยาบาล'}</h4>
                            <p class="doctor-name"><strong>แพทย์:</strong> ${result.data.doctor || '-'}</p>
                            <p class="department"><strong>แผนก:</strong> ${result.data.department || '-'}</p>
                        </div>
                        <div class="vitals-grid">
                            <div class="vitals-item highlight-blue">
                                <span class="vitals-label">วันที่นัด</span>
                                <span class="vitals-value-small">${result.data.date || '--'}</span>
                            </div>
                            <div class="vitals-item highlight-blue">
                                <span class="vitals-label">เวลา</span>
                                <span class="vitals-value-small">${result.data.time || '--'}</span>
                            </div>
                        </div>
                        <div class="appointment-extra">
                            <div class="prep-box">
                                <strong><i class="fas fa-exclamation-circle"></i> การเตรียมตัว:</strong>
                                <p>${result.data.preparation || 'ไม่มีข้อมูลการเตรียมตัวพิเศษ'}</p>
                            </div>
                            <div class="reason-box">
                                <strong><i class="fas fa-notes-medical"></i> เหตุผลการนัด:</strong>
                                <p>${result.data.reason || '-'}</p>
                            </div>
                        </div>
                    `;
                    vitalsCard.scrollIntoView({ behavior: 'smooth' });
                } else {
                    showToast('ไม่สามารถระบุประเภทข้อมูลสุขภาพได้', 'warning');
                }
            } else {
                showToast(result.detail || 'Error scanning image.', 'danger');
            }
        } catch (error) {
            showToast('Network error or server down.', 'danger');
        } finally {
            loader.style.display = 'none';
            scanBtn.disabled = false;
        }
    });

    // Manual Add
    manualAddBtn.addEventListener('click', () => {
        medNameInput.value = '';
        medQuantityInput.value = '';
        medFrequencyInput.value = '';
        medTimingInput.value = '';
        medExpiryInput.value = '';
        medInstructionsInput.value = '';
        previewContainer.style.display = 'none';
        interactionCard.style.display = 'none';
        registrationCard.style.display = 'block';
        registrationCard.scrollIntoView({ behavior: 'smooth' });
    });

    // Manual Interaction Check
    manualCheckBtn.addEventListener('click', async () => {
        const name = medNameInput.value.trim();
        if (!name) return showToast('Please enter a medicine name.', 'warning');

        loader.style.display = 'flex';
        try {
            const response = await fetch(`/api/check_interaction?name=${encodeURIComponent(name)}`);
            const result = await response.json();
            interactionText.innerHTML = result.report.replace(/\n/g, '<br>');
            interactionCard.style.display = 'block';
            registrationCard.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            showToast('Error checking interaction.', 'danger');
        } finally {
            loader.style.display = 'none';
        }
    });

    // Save to Database
    registerBtn.addEventListener('click', async () => {
        const medData = {
            name: medNameInput.value,
            quantity: medQuantityInput.value,
            frequency: medFrequencyInput.value,
            time_of_taking: medTimingInput.value,
            expiry: medExpiryInput.value,
            instructions: medInstructionsInput.value
        };

        try {
            const response = await fetch('/api/medicines', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(medData)
            });
            const result = await response.json();
            if (result.success) {
                showToast('Medicine registered successfully!', 'success');
                registrationCard.style.display = 'none';
                interactionCard.style.display = 'none';
                fetchMedicines();
            }
        } catch (error) {
            showToast('Error saving medicine.', 'danger');
        }
    });

    // Toast Notification System
    function showToast(message, type = 'primary') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i> <span>${message}</span>`;
        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    // Medicine Dashboard
    async function fetchMedicines() {
        try {
            const response = await fetch('/api/medicines');
            const meds = await response.json();
            medCount.textContent = meds.length;
            
            if (meds.length === 0) {
                medicineList.innerHTML = '<div class="empty-state"><i class="fas fa-pills"></i><p>No medicines yet.</p></div>';
                return;
            }

            medicineList.innerHTML = meds.map(m => `
                <div class="med-item">
                    <div class="med-info">
                        <h4>${m.name}</h4>
                        <p><strong>Quantity: ${m.quantity}</strong> • ${m.frequency}</p>
                        <p>Timing: ${m.time_of_taking}</p>
                        <p>${m.instructions}</p>
                    </div>
                    <div class="med-actions">
                        <button class="notify-btn" onclick="triggerNotify(${m.id})" title="Send Notification">
                            <i class="fas fa-bell"></i>
                        </button>
                        <button class="delete-btn" onclick="deleteMed(${m.id})" title="Delete">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error fetching meds:', error);
        }
    }

    window.triggerNotify = async (id) => {
        try {
            const response = await fetch(`/api/notify/${id}`, { method: 'POST' });
            const result = await response.json();
            if (result.success) {
                showToast(result.message, 'success');
            }
        } catch (error) {
            showToast('Failed to trigger notification.', 'danger');
        }
    };

    window.deleteMed = async (id) => {
        if (!confirm('Remove this medicine?')) return;
        try {
            await fetch(`/api/medicines/${id}`, { method: 'DELETE' });
            showToast('Medicine removed.', 'info');
            fetchMedicines();
        } catch (error) {
            showToast('Error deleting medicine.', 'danger');
        }
    };
});

document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle
    const themeToggle = document.getElementById('checkbox');
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    
    // Set initial theme
    if (localStorage.getItem("theme") === "dark" || (!localStorage.getItem("theme") && prefersDarkScheme.matches)) {
        document.documentElement.setAttribute("data-theme", "dark");
        themeToggle.checked = true;
    }

    themeToggle.addEventListener("change", function() {
        if (this.checked) {
            document.documentElement.setAttribute("data-theme", "dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.removeAttribute("data-theme");
            localStorage.setItem("theme", "light");
        }
    });

    // Elements
    const hospitalList = document.getElementById('hospital-list');
    const hospitalSearch = document.getElementById('hospital-search');
    const serviceSearch = document.getElementById('service-search');
    const currentHospitalName = document.getElementById('current-hospital-name');
    const recordCountBadge = document.getElementById('record-count');
    const emptyState = document.getElementById('empty-state');
    const dataTableWrapper = document.getElementById('data-table-wrapper');
    const tableBody = document.getElementById('table-body');
    const loader = document.getElementById('loader');
    const btnRefresh = document.getElementById('btn-refresh');

    let hospitalsData = [];
    let currentTableData = [];
    let activeHospitalId = null;

    // Load hospitals
    async function loadHospitals() {
        try {
            const response = await fetch('/api/hospitals');
            const result = await response.json();
            
            if (result.status === 'success') {
                hospitalsData = result.data;
                renderHospitals(hospitalsData);
            } else {
                hospitalList.innerHTML = `<li style="padding: 15px; color: red;">Lỗi tải danh sách: ${result.message}</li>`;
            }
        } catch (error) {
            hospitalList.innerHTML = `<li style="padding: 15px; color: red;">Lỗi kết nối server</li>`;
        }
    }

    // Render hospitals list
    function renderHospitals(hospitals) {
        hospitalList.innerHTML = '';
        if (hospitals.length === 0) {
            hospitalList.innerHTML = `<li style="padding: 15px; text-align: center; color: var(--text-secondary);">Không tìm thấy kết quả</li>`;
            return;
        }

        hospitals.forEach(h => {
            const li = document.createElement('li');
            li.className = `hospital-item ${activeHospitalId === h.id ? 'active' : ''}`;
            li.innerHTML = `
                <i class="fa-solid fa-building-medical"></i>
                <span>${h.name}</span>
            `;
            li.addEventListener('click', () => {
                // Update active state
                document.querySelectorAll('.hospital-item').forEach(el => el.classList.remove('active'));
                li.classList.add('active');
                
                activeHospitalId = h.id;
                currentHospitalName.textContent = h.name;
                loadTableData(h.id);
            });
            hospitalList.appendChild(li);
        });
    }

    // Filter hospitals
    hospitalSearch.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = hospitalsData.filter(h => h.name.toLowerCase().includes(query));
        renderHospitals(filtered);
    });

    // Load table data
    async function loadTableData(tableId) {
        emptyState.classList.add('hidden');
        dataTableWrapper.classList.add('hidden');
        loader.classList.remove('hidden');
        recordCountBadge.classList.add('hidden');
        serviceSearch.value = '';

        try {
            const response = await fetch(`/api/data/${encodeURIComponent(tableId)}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                currentTableData = result.data;
                renderTable(currentTableData);
                
                recordCountBadge.textContent = `${currentTableData.length} dịch vụ`;
                recordCountBadge.classList.remove('hidden');
                dataTableWrapper.classList.remove('hidden');
            } else {
                alert(`Lỗi khi tải dữ liệu: ${result.message}`);
                emptyState.classList.remove('hidden');
            }
        } catch (error) {
            alert('Lỗi kết nối server');
            emptyState.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
        }
    }

    // Render table
    function renderTable(data) {
        tableBody.innerHTML = '';
        if (data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 30px;">Không có dữ liệu</td></tr>`;
            return;
        }

        const fragment = document.createDocumentFragment();
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            
            // Highlight text if there's note
            let ghiChuHtml = item.ghichu ? `<span class="note-badge">${item.ghichu}</span>` : '';
            
            tr.innerHTML = `
                <td>${item.stt}</td>
                <td>${item.ma}</td>
                <td>${item.ten}</td>
                <td>${item.tenpheduyet}</td>
                <td class="text-right">${item.gia}</td>
                <td>${ghiChuHtml}</td>
            `;
            fragment.appendChild(tr);
        });
        
        tableBody.appendChild(fragment);
    }

    // Filter services
    serviceSearch.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        if (!query) {
            renderTable(currentTableData);
            return;
        }
        
        const filtered = currentTableData.filter(item => 
            (item.ma && item.ma.toLowerCase().includes(query)) || 
            (item.ten && item.ten.toLowerCase().includes(query)) ||
            (item.tenpheduyet && item.tenpheduyet.toLowerCase().includes(query))
        );
        renderTable(filtered);
    });

    // Refresh button
    btnRefresh.addEventListener('click', () => {
        if (activeHospitalId) {
            loadTableData(activeHospitalId);
        } else {
            loadHospitals();
        }
        
        // Add spin animation briefly
        const icon = btnRefresh.querySelector('i');
        icon.style.animation = 'spin 0.5s linear';
        setTimeout(() => {
            icon.style.animation = '';
        }, 500);
    });

    // Initialize
    loadHospitals();
});

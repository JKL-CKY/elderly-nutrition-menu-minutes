const API_BASE = 'http://localhost:8000';

async function apiCall(url, method = 'GET', data = null, isFormData = false) {
    const options = {
        method,
        headers: {}
    };
    
    if (data && !isFormData) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
    } else if (data && isFormData) {
        options.body = data;
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API调用错误:', error);
        throw error;
    }
}

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    document.body.insertBefore(alertDiv, document.body.firstChild);
    setTimeout(() => alertDiv.remove(), 3000);
}

function showLoading(containerId = null) {
    const container = containerId ? document.getElementById(containerId) : document.body;
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading active';
    loadingDiv.id = 'loading-overlay';
    loadingDiv.innerHTML = '<div class="spinner"></div><p>处理中...</p>';
    container.appendChild(loadingDiv);
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) loading.remove();
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

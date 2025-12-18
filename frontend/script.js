const API_BASE_URL = 'https://media-service-hub.onrender.com';

const form = document.getElementById('downloadForm');
const mediaUrlInput = document.getElementById('mediaUrl');
const loadingSpinner = document.getElementById('loadingSpinner');
const mediaInfo = document.getElementById('mediaInfo');
const infoContent = document.getElementById('infoContent');
const downloadOptions = document.getElementById('downloadOptions');
const optionsContainer = document.getElementById('optionsContainer');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const downloadBtn = document.querySelector('.btn-download');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const url = mediaUrlInput.value.trim();
    
    if (!url) {
        showError('Please enter a URL');
        return;
    }

    // Validate URL
    if (!isValidURL(url)) {
        showError('Please enter a valid URL');
        return;
    }

    // Check if it's a supported platform
    if (!isSupportedPlatform(url)) {
        showError('Unsupported URL. Please use YouTube or Instagram links.');
        return;
    }

    await fetchMediaInfo(url);
});

function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function isSupportedPlatform(url) {
    return url.includes('youtube.com') || 
           url.includes('youtu.be') || 
           url.includes('instagram.com');
}

async function fetchMediaInfo(url) {
    hideAllMessages();
    showLoading(true);
    downloadBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/api/info`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch media information');
        }

        displayMediaInfo(data);
        displayDownloadOptions(data);
        showLoading(false);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to fetch media information. Please try again.');
        showLoading(false);
    } finally {
        downloadBtn.disabled = false;
    }
}

function displayMediaInfo(data) {
    infoContent.innerHTML = '';
    
    const infoItems = [
        { label: 'Title', value: data.title || 'N/A' },
        { label: 'Duration', value: data.duration || 'N/A' },
        { label: 'Platform', value: data.platform || 'Unknown' },
        { label: 'Upload Date', value: data.upload_date || 'N/A' }
    ];

    if (data.thumbnail) {
        infoContent.innerHTML += `
            <div class="info-item" style="grid-column: 1 / -1;">
                <img src="${data.thumbnail}" alt="Thumbnail" style="max-width: 100%; border-radius: 8px; margin-bottom: 10px;">
            </div>
        `;
    }

    infoItems.forEach(item => {
        infoContent.innerHTML += `
            <div class="info-item">
                <div class="info-label">${item.label}</div>
                <div class="info-value">${item.value}</div>
            </div>
        `;
    });

    mediaInfo.classList.remove('hidden');
}

function displayDownloadOptions(data) {
    optionsContainer.innerHTML = '';

    if (!data.formats || data.formats.length === 0) {
        optionsContainer.innerHTML = '<p>No download options available</p>';
        downloadOptions.classList.remove('hidden');
        return;
    }

    data.formats.forEach((format, index) => {
        const option = document.createElement('div');
        option.className = 'quality-option';
        
        let details = '';
        if (format.resolution) {
            details = `${format.resolution}`;
        }
        if (format.format) {
            details += ` (${format.format})`;
        }

        option.innerHTML = `
            <div class="quality-label">${format.quality || 'Download'}</div>
            <div class="quality-details">${details}</div>
            <button class="btn-quality-download" onclick="downloadFile('${data.url}', '${format.format_id}')">
                Download
            </button>
        `;
        
        optionsContainer.appendChild(option);
    });

    downloadOptions.classList.remove('hidden');
}

async function downloadFile(url, formatId) {
    hideAllMessages();
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                url: url,
                format_id: formatId 
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Download failed');
        }

        // Get the filename from the response header
        const contentDisposition = response.headers.get('content-disposition');
        const filename = contentDisposition 
            ? contentDisposition.split('filename=')[1].replace(/"/g, '')
            : 'download';

        // Create blob and trigger download
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);

        showSuccess('Download started successfully!');
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Download failed. Please try again.');
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    if (show) {
        loadingSpinner.classList.remove('hidden');
        mediaInfo.classList.add('hidden');
        downloadOptions.classList.add('hidden');
    } else {
        loadingSpinner.classList.add('hidden');
    }
}

function showError(message) {
    errorMessage.textContent = '❌ ' + message;
    errorMessage.classList.remove('hidden');
}

function showSuccess(message) {
    successMessage.textContent = '✅ ' + message;
    successMessage.classList.remove('hidden');
    setTimeout(() => {
        successMessage.classList.add('hidden');
    }, 5000);
}

function hideAllMessages() {
    errorMessage.classList.add('hidden');
    successMessage.classList.add('hidden');
}

// Allow pasting from clipboard
document.addEventListener('paste', (e) => {
    if (document.activeElement !== mediaUrlInput) return;
    
    e.preventDefault();
    const text = e.clipboardData.getData('text');
    mediaUrlInput.value = text;
    mediaUrlInput.focus();
});

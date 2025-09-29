// ==================== 启动广告管理 ====================

let currentUploadType = 'image'; // 当前上传类型
let splashAdsData = []; // 广告数据
let currentAdPage = 1; // 当前页码
const adPageSize = 10; // 每页数量

// 获取认证令牌
function getAuthToken() {
    // 尝试从全局变量获取
    if (typeof authToken !== 'undefined' && authToken) {
        return authToken;
    }
    // 尝试从localStorage获取
    const token = localStorage.getItem('admin_token');
    if (token) {
        return token;
    }
    // 默认使用admin-token（开发环境）
    return 'admin-token';
}

// 加载启动广告列表
async function loadSplashAds(page = 1) {
    try {
        const status = document.getElementById('adStatusFilter').value;
        const type = document.getElementById('adTypeFilter').value;
        const search = document.getElementById('adSearchInput').value;
        
        const params = new URLSearchParams({
            page: page,
            page_size: adPageSize
        });
        
        if (status) params.append('status', status);
        if (type) params.append('ad_type', type);
        if (search) params.append('search', search);
        
        const response = await fetch(`/api/v1/splash-ads?${params}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            splashAdsData = data.items;
            currentAdPage = page;
            renderSplashAdsTable(data);
            renderAdsPagination(data);
        } else {
            showError('加载广告列表失败');
        }
    } catch (error) {
        showError('加载广告列表失败: ' + error.message);
    }
}

// 渲染广告列表表格
function renderSplashAdsTable(data) {
    const tbody = document.getElementById('splashAdsTableBody');
    
    if (!data.items || data.items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center">暂无广告数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.items.map(ad => {
        const clickRate = ad.view_count > 0 ? ((ad.click_count / ad.view_count) * 100).toFixed(2) : '0.00';
        const statusBadge = getStatusBadge(ad.status);
        const typeBadge = getTypeBadge(ad.ad_type);
        
        return `
            <tr>
                <td>${ad.id}</td>
                <td>
                    <div class="d-flex align-items-center">
                        ${ad.image_url ? `<img src="${ad.image_url}" alt="广告" style="width: 40px; height: 30px; object-fit: cover; margin-right: 8px;">` : ''}
                        <span>${ad.title}</span>
                    </div>
                </td>
                <td>${typeBadge}</td>
                <td>${statusBadge}</td>
                <td>${ad.priority}</td>
                <td>${ad.view_count}</td>
                <td>${ad.click_count}</td>
                <td>${clickRate}%</td>
                <td>${formatDateTime(ad.created_at)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="editSplashAd(${ad.id})" title="编辑">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-${ad.status === 'active' ? 'warning' : 'success'}" 
                                onclick="toggleAdStatus(${ad.id}, '${ad.status === 'active' ? 'inactive' : 'active'}')" 
                                title="${ad.status === 'active' ? '停用' : '启用'}">
                            <i class="bi bi-${ad.status === 'active' ? 'pause' : 'play'}"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="deleteSplashAd(${ad.id})" title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// 渲染分页
function renderAdsPagination(data) {
    const pagination = document.getElementById('splashAdsPagination');
    
    if (data.total_pages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '<ul class="pagination">';
    
    // 上一页
    if (data.page > 1) {
        paginationHTML += `<li class="page-item">
            <a class="page-link" href="#" onclick="loadSplashAds(${data.page - 1})">上一页</a>
        </li>`;
    }
    
    // 页码
    const startPage = Math.max(1, data.page - 2);
    const endPage = Math.min(data.total_pages, data.page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `<li class="page-item ${i === data.page ? 'active' : ''}">
            <a class="page-link" href="#" onclick="loadSplashAds(${i})">${i}</a>
        </li>`;
    }
    
    // 下一页
    if (data.page < data.total_pages) {
        paginationHTML += `<li class="page-item">
            <a class="page-link" href="#" onclick="loadSplashAds(${data.page + 1})">下一页</a>
        </li>`;
    }
    
    paginationHTML += '</ul>';
    pagination.innerHTML = paginationHTML;
}

// 获取状态徽章
function getStatusBadge(status) {
    const badges = {
        'draft': '<span class="badge bg-secondary">草稿</span>',
        'active': '<span class="badge bg-success">激活</span>',
        'inactive': '<span class="badge bg-warning">停用</span>',
        'expired': '<span class="badge bg-danger">已过期</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">未知</span>';
}

// 获取类型徽章
function getTypeBadge(type) {
    const badges = {
        'image': '<span class="badge bg-primary">图片</span>',
        'video': '<span class="badge bg-info">视频</span>'
    };
    return badges[type] || '<span class="badge bg-secondary">未知</span>';
}

// 搜索广告
function searchSplashAds() {
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
        loadSplashAds(1);
    }, 500);
}

// 切换广告类型字段显示
function toggleAdTypeFields() {
    const adType = document.getElementById('adType').value;
    const imageSection = document.getElementById('imageUploadSection');
    const videoSection = document.getElementById('videoUploadSection');
    
    if (adType === 'image') {
        imageSection.style.display = 'block';
        videoSection.style.display = 'none';
        document.getElementById('adImageUrl').required = true;
        document.getElementById('adVideoUrl').required = false;
    } else {
        imageSection.style.display = 'block';
        videoSection.style.display = 'block';
        document.getElementById('adImageUrl').required = false;
        document.getElementById('adVideoUrl').required = true;
    }
}

// 切换目标字段显示
function toggleTargetFields() {
    const action = document.getElementById('adClickAction').value;
    const urlField = document.getElementById('targetUrlField');
    const idField = document.getElementById('targetIdField');
    
    urlField.style.display = 'none';
    idField.style.display = 'none';
    
    if (action === 'url') {
        urlField.style.display = 'block';
    } else if (action === 'product' || action === 'category') {
        idField.style.display = 'block';
        document.getElementById('adTargetId').placeholder = action === 'product' ? '商品ID' : '分类ID';
    }
}

// 上传广告素材
function uploadAdMedia(type) {
    currentUploadType = type;
    const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
    modal.show();
}

// 执行上传
async function performUpload() {
    const fileInput = document.getElementById('mediaFileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('请选择文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const progressBar = document.querySelector('#uploadProgress .progress-bar');
    const progressContainer = document.getElementById('uploadProgress');
    
    try {
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        
        const response = await fetch('/api/v1/splash-ads/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // 更新对应的URL字段
            if (currentUploadType === 'image') {
                document.getElementById('adImageUrl').value = result.url;
                updateImagePreview(result.url);
            } else {
                document.getElementById('adVideoUrl').value = result.url;
                updateVideoPreview(result.url);
            }
            
            progressBar.style.width = '100%';
            showSuccess('文件上传成功');
            
            // 关闭上传模态框
            bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
            
        } else {
            const error = await response.json();
            showError('上传失败: ' + error.detail);
        }
    } catch (error) {
        showError('上传失败: ' + error.message);
    } finally {
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 1000);
    }
}

// 更新图片预览
function updateImagePreview(url) {
    const preview = document.getElementById('imagePreview');
    const img = document.getElementById('previewImage');
    
    if (url) {
        img.src = url;
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
}

// 更新视频预览
function updateVideoPreview(url) {
    const preview = document.getElementById('videoPreview');
    const source = document.getElementById('videoSource');
    const video = document.getElementById('previewVideo');
    
    if (url) {
        source.src = url;
        video.load();
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
}

// 保存广告
async function saveSplashAd() {
    const form = document.getElementById('splashAdForm');
    const formData = new FormData(form);
    const adId = document.getElementById('adId').value;
    
    // 构建请求数据
    const data = {
        title: formData.get('title'),
        description: formData.get('description'),
        ad_type: formData.get('ad_type'),
        image_url: formData.get('image_url') || null,
        video_url: formData.get('video_url') || null,
        click_action: formData.get('click_action'),
        target_url: formData.get('target_url') || null,
        target_id: formData.get('target_id') ? parseInt(formData.get('target_id')) : null,
        display_duration: parseInt(formData.get('display_duration')),
        skip_enabled: formData.has('skip_enabled'),
        skip_delay: parseInt(formData.get('skip_delay')),
        start_time: formData.get('start_time') || null,
        end_time: formData.get('end_time') || null,
        priority: parseInt(formData.get('priority')),
        weight: parseInt(formData.get('weight'))
    };
    
    try {
        const url = adId ? `/api/v1/splash-ads/${adId}` : '/api/v1/splash-ads';
        const method = adId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showSuccess(adId ? '广告更新成功' : '广告创建成功');
            bootstrap.Modal.getInstance(document.getElementById('addSplashAdModal')).hide();
            loadSplashAds(currentAdPage);
        } else {
            const error = await response.json();
            showError('保存失败: ' + error.detail);
        }
    } catch (error) {
        showError('保存失败: ' + error.message);
    }
}

// 编辑广告
async function editSplashAd(adId) {
    try {
        const response = await fetch(`/api/v1/splash-ads/${adId}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            const ad = await response.json();
            
            // 填充表单数据
            document.getElementById('adId').value = ad.id;
            document.getElementById('adTitle').value = ad.title;
            document.getElementById('adDescription').value = ad.description || '';
            document.getElementById('adType').value = ad.ad_type;
            document.getElementById('adImageUrl').value = ad.image_url || '';
            document.getElementById('adVideoUrl').value = ad.video_url || '';
            document.getElementById('adClickAction').value = ad.click_action || 'none';
            document.getElementById('adTargetUrl').value = ad.target_url || '';
            document.getElementById('adTargetId').value = ad.target_id || '';
            document.getElementById('adDuration').value = ad.display_duration;
            document.getElementById('adSkipEnabled').checked = ad.skip_enabled;
            document.getElementById('adSkipDelay').value = ad.skip_delay;
            document.getElementById('adStartTime').value = ad.start_time ? new Date(ad.start_time).toISOString().slice(0, 16) : '';
            document.getElementById('adEndTime').value = ad.end_time ? new Date(ad.end_time).toISOString().slice(0, 16) : '';
            document.getElementById('adPriority').value = ad.priority;
            document.getElementById('adWeight').value = ad.weight;
            
            // 更新界面
            toggleAdTypeFields();
            toggleTargetFields();
            updateImagePreview(ad.image_url);
            updateVideoPreview(ad.video_url);
            
            // 更新模态框标题
            document.getElementById('splashAdModalTitle').textContent = '编辑启动广告';
            
            // 显示模态框
            const modal = new bootstrap.Modal(document.getElementById('addSplashAdModal'));
            modal.show();
            
        } else {
            showError('获取广告信息失败');
        }
    } catch (error) {
        showError('获取广告信息失败: ' + error.message);
    }
}

// 切换广告状态
async function toggleAdStatus(adId, newStatus) {
    try {
        const response = await fetch(`/api/v1/splash-ads/${adId}/status?status=${newStatus}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            showSuccess('状态更新成功');
            loadSplashAds(currentAdPage);
        } else {
            showError('状态更新失败');
        }
    } catch (error) {
        showError('状态更新失败: ' + error.message);
    }
}

// 删除广告
async function deleteSplashAd(adId) {
    if (!confirm('确定要删除这个广告吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/v1/splash-ads/${adId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (response.ok) {
            showSuccess('广告删除成功');
            loadSplashAds(currentAdPage);
        } else {
            showError('删除失败');
        }
    } catch (error) {
        showError('删除失败: ' + error.message);
    }
}

// 重置广告表单
function resetSplashAdForm() {
    document.getElementById('splashAdForm').reset();
    document.getElementById('adId').value = '';
    document.getElementById('splashAdModalTitle').textContent = '添加启动广告';
    toggleAdTypeFields();
    toggleTargetFields();
    updateImagePreview('');
    updateVideoPreview('');
}

// 初始化事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 监听模态框关闭事件
    const modal = document.getElementById('addSplashAdModal');
    if (modal) {
        modal.addEventListener('hidden.bs.modal', resetSplashAdForm);
    }
    
    // 监听URL输入框变化，更新预览
    const imageUrlInput = document.getElementById('adImageUrl');
    const videoUrlInput = document.getElementById('adVideoUrl');
    
    if (imageUrlInput) {
        imageUrlInput.addEventListener('input', function() {
            updateImagePreview(this.value);
        });
    }
    
    if (videoUrlInput) {
        videoUrlInput.addEventListener('input', function() {
            updateVideoPreview(this.value);
        });
    }
});

// 工具函数：格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 工具函数：显示成功消息
function showSuccess(message) {
    showNotification(message, 'success');
}

// 工具函数：显示错误消息
function showError(message) {
    showNotification(message, 'error');
}

// 通知系统
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // 自动消失
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

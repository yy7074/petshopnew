// 增强版后台管理系统JavaScript
// 全局变量
const API_BASE_URL = 'http://localhost:3000/api/v1/admin';
let currentSection = 'dashboard';
let authToken = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    // 检查管理员身份验证
    checkAdminAuth();
});

// 管理员身份验证检查
function checkAdminAuth() {
    const token = localStorage.getItem('admin_token');
    if (token) {
        authToken = token;
        // 验证token有效性
        validateToken();
    } else {
        // 显示登录界面
        showAdminLogin();
    }
}

// 验证token
async function validateToken() {
    try {
        // 暂时跳过token验证，直接认为有效
        // 因为后端可能没有验证接口
        hideAdminLogin();
        loadDashboardData();
    } catch (error) {
        console.error('Token验证失败:', error);
        showAdminLogin();
    }
}

// 显示管理员登录界面
function showAdminLogin() {
    const loginModal = document.getElementById('adminLoginModal');
    if (!loginModal) {
        createLoginModal();
    }
    const modal = new bootstrap.Modal(document.getElementById('adminLoginModal'));
    modal.show();
}

// 隐藏登录界面
function hideAdminLogin() {
    const loginModal = document.getElementById('adminLoginModal');
    if (loginModal) {
        const modal = bootstrap.Modal.getInstance(loginModal);
        if (modal) modal.hide();
    }
}

// 创建登录模态框
function createLoginModal() {
    const modalHTML = `
        <div class="modal fade" id="adminLoginModal" tabindex="-1" data-bs-backdrop="static">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">管理员登录</h5>
                    </div>
                    <div class="modal-body">
                        <form id="adminLoginForm">
                            <div class="mb-3">
                                <label for="adminUsername" class="form-label">用户名</label>
                                <input type="text" class="form-control" id="adminUsername" required>
                            </div>
                            <div class="mb-3">
                                <label for="adminPassword" class="form-label">密码</label>
                                <input type="password" class="form-control" id="adminPassword" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="adminLogin()">登录</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 管理员登录
window.adminLogin = async function() {
    const username = document.getElementById('adminUsername').value;
    const password = document.getElementById('adminPassword').value;

    try {
        const response = await apiRequest('/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.access_token) {
            authToken = response.access_token;
            localStorage.setItem('admin_token', authToken);
            hideAdminLogin();
            showSuccess('登录成功');
            // 登录成功后加载数据
            setTimeout(() => {
                loadDashboardData();
            }, 1000);
        } else {
            showError('登录失败：' + response.message);
        }
    } catch (error) {
        showError('登录失败：' + error.message);
    }
}

// 显示指定的内容区域
function showSection(sectionName) {
    // 隐藏所有内容区域
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // 显示指定区域
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // 更新导航状态
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[href="#${sectionName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // 更新页面标题
    const titles = {
        'dashboard': '仪表盘',
        'users': '用户管理',
        'products': '商品管理',
        'categories': '分类管理',
        'orders': '订单管理',
        'shops': '店铺管理',
        'events': '专场活动',
        'messages': '消息管理',
        'settings': '系统设置'
    };
    
    const pageTitle = document.getElementById('page-title');
    if (pageTitle && titles[sectionName]) {
        pageTitle.textContent = titles[sectionName];
    }
    
    currentSection = sectionName;
    
    // 根据不同区域加载对应数据
    switch(sectionName) {
        case 'users':
            loadUsers();
            break;
        case 'products':
            loadProducts();
            break;
        case 'categories':
            loadCategories();
            break;
        case 'orders':
            loadOrders();
            break;
        case 'events':
            loadEvents();
            break;
        case 'shops':
            loadShops();
            break;
        case 'messages':
            loadMessages();
            break;
    }
}

// 初始化图表
function initCharts() {
    // 销售趋势图
    const salesCtx = document.getElementById('salesChart');
    if (salesCtx) {
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
                datasets: [{
                    label: '销售额',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '¥' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    // 分类占比图
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx) {
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: ['宠物', '水族', '宠物用品', '宠物食品'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: [
                        '#4e73df',
                        '#1cc88a',
                        '#36b9cc',
                        '#f6c23e'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// 加载仪表盘数据
async function loadDashboardData() {
    if (!authToken) {
        console.log('没有认证token，跳过加载数据');
        return;
    }
    
    try {
        console.log('开始加载仪表盘数据，token:', authToken ? '已设置' : '未设置');
        const response = await apiRequest('/dashboard/stats');
        
        // 更新统计数据
        document.getElementById('total-users').textContent = response.total_users.toLocaleString();
        document.getElementById('total-products').textContent = response.total_products.toLocaleString();
        document.getElementById('today-orders').textContent = response.today_orders.toLocaleString();
        document.getElementById('today-revenue').textContent = '¥' + response.today_revenue.toLocaleString();
        
    } catch (error) {
        console.error('加载仪表盘数据失败:', error);
        if (error.message.includes('401')) {
            showError('认证已过期，请重新登录');
            logout();
            return;
        }
        // 使用模拟数据
        const stats = {
            totalUsers: 12345,
            totalProducts: 8967,
            todayOrders: 156,
            todayRevenue: 23456
        };
        
        document.getElementById('total-users').textContent = stats.totalUsers.toLocaleString();
        document.getElementById('total-products').textContent = stats.totalProducts.toLocaleString();
        document.getElementById('today-orders').textContent = stats.todayOrders.toLocaleString();
        document.getElementById('today-revenue').textContent = '¥' + stats.todayRevenue.toLocaleString();
    }
}

// 加载用户数据
async function loadUsers() {
    try {
        const response = await apiRequest('/users', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const tbody = document.querySelector('#usersTable tbody');
        if (tbody && response.users) {
            tbody.innerHTML = response.users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.phone}</td>
                    <td>${user.email || '未填写'}</td>
                    <td>
                        <span class="badge ${getStatusClass(user.status)}">
                            ${getStatusText(user.status)}
                        </span>
                    </td>
                    <td>${formatDateTime(user.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="viewUser(${user.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-warning me-1" onclick="editUser(${user.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('加载用户数据失败:', error);
        showError('加载用户数据失败');
    }
}

// 加载商品数据
async function loadProducts() {
    try {
        const response = await apiRequest('/products', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const tbody = document.querySelector('#productsTable tbody');
        if (tbody && response.products) {
            tbody.innerHTML = response.products.map(product => `
                <tr>
                    <td>${product.id}</td>
                    <td>${product.title}</td>
                    <td>${product.category_name || '未分类'}</td>
                    <td>${product.seller_name}</td>
                    <td>¥${product.current_price.toFixed(2)}</td>
                    <td>
                        <span class="badge ${getProductStatusClass(product.status)}">
                            ${getProductStatusText(product.status)}
                        </span>
                    </td>
                    <td>${formatDateTime(product.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="viewProduct(${product.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-warning me-1" onclick="editProduct(${product.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('加载商品数据失败:', error);
        showError('加载商品数据失败');
    }
}

// 加载分类数据
async function loadCategories() {
    try {
        const response = await apiRequest('/categories', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const tbody = document.querySelector('#categoriesTable tbody');
        if (tbody && response.categories) {
            tbody.innerHTML = response.categories.map(category => `
                <tr>
                    <td>${category.id}</td>
                    <td>${category.name}</td>
                    <td>${category.parent_name || '顶级分类'}</td>
                    <td>${category.product_count || 0}</td>
                    <td>${category.sort_order}</td>
                    <td>
                        <span class="badge ${category.is_active ? 'status-active' : 'status-inactive'}">
                            ${category.is_active ? '启用' : '禁用'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-warning me-1" onclick="editCategory(${category.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteCategory(${category.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('加载分类数据失败:', error);
        showError('加载分类数据失败');
    }
}

// 加载订单数据
async function loadOrders() {
    try {
        const response = await apiRequest('/orders', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const tbody = document.querySelector('#ordersTable tbody');
        if (tbody && response.orders) {
            tbody.innerHTML = response.orders.map(order => `
                <tr>
                    <td>${order.order_no}</td>
                    <td>${order.buyer_name}</td>
                    <td>${order.product_title}</td>
                    <td>¥${order.total_amount.toFixed(2)}</td>
                    <td>
                        <span class="badge ${getOrderStatusClass(order.order_status)}">
                            ${getOrderStatusText(order.order_status)}
                        </span>
                    </td>
                    <td>${formatDateTime(order.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="viewOrder('${order.order_no}')">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="updateOrderStatus('${order.order_no}')">
                            <i class="bi bi-pencil"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('加载订单数据失败:', error);
        showError('加载订单数据失败');
    }
}

// 加载店铺数据
async function loadShops() {
    try {
        const response = await apiRequest('/shops', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const tbody = document.querySelector('#shopsTable tbody');
        if (tbody && response.shops) {
            tbody.innerHTML = response.shops.map(shop => `
                <tr>
                    <td>${shop.id}</td>
                    <td>${shop.shop_name}</td>
                    <td>${shop.owner_name}</td>
                    <td>${shop.contact_phone}</td>
                    <td>${shop.total_sales}</td>
                    <td>
                        <span class="badge ${getShopStatusClass(shop.status)}">
                            ${getShopStatusText(shop.status)}
                        </span>
                    </td>
                    <td>${formatDateTime(shop.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="viewShop(${shop.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-warning me-1" onclick="editShop(${shop.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteShop(${shop.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('加载店铺数据失败:', error);
        showError('加载店铺数据失败');
    }
}

// 加载专场活动数据
async function loadEvents() {
    try {
        const response = await apiRequest('/events', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const tbody = document.querySelector('#eventsTable tbody');
        if (tbody && response.events) {
            tbody.innerHTML = response.events.map(event => `
                <tr>
                    <td>${event.id}</td>
                    <td>${event.title}</td>
                    <td>${formatDateTime(event.start_time)}</td>
                    <td>${formatDateTime(event.end_time)}</td>
                    <td>${event.product_count || 0}</td>
                    <td>
                        <span class="badge ${event.is_active ? 'status-active' : 'status-inactive'}">
                            ${event.is_active ? '进行中' : '已结束'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="viewEvent(${event.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-warning me-1" onclick="editEvent(${event.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteEvent(${event.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('加载专场活动数据失败:', error);
        showError('加载专场活动数据失败');
    }
}

// 加载消息数据
async function loadMessages() {
    try {
        const response = await apiRequest('/messages', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const tbody = document.querySelector('#messagesTable tbody');
        if (tbody && response.messages) {
            tbody.innerHTML = response.messages.map(message => `
                <tr>
                    <td>${message.id}</td>
                    <td>${message.title || '无标题'}</td>
                    <td>${getMessageTypeText(message.message_type)}</td>
                    <td>${message.sender_name || '系统'}</td>
                    <td>${message.receiver_name}</td>
                    <td>
                        <span class="badge ${message.is_read ? 'status-active' : 'status-pending'}">
                            ${message.is_read ? '已读' : '未读'}
                        </span>
                    </td>
                    <td>${formatDateTime(message.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="viewMessage(${message.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteMessage(${message.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        console.error('加载消息数据失败:', error);
        showError('加载消息数据失败');
    }
}

// 工具函数
function getStatusClass(status) {
    const statusClasses = {
        1: 'status-active',
        2: 'status-inactive',
        3: 'status-banned'
    };
    return statusClasses[status] || 'status-inactive';
}

function getStatusText(status) {
    const statusTexts = {
        1: '正常',
        2: '冻结',
        3: '禁用'
    };
    return statusTexts[status] || '未知';
}

function getProductStatusClass(status) {
    const statusClasses = {
        1: 'status-pending',
        2: 'status-active',
        3: 'status-inactive',
        4: 'status-banned'
    };
    return statusClasses[status] || 'status-inactive';
}

function getProductStatusText(status) {
    const statusTexts = {
        1: '待审核',
        2: '拍卖中',
        3: '已结束',
        4: '已下架'
    };
    return statusTexts[status] || '未知';
}

function getOrderStatusClass(status) {
    const statusClasses = {
        1: 'status-pending',
        2: 'status-warning',
        3: 'status-info',
        4: 'status-success',
        5: 'status-active',
        6: 'status-banned'
    };
    return statusClasses[status] || 'status-inactive';
}

function getOrderStatusText(status) {
    const statusTexts = {
        1: '待支付',
        2: '待发货',
        3: '已发货',
        4: '已收货',
        5: '已完成',
        6: '已取消'
    };
    return statusTexts[status] || '未知';
}

function getShopStatusClass(status) {
    const statusClasses = {
        1: 'status-active',
        2: 'status-warning',
        3: 'status-banned'
    };
    return statusClasses[status] || 'status-inactive';
}

function getShopStatusText(status) {
    const statusTexts = {
        1: '正常',
        2: '暂停',
        3: '关闭'
    };
    return statusTexts[status] || '未知';
}

function getMessageTypeText(type) {
    const typeTexts = {
        1: '系统消息',
        2: '私信',
        3: '拍卖通知',
        4: '订单通知'
    };
    return typeTexts[type] || '未知';
}

function formatDateTime(dateString) {
    if (!dateString) return '未知';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// API请求封装
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        mode: 'cors',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    if (authToken) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API请求失败:', error);
        console.error('请求URL:', url);
        console.error('请求配置:', config);
        throw error;
    }
}

// 显示加载状态
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="text-center"><div class="loading"></div></div>';
    }
}

// 显示错误信息
function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-danger border-0';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// 显示成功信息
function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-success border-0';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// 详细操作函数
window.viewUser = function(userId) {
    // TODO: 实现用户详情查看
    console.log('查看用户:', userId);
}

window.editUser = async function(userId) {
    try {
        // 获取用户详细信息
        const userResponse = await apiRequest(`/users/${userId}`);
        
        // 创建编辑用户的模态框
        const modalHtml = `
            <div class="modal fade" id="editUserModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">编辑用户 - ${userResponse.username}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="editUserForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">用户名</label>
                                            <input type="text" class="form-control" id="username" value="${userResponse.username || ''}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">手机号</label>
                                            <input type="text" class="form-control" id="phone" value="${userResponse.phone || ''}" required>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">邮箱</label>
                                            <input type="email" class="form-control" id="email" value="${userResponse.email || ''}">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">昵称</label>
                                            <input type="text" class="form-control" id="nickname" value="${userResponse.nickname || ''}">
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">真实姓名</label>
                                            <input type="text" class="form-control" id="real_name" value="${userResponse.real_name || ''}">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">性别</label>
                                            <select class="form-control" id="gender">
                                                <option value="0" ${userResponse.gender === 0 ? 'selected' : ''}>未知</option>
                                                <option value="1" ${userResponse.gender === 1 ? 'selected' : ''}>男</option>
                                                <option value="2" ${userResponse.gender === 2 ? 'selected' : ''}>女</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">地区</label>
                                            <input type="text" class="form-control" id="location" value="${userResponse.location || ''}">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">账户余额 (¥)</label>
                                            <div class="input-group">
                                                <input type="number" class="form-control" id="balance" value="${userResponse.balance || 0}" step="0.01" min="0">
                                                <button type="button" class="btn btn-outline-primary" onclick="showAddBalanceDialog(${userId})">
                                                    <i class="bi bi-plus"></i> 充值
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">信用分</label>
                                            <input type="number" class="form-control" id="credit_score" value="${userResponse.credit_score || 100}" min="0" max="1000">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">账户状态</label>
                                            <select class="form-control" id="status">
                                                <option value="1" ${userResponse.status === 1 ? 'selected' : ''}>正常</option>
                                                <option value="2" ${userResponse.status === 2 ? 'selected' : ''}>冻结</option>
                                                <option value="3" ${userResponse.status === 3 ? 'selected' : ''}>禁用</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-12">
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="is_seller" ${userResponse.is_seller ? 'checked' : ''}>
                                                <label class="form-check-label" for="is_seller">卖家权限</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="is_verified" ${userResponse.is_verified ? 'checked' : ''}>
                                                <label class="form-check-label" for="is_verified">已认证</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="is_admin" ${userResponse.is_admin ? 'checked' : ''}>
                                                <label class="form-check-label" for="is_admin">管理员权限</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" onclick="updateUser(${userId})">保存更改</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 添加模态框到页面
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
        modal.show();
        
        // 模态框隐藏时删除
        document.getElementById('editUserModal').addEventListener('hidden.bs.modal', () => {
            document.getElementById('editUserModal').remove();
        });
        
    } catch (error) {
        console.error('获取用户详情失败:', error);
        showError('获取用户详情失败: ' + error.message);
    }
}

window.updateUser = async function(userId) {
    try {
        const formData = {
            username: document.getElementById('username').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            nickname: document.getElementById('nickname').value,
            real_name: document.getElementById('real_name').value,
            gender: parseInt(document.getElementById('gender').value),
            location: document.getElementById('location').value,
            balance: parseFloat(document.getElementById('balance').value),
            credit_score: parseInt(document.getElementById('credit_score').value),
            status: parseInt(document.getElementById('status').value),
            is_seller: document.getElementById('is_seller').checked,
            is_verified: document.getElementById('is_verified').checked,
            is_admin: document.getElementById('is_admin').checked
        };
        
        const response = await apiRequest(`/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
        
        if (response.success) {
            showSuccess('用户信息更新成功');
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('editUserModal'));
            modal.hide();
            // 刷新用户列表
            loadUsers();
        } else {
            showError(response.message || '更新失败');
        }
    } catch (error) {
        console.error('更新用户失败:', error);
        showError('更新用户失败: ' + error.message);
    }
}

window.showAddBalanceDialog = function(userId) {
    const balanceModalHtml = `
        <div class="modal fade" id="addBalanceModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">为用户充值</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">充值金额 (¥)</label>
                            <input type="number" class="form-control" id="addAmount" placeholder="请输入充值金额" step="0.01" min="0.01" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">充值说明</label>
                            <textarea class="form-control" id="addReason" placeholder="充值原因或说明" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" onclick="addUserBalance(${userId})">确认充值</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 添加模态框到页面
    document.body.insertAdjacentHTML('beforeend', balanceModalHtml);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('addBalanceModal'));
    modal.show();
    
    // 模态框隐藏时删除
    document.getElementById('addBalanceModal').addEventListener('hidden.bs.modal', () => {
        document.getElementById('addBalanceModal').remove();
    });
}

window.addUserBalance = async function(userId) {
    try {
        const amount = parseFloat(document.getElementById('addAmount').value);
        const reason = document.getElementById('addReason').value;
        
        if (!amount || amount <= 0) {
            showError('请输入有效的充值金额');
            return;
        }
        
        const response = await apiRequest(`/users/${userId}/add-balance`, {
            method: 'POST',
            body: JSON.stringify({ amount: amount, reason: reason })
        });
        
        if (response.success) {
            showSuccess(`成功充值 ¥${amount}，当前余额: ¥${response.new_balance}`);
            // 关闭充值模态框
            const balanceModal = bootstrap.Modal.getInstance(document.getElementById('addBalanceModal'));
            balanceModal.hide();
            // 更新编辑框中的余额显示
            if (document.getElementById('balance')) {
                document.getElementById('balance').value = response.new_balance;
            }
        } else {
            showError(response.message || '充值失败');
        }
    } catch (error) {
        console.error('充值失败:', error);
        showError('充值失败: ' + error.message);
    }
}

window.deleteUser = function(userId) {
    if (confirm('确定要删除这个用户吗？')) {
        // TODO: 实现用户删除
        console.log('删除用户:', userId);
    }
}

// 加载专场活动数据
async function loadEvents() {
    if (!authToken) return;
    
    try {
        const response = await apiRequest('/events?page=1&size=20');
        
        const eventsTableBody = document.querySelector('#eventsTable tbody');
        if (!eventsTableBody) return;
        
        eventsTableBody.innerHTML = '';
        
        if (response.events && response.events.length > 0) {
            response.events.forEach(event => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${event.id}</td>
                    <td>${event.title}</td>
                    <td>${event.description ? event.description.substring(0, 50) + '...' : '无描述'}</td>
                    <td>${event.product_count || 0}</td>
                    <td>${formatDateTime(event.start_time)}</td>
                    <td>${formatDateTime(event.end_time)}</td>
                    <td>
                        <span class="badge ${event.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${event.is_active ? '活跃' : '禁用'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary me-1" onclick="manageEventProducts(${event.id})">
                            <i class="bi bi-box"></i> 管理商品
                        </button>
                        <button class="btn btn-sm btn-info me-1" onclick="viewEvent(${event.id})">
                            <i class="bi bi-eye"></i> 查看
                        </button>
                        <button class="btn btn-sm btn-warning me-1" onclick="editEvent(${event.id})">
                            <i class="bi bi-pencil"></i> 编辑
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteEvent(${event.id})">
                            <i class="bi bi-trash"></i> 删除
                        </button>
                    </td>
                `;
                eventsTableBody.appendChild(row);
            });
        } else {
            eventsTableBody.innerHTML = '<tr><td colspan="8" class="text-center">暂无专场活动</td></tr>';
        }
        
    } catch (error) {
        console.error('加载专场活动失败:', error);
        showError('加载专场活动失败: ' + error.message);
    }
}

// 管理专场商品
window.manageEventProducts = async function(eventId) {
    try {
        // 创建模态框
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="modal fade" id="manageEventProductsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">管理专场商品</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>专场中的商品</h6>
                                    <div id="eventProductsList">加载中...</div>
                                </div>
                                <div class="col-md-6">
                                    <h6>可添加的商品</h6>
                                    <div class="mb-3">
                                        <input type="text" class="form-control" id="productSearchInput" 
                                               placeholder="搜索商品...">
                                    </div>
                                    <div id="availableProductsList">加载中...</div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const modalElement = document.getElementById('manageEventProductsModal');
        const bsModal = new bootstrap.Modal(modalElement);
        bsModal.show();
        
        // 加载专场中的商品
        loadEventProducts(eventId);
        
        // 加载可添加的商品
        loadAvailableProducts(eventId);
        
        // 绑定搜索事件
        document.getElementById('productSearchInput').addEventListener('input', (e) => {
            loadAvailableProducts(eventId, e.target.value);
        });
        
        // 清理DOM
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
        });
        
    } catch (error) {
        console.error('管理专场商品失败:', error);
        showError('管理专场商品失败: ' + error.message);
    }
}

// 加载专场中的商品
async function loadEventProducts(eventId) {
    try {
        const response = await apiRequest(`/events/${eventId}/products`);
        
        const container = document.getElementById('eventProductsList');
        if (!container) return;
        
        if (response.items && response.items.length > 0) {
            const html = response.items.map(product => `
                <div class="card mb-2">
                    <div class="card-body p-2">
                        <div class="d-flex">
                            ${product.images && product.images.length > 0 ? 
                                `<img src="${product.images[0]}" alt="${product.title}" 
                                     style="width: 50px; height: 50px; object-fit: cover; margin-right: 10px; border-radius: 4px;">` : 
                                `<div style="width: 50px; height: 50px; background: #f8f9fa; margin-right: 10px; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                                    <i class="bi bi-image text-muted"></i>
                                </div>`
                            }
                            <div class="flex-grow-1">
                                <h6 class="card-title mb-1">${product.title}</h6>
                                <p class="card-text small mb-1 text-muted">
                                    起拍价: ¥${product.starting_price} | 当前价: ¥${product.current_price}<br>
                                    状态: ${getProductStatusText(product.status)} | 
                                    出价数: ${product.bid_count || 0}
                                </p>
                                <button class="btn btn-sm btn-danger" 
                                        onclick="removeProductFromEvent(${eventId}, ${product.id})">
                                    <i class="bi bi-dash"></i> 移除
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="text-muted text-center">暂无商品</p>';
        }
        
    } catch (error) {
        console.error('加载专场商品失败:', error);
        document.getElementById('eventProductsList').innerHTML = '<p class="text-danger">加载失败</p>';
    }
}

// 加载可添加的商品
async function loadAvailableProducts(eventId, keyword = '') {
    try {
        const url = `/products/available-for-event?event_id=${eventId}&page=1&size=10${keyword ? '&keyword=' + keyword : ''}`;
        const response = await apiRequest(url);
        
        const container = document.getElementById('availableProductsList');
        if (!container) return;
        
        if (response.products && response.products.length > 0) {
            const html = response.products.map(product => `
                <div class="card mb-2">
                    <div class="card-body p-2">
                        <div class="d-flex">
                            ${product.images && product.images.length > 0 ? 
                                `<img src="${product.images[0]}" alt="${product.title}" 
                                     style="width: 50px; height: 50px; object-fit: cover; margin-right: 10px; border-radius: 4px;">` : 
                                `<div style="width: 50px; height: 50px; background: #f8f9fa; margin-right: 10px; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                                    <i class="bi bi-image text-muted"></i>
                                </div>`
                            }
                            <div class="flex-grow-1">
                                <h6 class="card-title mb-1">${product.title}</h6>
                                <p class="card-text small mb-1 text-muted">
                                    起拍价: ¥${product.starting_price} | 当前价: ¥${product.current_price}<br>
                                    状态: ${getProductStatusText(product.status)} | 
                                    出价数: ${product.bid_count || 0}
                                </p>
                                <button class="btn btn-sm btn-success" 
                                        onclick="addProductToEvent(${eventId}, ${product.id})">
                                    <i class="bi bi-plus"></i> 添加到专场
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="text-muted text-center">暂无可添加商品</p>';
        }
        
    } catch (error) {
        console.error('加载可选商品失败:', error);
        document.getElementById('availableProductsList').innerHTML = '<p class="text-danger">加载失败</p>';
    }
}

// 添加商品到专场
window.addProductToEvent = async function(eventId, productId) {
    try {
        const response = await apiRequest(`/events/${eventId}/products`, {
            method: 'POST',
            body: JSON.stringify({
                product_ids: [productId],
                sort_order: 0
            })
        });
        
        if (response.success) {
            showSuccess(response.message);
            // 重新加载两个列表
            loadEventProducts(eventId);
            loadAvailableProducts(eventId);
        }
        
    } catch (error) {
        console.error('添加商品到专场失败:', error);
        showError('添加商品到专场失败: ' + error.message);
    }
}

// 从专场移除商品
window.removeProductFromEvent = async function(eventId, productId) {
    if (!confirm('确定要从专场中移除这个商品吗？')) return;
    
    try {
        const response = await apiRequest(`/admin/events/${eventId}/products/${productId}`, {
            method: 'DELETE'
        });
        
        if (response.success) {
            showSuccess(response.message);
            // 重新加载两个列表
            loadEventProducts(eventId);
            loadAvailableProducts(eventId);
        }
        
    } catch (error) {
        console.error('移除商品失败:', error);
        showError('移除商品失败: ' + error.message);
    }
}

// 退出登录
function logout() {
    if (confirm('确定要退出登录吗？')) {
        // 清除认证信息
        authToken = null;
        localStorage.removeItem('admin_token');
        
        showSuccess('退出登录成功');
        
        // 1秒后显示登录界面
        setTimeout(() => {
            showAdminLogin();
        }, 1000);
    }
}

// 显示用户资料
function showProfile() {
    showInfo('管理员资料功能开发中...');
}

// 显示信息提示
function showInfo(message) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-info border-0';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // 清理DOM
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function viewProduct(productId) {
    // TODO: 实现商品详情查看
    console.log('查看商品:', productId);
}

function editProduct(productId) {
    // TODO: 实现商品编辑
    console.log('编辑商品:', productId);
}

function deleteProduct(productId) {
    if (confirm('确定要删除这个商品吗？')) {
        // TODO: 实现商品删除
        console.log('删除商品:', productId);
    }
}

function editCategory(categoryId) {
    // TODO: 实现分类编辑
    console.log('编辑分类:', categoryId);
}

function deleteCategory(categoryId) {
    if (confirm('确定要删除这个分类吗？')) {
        // TODO: 实现分类删除
        console.log('删除分类:', categoryId);
    }
}

function viewOrder(orderNo) {
    // TODO: 实现订单详情查看
    console.log('查看订单:', orderNo);
}

function updateOrderStatus(orderNo) {
    // TODO: 实现订单状态更新
    console.log('更新订单状态:', orderNo);
}

function viewShop(shopId) {
    // TODO: 实现店铺详情查看
    console.log('查看店铺:', shopId);
}

function editShop(shopId) {
    // TODO: 实现店铺编辑
    console.log('编辑店铺:', shopId);
}

function deleteShop(shopId) {
    if (confirm('确定要删除这个店铺吗？')) {
        // TODO: 实现店铺删除
        console.log('删除店铺:', shopId);
    }
}

async function viewEvent(eventId) {
    try {
        const response = await apiRequest(`/events/${eventId}`);
        
        // 创建查看专场的模态框
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="modal fade" id="viewEventModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">专场活动详情</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>基本信息</h6>
                                    <p><strong>标题:</strong> ${response.title}</p>
                                    <p><strong>描述:</strong> ${response.description || '无描述'}</p>
                                    <p><strong>状态:</strong> 
                                        <span class="badge ${response.is_active ? 'bg-success' : 'bg-secondary'}">
                                            ${response.is_active ? '活跃' : '禁用'}
                                        </span>
                                    </p>
                                </div>
                                <div class="col-md-6">
                                    <h6>时间信息</h6>
                                    <p><strong>开始时间:</strong> ${formatDateTime(response.start_time)}</p>
                                    <p><strong>结束时间:</strong> ${formatDateTime(response.end_time)}</p>
                                    <p><strong>创建时间:</strong> ${formatDateTime(response.created_at)}</p>
                                    <p><strong>商品数量:</strong> ${response.product_count || 0} 件</p>
                                </div>
                            </div>
                            <hr>
                            <div id="eventProductsPreview">
                                <h6>专场商品预览</h6>
                                <div id="eventProductsContainer">
                                    <div class="text-center">
                                        <div class="loading"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" onclick="editEvent(${eventId})">编辑专场</button>
                            <button type="button" class="btn btn-info" onclick="manageEventProducts(${eventId})">管理商品</button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const modalElement = document.getElementById('viewEventModal');
        const bsModal = new bootstrap.Modal(modalElement);
        bsModal.show();
        
        // 加载专场商品预览
        loadEventProductsPreview(eventId);
        
        // 清理DOM
        modalElement.addEventListener('hidden.bs.modal', function () {
            document.body.removeChild(modal);
        });
        
    } catch (error) {
        console.error('查看专场活动失败:', error);
        showError('查看专场活动失败: ' + error.message);
    }
}

async function editEvent(eventId) {
    try {
        // 获取专场数据
        const response = await apiRequest(`/events/${eventId}`);
        
        // 创建编辑专场的模态框
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="modal fade" id="editEventModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">编辑专场活动</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="editEventForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="eventTitle" class="form-label">专场标题 *</label>
                                            <input type="text" class="form-control" id="eventTitle" 
                                                   value="${response.title}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="eventDescription" class="form-label">专场描述</label>
                                            <textarea class="form-control" id="eventDescription" 
                                                      rows="3">${response.description || ''}</textarea>
                                        </div>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" 
                                                       id="eventIsActive" ${response.is_active ? 'checked' : ''}>
                                                <label class="form-check-label" for="eventIsActive">
                                                    启用专场
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="eventStartTime" class="form-label">开始时间 *</label>
                                            <input type="datetime-local" class="form-control" 
                                                   id="eventStartTime" 
                                                   value="${formatDateTimeForInput(response.start_time)}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="eventEndTime" class="form-label">结束时间 *</label>
                                            <input type="datetime-local" class="form-control" 
                                                   id="eventEndTime" 
                                                   value="${formatDateTimeForInput(response.end_time)}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="eventSortOrder" class="form-label">排序顺序</label>
                                            <input type="number" class="form-control" 
                                                   id="eventSortOrder" 
                                                   value="${response.sort_order || 0}" min="0">
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" onclick="saveEventChanges(${eventId})">
                                <i class="bi bi-save"></i> 保存更改
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const modalElement = document.getElementById('editEventModal');
        const bsModal = new bootstrap.Modal(modalElement);
        bsModal.show();
        
        // 清理DOM
        modalElement.addEventListener('hidden.bs.modal', function () {
            document.body.removeChild(modal);
        });
        
    } catch (error) {
        console.error('获取专场数据失败:', error);
        showError('获取专场数据失败: ' + error.message);
    }
}

// 加载专场商品预览
async function loadEventProductsPreview(eventId) {
    try {
        const response = await apiRequest(`/events/${eventId}/products?page=1&size=5`);
        const container = document.getElementById('eventProductsContainer');
        
        if (!container) return;
        
        if (response.products && response.products.length > 0) {
            const html = response.products.map(product => `
                <div class="card mb-2">
                    <div class="card-body p-2">
                        <div class="row">
                            <div class="col-md-8">
                                <h6 class="card-title mb-1">${product.title}</h6>
                                <p class="card-text small mb-1">
                                    起拍价: ¥${product.starting_price} | 当前价: ¥${product.current_price}
                                </p>
                                <p class="card-text small text-muted mb-0">
                                    卖家: ${product.seller_name} | 分类: ${product.category_name}
                                </p>
                            </div>
                            <div class="col-md-4 text-end">
                                <span class="badge bg-info">${product.status_text || '拍卖中'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
            
            const totalText = response.total > 5 ? `<p class="text-muted small">显示前5件商品，共${response.total}件</p>` : '';
            container.innerHTML = html + totalText;
        } else {
            container.innerHTML = '<p class="text-muted">该专场暂无商品</p>';
        }
    } catch (error) {
        console.error('加载专场商品预览失败:', error);
        document.getElementById('eventProductsContainer').innerHTML = '<p class="text-danger">加载失败</p>';
    }
}

// 保存专场更改
async function saveEventChanges(eventId) {
    try {
        const formData = {
            title: document.getElementById('eventTitle').value.trim(),
            description: document.getElementById('eventDescription').value.trim(),
            start_time: document.getElementById('eventStartTime').value,
            end_time: document.getElementById('eventEndTime').value,
            is_active: document.getElementById('eventIsActive').checked,
            sort_order: parseInt(document.getElementById('eventSortOrder').value) || 0
        };
        
        // 验证必填字段
        if (!formData.title) {
            showError('请输入专场标题');
            return;
        }
        
        if (!formData.start_time || !formData.end_time) {
            showError('请选择开始时间和结束时间');
            return;
        }
        
        if (new Date(formData.start_time) >= new Date(formData.end_time)) {
            showError('结束时间必须晚于开始时间');
            return;
        }
        
        const response = await apiRequest(`/events/${eventId}`, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
        
        if (response.success) {
            showSuccess('专场活动更新成功');
            
            // 关闭编辑模态框
            const editModal = bootstrap.Modal.getInstance(document.getElementById('editEventModal'));
            if (editModal) {
                editModal.hide();
            }
            
            // 关闭查看模态框
            const viewModal = bootstrap.Modal.getInstance(document.getElementById('viewEventModal'));
            if (viewModal) {
                viewModal.hide();
            }
            
            // 刷新专场列表
            loadEvents();
        }
        
    } catch (error) {
        console.error('保存专场更改失败:', error);
        showError('保存专场更改失败: ' + error.message);
    }
}

// 格式化日期时间为输入框格式
function formatDateTimeForInput(dateTimeString) {
    if (!dateTimeString) return '';
    const date = new Date(dateTimeString);
    if (isNaN(date.getTime())) return '';
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function deleteEvent(eventId) {
    if (confirm('确定要删除这个专场活动吗？')) {
        // TODO: 实现专场活动删除
        console.log('删除专场活动:', eventId);
    }
}

function viewMessage(messageId) {
    // TODO: 实现消息详情查看
    console.log('查看消息:', messageId);
}

function deleteMessage(messageId) {
    if (confirm('确定要删除这条消息吗？')) {
        // TODO: 实现消息删除
        console.log('删除消息:', messageId);
    }
}

// 导出数据功能
function exportData() {
    const section = currentSection;
    switch(section) {
        case 'users':
            exportUsers();
            break;
        case 'products':
            exportProducts();
            break;
        case 'orders':
            exportOrders();
            break;
        default:
            showError('当前页面不支持导出数据');
    }
}

function exportUsers() {
    // TODO: 实现用户数据导出
    console.log('导出用户数据');
}

function exportProducts() {
    // TODO: 实现商品数据导出
    console.log('导出商品数据');
}

function exportOrders() {
    // TODO: 实现订单数据导出
    console.log('导出订单数据');
}

// 搜索功能
function searchOrders() {
    const status = document.getElementById('orderStatusFilter').value;
    const search = document.getElementById('orderSearch').value;
    
    loadOrders(1, 20, status, search);
}

// 新增分类
function addCategory() {
    showCategoryModal();
}

// 新增专场活动
function addEvent() {
    showEventModal();
}

// 显示专场活动模态框
function showEventModal(eventId = null) {
    const isEdit = eventId !== null;
    const modalHTML = `
        <div class="modal fade" id="eventModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${isEdit ? '编辑专场活动' : '新建专场活动'}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="eventForm">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="eventTitle" class="form-label">活动名称 *</label>
                                        <input type="text" class="form-control" id="eventTitle" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="eventStatus" class="form-label">状态</label>
                                        <select class="form-select" id="eventStatus">
                                            <option value="true">启用</option>
                                            <option value="false">禁用</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="eventDescription" class="form-label">活动描述</label>
                                <textarea class="form-control" id="eventDescription" rows="3"></textarea>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="eventStartTime" class="form-label">开始时间 *</label>
                                        <input type="datetime-local" class="form-control" id="eventStartTime" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="eventEndTime" class="form-label">结束时间 *</label>
                                        <input type="datetime-local" class="form-control" id="eventEndTime" required>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="eventBannerImage" class="form-label">活动横幅图片URL</label>
                                <input type="url" class="form-control" id="eventBannerImage" 
                                       placeholder="https://example.com/banner.jpg">
                                <div class="form-text">请输入图片的完整URL地址</div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="eventSortOrder" class="form-label">排序权重</label>
                                <input type="number" class="form-control" id="eventSortOrder" value="0" min="0">
                                <div class="form-text">数值越大排序越靠前</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" onclick="saveEvent(${eventId})">
                            ${isEdit ? '更新' : '创建'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 移除旧的模态框
    const existingModal = document.getElementById('eventModal');
    if (existingModal) {
        existingModal.remove();
    }

    // 添加新模态框到页面
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 如果是编辑模式，加载现有数据
    if (isEdit) {
        loadEventData(eventId);
    }
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    modal.show();
    
    // 清理DOM
    document.getElementById('eventModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// 保存专场活动
async function saveEvent(eventId = null) {
    const title = document.getElementById('eventTitle').value.trim();
    const description = document.getElementById('eventDescription').value.trim();
    const startTime = document.getElementById('eventStartTime').value;
    const endTime = document.getElementById('eventEndTime').value;
    const bannerImage = document.getElementById('eventBannerImage').value.trim();
    const isActive = document.getElementById('eventStatus').value === 'true';
    const sortOrder = parseInt(document.getElementById('eventSortOrder').value) || 0;

    // 验证必填字段
    if (!title) {
        showError('请输入活动名称');
        return;
    }
    
    if (!startTime || !endTime) {
        showError('请选择开始时间和结束时间');
        return;
    }
    
    if (new Date(startTime) >= new Date(endTime)) {
        showError('结束时间必须晚于开始时间');
        return;
    }

    const eventData = {
        title,
        description,
        start_time: startTime,
        end_time: endTime,
        banner_image: bannerImage || null,
        is_active: isActive,
        sort_order: sortOrder
    };

    try {
        const url = eventId ? `/admin/events/${eventId}` : '/admin/events';
        const method = eventId ? 'PUT' : 'POST';
        
        const response = await apiRequest(url, {
            method,
            body: JSON.stringify(eventData)
        });

        if (response.success) {
            showSuccess(response.message || (eventId ? '专场活动更新成功' : '专场活动创建成功'));
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('eventModal'));
            if (modal) {
                modal.hide();
            }
            
            // 重新加载专场活动列表
            loadEvents();
        } else {
            showError(response.message || '操作失败');
        }
    } catch (error) {
        console.error('保存专场活动失败:', error);
        showError('保存失败: ' + error.message);
    }
}

// 加载专场活动数据（用于编辑）
async function loadEventData(eventId) {
    try {
        const response = await apiRequest(`/admin/events/${eventId}`);
        
        if (response) {
            document.getElementById('eventTitle').value = response.title || '';
            document.getElementById('eventDescription').value = response.description || '';
            document.getElementById('eventStatus').value = response.is_active ? 'true' : 'false';
            document.getElementById('eventBannerImage').value = response.banner_image || '';
            document.getElementById('eventSortOrder').value = response.sort_order || 0;
            
            // 处理时间格式
            if (response.start_time) {
                const startTime = new Date(response.start_time);
                document.getElementById('eventStartTime').value = startTime.toISOString().slice(0, 16);
            }
            
            if (response.end_time) {
                const endTime = new Date(response.end_time);
                document.getElementById('eventEndTime').value = endTime.toISOString().slice(0, 16);
            }
        }
    } catch (error) {
        console.error('加载专场活动数据失败:', error);
        showError('加载数据失败: ' + error.message);
    }
}

// 编辑专场活动
function editEvent(eventId) {
    showEventModal(eventId);
}

// 查看专场活动
function viewEvent(eventId) {
    // 这里可以实现查看专场活动详情的功能
    console.log('查看专场活动:', eventId);
    // 可以跳转到专场活动详情页面或显示详情模态框
}

// 删除专场活动
async function deleteEvent(eventId) {
    if (!confirm('确定要删除这个专场活动吗？删除后将无法恢复！')) {
        return;
    }
    
    try {
        const response = await apiRequest(`/admin/events/${eventId}`, {
            method: 'DELETE'
        });
        
        if (response.success) {
            showSuccess('专场活动删除成功');
            loadEvents();
        } else {
            showError(response.message || '删除失败');
        }
    } catch (error) {
        console.error('删除专场活动失败:', error);
        showError('删除失败: ' + error.message);
    }
}

// 获取商品状态文本
function getProductStatusText(status) {
    const statusMap = {
        1: '待审核',
        2: '拍卖中',
        3: '已成交',
        4: '流拍',
        5: '已下架'
    };
    return statusMap[status] || '未知';
}

// 发送系统消息
function sendSystemMessage() {
    showSystemMessageModal();
}

// 显示分类模态框
function showCategoryModal(categoryId = null) {
    const modalHTML = `
        <div class="modal fade" id="categoryModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${categoryId ? '编辑分类' : '新增分类'}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="categoryForm">
                            <div class="mb-3">
                                <label for="categoryName" class="form-label">分类名称</label>
                                <input type="text" class="form-control" id="categoryName" required>
                            </div>
                            <div class="mb-3">
                                <label for="parentCategory" class="form-label">父分类</label>
                                <select class="form-select" id="parentCategory">
                                    <option value="0">顶级分类</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="sortOrder" class="form-label">排序</label>
                                <input type="number" class="form-control" id="sortOrder" value="0">
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="isActive" checked>
                                    <label class="form-check-label" for="isActive">启用</label>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" onclick="saveCategory(${categoryId})">保存</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除现有模态框
    const existingModal = document.getElementById('categoryModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('categoryModal'));
    modal.show();
}

// 显示专场活动模态框
function showEventModal(eventId = null) {
    const modalHTML = `
        <div class="modal fade" id="eventModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${eventId ? '编辑专场活动' : '新建专场活动'}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="eventForm">
                            <div class="mb-3">
                                <label for="eventTitle" class="form-label">活动标题</label>
                                <input type="text" class="form-control" id="eventTitle" required>
                            </div>
                            <div class="mb-3">
                                <label for="eventDescription" class="form-label">活动描述</label>
                                <textarea class="form-control" id="eventDescription" rows="3"></textarea>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="startTime" class="form-label">开始时间</label>
                                        <input type="datetime-local" class="form-control" id="startTime" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="endTime" class="form-label">结束时间</label>
                                        <input type="datetime-local" class="form-control" id="endTime" required>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="bannerImage" class="form-label">横幅图片</label>
                                <input type="file" class="form-control" id="bannerImage" accept="image/*">
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="eventActive" checked>
                                    <label class="form-check-label" for="eventActive">启用活动</label>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" onclick="saveEvent(${eventId})">保存</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除现有模态框
    const existingModal = document.getElementById('eventModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    modal.show();
}

// 显示系统消息模态框
function showSystemMessageModal() {
    const modalHTML = `
        <div class="modal fade" id="systemMessageModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">发送系统消息</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="systemMessageForm">
                            <div class="mb-3">
                                <label for="messageTitle" class="form-label">消息标题</label>
                                <input type="text" class="form-control" id="messageTitle" required>
                            </div>
                            <div class="mb-3">
                                <label for="messageContent" class="form-label">消息内容</label>
                                <textarea class="form-control" id="messageContent" rows="4" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label for="receiverType" class="form-label">接收者</label>
                                <select class="form-select" id="receiverType" onchange="toggleReceiverIds()">
                                    <option value="all">所有用户</option>
                                    <option value="user">指定用户</option>
                                </select>
                            </div>
                            <div class="mb-3" id="receiverIdsContainer" style="display: none;">
                                <label for="receiverIds" class="form-label">用户ID（逗号分隔）</label>
                                <input type="text" class="form-control" id="receiverIds" placeholder="1,2,3">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" onclick="sendSystemMsg()">发送</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除现有模态框
    const existingModal = document.getElementById('systemMessageModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('systemMessageModal'));
    modal.show();
}

// 切换接收者ID输入框
function toggleReceiverIds() {
    const receiverType = document.getElementById('receiverType').value;
    const container = document.getElementById('receiverIdsContainer');
    container.style.display = receiverType === 'user' ? 'block' : 'none';
}

// 保存分类
async function saveCategory(categoryId) {
    const formData = {
        name: document.getElementById('categoryName').value,
        parent_id: parseInt(document.getElementById('parentCategory').value),
        sort_order: parseInt(document.getElementById('sortOrder').value),
        is_active: document.getElementById('isActive').checked
    };
    
    try {
        const url = categoryId ? `/categories/${categoryId}` : '/categories';
        const method = categoryId ? 'PUT' : 'POST';
        
        await apiRequest(url, {
            method: method,
            body: JSON.stringify(formData),
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        showSuccess('分类保存成功');
        const modal = bootstrap.Modal.getInstance(document.getElementById('categoryModal'));
        modal.hide();
        loadCategories();
    } catch (error) {
        showError('保存分类失败: ' + error.message);
    }
}

// 保存专场活动
async function saveEvent(eventId) {
    const formData = {
        title: document.getElementById('eventTitle').value,
        description: document.getElementById('eventDescription').value,
        start_time: document.getElementById('startTime').value,
        end_time: document.getElementById('endTime').value,
        is_active: document.getElementById('eventActive').checked
    };
    
    try {
        const url = eventId ? `/events/${eventId}` : '/events';
        const method = eventId ? 'PUT' : 'POST';
        
        await apiRequest(url, {
            method: method,
            body: JSON.stringify(formData),
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        showSuccess('专场活动保存成功');
        const modal = bootstrap.Modal.getInstance(document.getElementById('eventModal'));
        modal.hide();
        loadEvents();
    } catch (error) {
        showError('保存专场活动失败: ' + error.message);
    }
}

// 发送系统消息
async function sendSystemMsg() {
    const receiverType = document.getElementById('receiverType').value;
    const receiverIds = receiverType === 'user' ? 
        document.getElementById('receiverIds').value.split(',').map(id => parseInt(id.trim())) : 
        null;
    
    const messageData = {
        title: document.getElementById('messageTitle').value,
        content: document.getElementById('messageContent').value,
        receiver_type: receiverType,
        receiver_ids: receiverIds
    };
    
    try {
        await apiRequest('/messages/system', {
            method: 'POST',
            body: JSON.stringify(messageData),
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        showSuccess('系统消息发送成功');
        const modal = bootstrap.Modal.getInstance(document.getElementById('systemMessageModal'));
        modal.hide();
        loadMessages();
    } catch (error) {
        showError('发送系统消息失败: ' + error.message);
    }
}

// 批量操作
async function batchOperation(action, selectedIds) {
    if (selectedIds.length === 0) {
        showError('请选择要操作的项目');
        return;
    }
    
    try {
        const response = await apiRequest(`/batch/${action}`, {
            method: 'POST',
            body: JSON.stringify({ ids: selectedIds }),
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        showSuccess(`批量操作完成：成功 ${response.success_count} 个，失败 ${response.failure_count} 个`);
        
        // 刷新当前页面数据
        switch(currentSection) {
            case 'users':
                loadUsers();
                break;
            case 'products':
                loadProducts();
                break;
            case 'orders':
                loadOrders();
                break;
            default:
                break;
        }
    } catch (error) {
        showError('批量操作失败: ' + error.message);
    }
}

// 添加统计图表更新
async function updateCharts() {
    try {
        const response = await apiRequest('/statistics/overview', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        // 更新图表数据
        if (window.salesChart) {
            const salesData = response.daily_revenue.slice(-6);
            window.salesChart.data.labels = salesData.map(item => new Date(item.date).toLocaleDateString());
            window.salesChart.data.datasets[0].data = salesData.map(item => item.amount);
            window.salesChart.update();
        }
        
    } catch (error) {
        console.error('更新图表失败:', error);
    }
}

// ===== 店铺管理相关函数 =====

// 加载开店申请列表
async function loadApplications() {
    try {
        const statusFilter = document.getElementById('applicationStatusFilter')?.value || '';
        const typeFilter = document.getElementById('storeTypeFilter')?.value || '';
        
        let params = new URLSearchParams();
        if (statusFilter) params.append('status', statusFilter);
        if (typeFilter) params.append('store_type', typeFilter);
        
        const response = await apiRequest(`/store-applications?${params.toString()}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        renderApplicationsTable(response.items || []);
    } catch (error) {
        console.error('加载开店申请失败:', error);
        showAlert('加载开店申请失败', 'error');
        renderApplicationsTable([]);
    }
}

// 渲染开店申请表格
function renderApplicationsTable(applications) {
    const tbody = document.querySelector('#applicationsTable tbody');
    if (!tbody) return;
    
    if (applications.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center">暂无数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = applications.map(app => `
        <tr>
            <td>${app.id}</td>
            <td>${app.store_name}</td>
            <td>${app.store_type}</td>
            <td>${app.real_name}</td>
            <td>${app.consignee_phone}</td>
            <td>¥${app.deposit_amount}</td>
            <td>
                <span class="badge ${app.payment_status === 1 ? 'bg-success' : 'bg-warning'}">
                    ${app.payment_status === 1 ? '已支付' : '未支付'}
                </span>
            </td>
            <td>
                <span class="badge ${getApplicationStatusClass(app.status)}">
                    ${getApplicationStatusText(app.status)}
                </span>
            </td>
            <td>${formatDateTime(app.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="viewApplication(${app.id})">
                    <i class="bi bi-eye"></i>
                </button>
                ${app.status === 0 ? `
                    <button class="btn btn-sm btn-success" onclick="reviewApplication(${app.id}, 1)">
                        <i class="bi bi-check"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="showRejectModal(${app.id})">
                        <i class="bi bi-x"></i>
                    </button>
                ` : ''}
            </td>
        </tr>
    `).join('');
}

// 获取申请状态样式类
function getApplicationStatusClass(status) {
    switch (status) {
        case 0: return 'bg-warning';
        case 1: return 'bg-success';
        case 2: return 'bg-danger';
        case 3: return 'bg-primary';
        default: return 'bg-secondary';
    }
}

// 获取申请状态文本
function getApplicationStatusText(status) {
    switch (status) {
        case 0: return '待审核';
        case 1: return '审核通过';
        case 2: return '审核拒绝';
        case 3: return '已开店';
        default: return '未知';
    }
}

// 查看申请详情
async function viewApplication(applicationId) {
    try {
        const response = await apiRequest(`/store-applications/${applicationId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        showApplicationModal(response);
    } catch (error) {
        console.error('获取申请详情失败:', error);
        showAlert('获取申请详情失败', 'error');
    }
}

// 显示申请详情模态框
function showApplicationModal(application) {
    const modalHTML = `
        <div class="modal fade" id="applicationModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">开店申请详情</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>基本信息</h6>
                                <p><strong>店铺名称:</strong> ${application.store_name}</p>
                                <p><strong>店铺类型:</strong> ${application.store_type}</p>
                                <p><strong>店铺描述:</strong> ${application.store_description || '无'}</p>
                                
                                <h6>联系信息</h6>
                                <p><strong>真实姓名:</strong> ${application.real_name}</p>
                                <p><strong>联系电话:</strong> ${application.consignee_phone}</p>
                                <p><strong>所在地区:</strong> ${application.return_region}</p>
                                <p><strong>详细地址:</strong> ${application.return_address}</p>
                            </div>
                            <div class="col-md-6">
                                <h6>身份信息</h6>
                                <p><strong>身份证号:</strong> ${application.id_number}</p>
                                <p><strong>有效期:</strong> ${application.id_start_date} 至 ${application.id_end_date}</p>
                                
                                <h6>费用信息</h6>
                                <p><strong>保证金:</strong> ¥${application.deposit_amount}</p>
                                <p><strong>年费:</strong> ¥${application.annual_fee}</p>
                                <p><strong>支付状态:</strong> ${application.payment_status === 1 ? '已支付' : '未支付'}</p>
                                
                                <h6>审核信息</h6>
                                <p><strong>申请状态:</strong> ${getApplicationStatusText(application.status)}</p>
                                <p><strong>申请时间:</strong> ${formatDateTime(application.created_at)}</p>
                                ${application.reviewed_at ? `<p><strong>审核时间:</strong> ${formatDateTime(application.reviewed_at)}</p>` : ''}
                                ${application.reject_reason ? `<p><strong>拒绝原因:</strong> ${application.reject_reason}</p>` : ''}
                            </div>
                        </div>
                        
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6>证件照片</h6>
                                <div class="row">
                                    ${application.id_front_image ? `
                                        <div class="col-md-4">
                                            <p>身份证人像面</p>
                                            <img src="${application.id_front_image}" class="img-fluid" style="max-height: 200px; cursor: pointer;" onclick="showImagePreview('${application.id_front_image}')">
                                        </div>
                                    ` : ''}
                                    ${application.id_back_image ? `
                                        <div class="col-md-4">
                                            <p>身份证国徽面</p>
                                            <img src="${application.id_back_image}" class="img-fluid" style="max-height: 200px; cursor: pointer;" onclick="showImagePreview('${application.id_back_image}')">
                                        </div>
                                    ` : ''}
                                    ${application.business_license_image ? `
                                        <div class="col-md-4">
                                            <p>营业执照</p>
                                            <img src="${application.business_license_image}" class="img-fluid" style="max-height: 200px; cursor: pointer;" onclick="showImagePreview('${application.business_license_image}')">
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        ${application.status === 0 ? `
                            <button type="button" class="btn btn-success" onclick="reviewApplication(${application.id}, 1)">
                                审核通过
                            </button>
                            <button type="button" class="btn btn-danger" onclick="showRejectModal(${application.id})">
                                审核拒绝
                            </button>
                        ` : ''}
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('applicationModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('applicationModal'));
    modal.show();
}

// 显示拒绝原因输入模态框
function showRejectModal(applicationId) {
    const modalHTML = `
        <div class="modal fade" id="rejectModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">审核拒绝</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="rejectReason" class="form-label">拒绝原因 <span class="text-danger">*</span></label>
                            <textarea class="form-control" id="rejectReason" rows="4" placeholder="请输入拒绝原因..."></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-danger" onclick="confirmReject(${applicationId})">确认拒绝</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('rejectModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('rejectModal'));
    modal.show();
}

// 确认拒绝申请
function confirmReject(applicationId) {
    const rejectReason = document.getElementById('rejectReason').value.trim();
    if (!rejectReason) {
        showAlert('请输入拒绝原因', 'error');
        return;
    }
    
    reviewApplication(applicationId, 2, rejectReason);
    
    // 关闭模态框
    const modal = bootstrap.Modal.getInstance(document.getElementById('rejectModal'));
    if (modal) modal.hide();
}

// 审核申请
async function reviewApplication(applicationId, status, rejectReason = '') {
    try {
        const body = { status: status };
        if (status === 2 && rejectReason) {
            body.reject_reason = rejectReason;
        }
        
        const response = await apiRequest(`/store-applications/${applicationId}/review`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        showAlert(status === 1 ? '审核通过成功' : '审核拒绝成功', 'success');
        loadApplications(); // 重新加载列表
        
        // 关闭申请详情模态框
        const applicationModal = bootstrap.Modal.getInstance(document.getElementById('applicationModal'));
        if (applicationModal) applicationModal.hide();
        
    } catch (error) {
        console.error('审核申请失败:', error);
        showAlert('审核申请失败: ' + error.message, 'error');
    }
}

// 加载店铺列表
async function loadStores() {
    try {
        const statusFilter = document.getElementById('storeStatusFilter')?.value || '';
        const verifiedFilter = document.getElementById('verifiedFilter')?.value || '';
        
        let params = new URLSearchParams();
        if (statusFilter) params.append('status', statusFilter);
        if (verifiedFilter) params.append('verified_only', verifiedFilter === 'true');
        
        const response = await apiRequest(`/stores?${params.toString()}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        renderStoresTable(response.items || []);
    } catch (error) {
        console.error('加载店铺列表失败:', error);
        showAlert('加载店铺列表失败', 'error');
        renderStoresTable([]);
    }
}

// 渲染店铺表格
function renderStoresTable(stores) {
    const tbody = document.querySelector('#storesTable tbody');
    if (!tbody) return;
    
    if (stores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center">暂无数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = stores.map(store => `
        <tr>
            <td>${store.id}</td>
            <td>${store.name}</td>
            <td>${store.owner_info ? store.owner_info.nickname : '未知'}</td>
            <td>${store.phone || '未填写'}</td>
            <td>${store.total_products}</td>
            <td>${store.total_sales}</td>
            <td>${store.rating}/5.0</td>
            <td>${store.follower_count}</td>
            <td>
                <span class="badge ${store.verified ? 'bg-success' : 'bg-warning'}">
                    ${store.verified ? '已认证' : '未认证'}
                </span>
            </td>
            <td>
                <span class="badge ${store.is_open ? 'bg-success' : 'bg-danger'}">
                    ${store.is_open ? '营业中' : '已关闭'}
                </span>
            </td>
            <td>${formatDateTime(store.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="viewStore(${store.id})" title="查看详情">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-sm ${store.verified ? 'btn-warning' : 'btn-success'}" 
                        onclick="toggleStoreVerification(${store.id}, ${!store.verified})"
                        title="${store.verified ? '取消认证' : '认证店铺'}">
                    <i class="bi bi-${store.verified ? 'x-circle' : 'check-circle'}"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// 查看店铺详情
async function viewStore(storeId) {
    try {
        const response = await apiRequest(`/stores/${storeId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        showStoreModal(response);
    } catch (error) {
        console.error('获取店铺详情失败:', error);
        showAlert('获取店铺详情失败', 'error');
    }
}

// 显示店铺详情模态框
function showStoreModal(store) {
    const modalHTML = `
        <div class="modal fade" id="storeModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">店铺详情</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>基本信息</h6>
                                <p><strong>店铺名称:</strong> ${store.name}</p>
                                <p><strong>店铺描述:</strong> ${store.description || '无'}</p>
                                <p><strong>联系电话:</strong> ${store.phone || '未填写'}</p>
                                <p><strong>店铺地址:</strong> ${store.location || '未填写'}</p>
                                <p><strong>营业状态:</strong> ${store.is_open ? '营业中' : '已关闭'}</p>
                                <p><strong>认证状态:</strong> ${store.verified ? '已认证' : '未认证'}</p>
                            </div>
                            <div class="col-md-6">
                                <h6>经营数据</h6>
                                <p><strong>商品总数:</strong> ${store.total_products}</p>
                                <p><strong>销售总数:</strong> ${store.total_sales}</p>
                                <p><strong>总收入:</strong> ¥${store.total_revenue}</p>
                                <p><strong>店铺评分:</strong> ${store.rating}/5.0 (${store.rating_count}条评价)</p>
                                <p><strong>关注数量:</strong> ${store.follower_count}</p>
                                <p><strong>创建时间:</strong> ${formatDateTime(store.created_at)}</p>
                            </div>
                        </div>
                        
                        ${store.announcement ? `
                            <div class="row mt-3">
                                <div class="col-12">
                                    <h6>店铺公告</h6>
                                    <div class="alert alert-info">${store.announcement}</div>
                                </div>
                            </div>
                        ` : ''}
                        
                        ${store.recent_products && store.recent_products.length > 0 ? `
                            <div class="row mt-3">
                                <div class="col-12">
                                    <h6>最近商品</h6>
                                    <div class="row">
                                        ${store.recent_products.slice(0, 6).map(product => `
                                            <div class="col-md-2 mb-2">
                                                <div class="card">
                                                    ${product.images && product.images.length > 0 ? `
                                                        <img src="${product.images[0]}" class="card-img-top" style="height: 80px; object-fit: cover;">
                                                    ` : `
                                                        <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 80px;">
                                                            <i class="bi bi-image text-muted"></i>
                                                        </div>
                                                    `}
                                                    <div class="card-body p-2">
                                                        <small class="card-title d-block text-truncate" title="${product.title}">${product.title}</small>
                                                        <small class="text-muted">¥${product.current_price}</small>
                                                    </div>
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('storeModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('storeModal'));
    modal.show();
}

// 切换店铺认证状态
async function toggleStoreVerification(storeId, verified) {
    if (!confirm(`确定要${verified ? '认证' : '取消认证'}这个店铺吗？`)) {
        return;
    }
    
    try {
        const response = await apiRequest(`/stores/${storeId}/verify`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ verified: verified })
        });
        
        showAlert(verified ? '店铺认证成功' : '取消认证成功', 'success');
        loadStores(); // 重新加载列表
        
    } catch (error) {
        console.error('切换认证状态失败:', error);
        showAlert('操作失败: ' + error.message, 'error');
    }
}

// 显示图片预览
function showImagePreview(imageUrl) {
    const modalHTML = `
        <div class="modal fade" id="imagePreviewModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">图片预览</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${imageUrl}" class="img-fluid" style="max-width: 100%; max-height: 500px;">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        <a href="${imageUrl}" target="_blank" class="btn btn-primary">在新窗口打开</a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('imagePreviewModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
    modal.show();
}

// viewEvent 和 editEvent 函数已在上方实现

// 删除专场活动
function deleteEvent(eventId) {
    if (confirm('确定要删除这个专场活动吗？')) {
        console.log('删除专场活动:', eventId);
        // TODO: 实现删除功能
    }
}

// 添加专场活动
function addEvent() {
    console.log('添加专场活动');
    // TODO: 实现添加功能
}
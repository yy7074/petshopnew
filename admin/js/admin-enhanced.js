// 增强版后台管理系统JavaScript
// 全局变量
const API_BASE_URL = 'http://localhost:3000/api/v1';
let currentSection = 'dashboard';
let authToken = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadDashboardData();
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
        const response = await apiRequest('/admin/verify', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        if (response.valid) {
            hideAdminLogin();
        } else {
            showAdminLogin();
        }
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
async function adminLogin() {
    const username = document.getElementById('adminUsername').value;
    const password = document.getElementById('adminPassword').value;

    try {
        const response = await apiRequest('/admin/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.access_token) {
            authToken = response.access_token;
            localStorage.setItem('admin_token', authToken);
            hideAdminLogin();
            showSuccess('登录成功');
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
        case 'shops':
            loadShops();
            break;
        case 'events':
            loadEvents();
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
    try {
        const response = await apiRequest('/admin/dashboard/stats', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        // 更新统计数据
        document.getElementById('total-users').textContent = response.totalUsers.toLocaleString();
        document.getElementById('total-products').textContent = response.totalProducts.toLocaleString();
        document.getElementById('today-orders').textContent = response.todayOrders.toLocaleString();
        document.getElementById('today-revenue').textContent = '¥' + response.todayRevenue.toLocaleString();
        
    } catch (error) {
        console.error('加载仪表盘数据失败:', error);
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
        const response = await apiRequest('/admin/users', {
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
        const response = await apiRequest('/admin/products', {
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
        const response = await apiRequest('/admin/categories', {
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
        const response = await apiRequest('/admin/orders', {
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
        const response = await apiRequest('/admin/shops', {
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
        const response = await apiRequest('/admin/events', {
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
        const response = await apiRequest('/admin/messages', {
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
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API请求失败:', error);
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
function viewUser(userId) {
    // TODO: 实现用户详情查看
    console.log('查看用户:', userId);
}

function editUser(userId) {
    // TODO: 实现用户编辑
    console.log('编辑用户:', userId);
}

function deleteUser(userId) {
    if (confirm('确定要删除这个用户吗？')) {
        // TODO: 实现用户删除
        console.log('删除用户:', userId);
    }
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

function viewEvent(eventId) {
    // TODO: 实现专场活动详情查看
    console.log('查看专场活动:', eventId);
}

function editEvent(eventId) {
    // TODO: 实现专场活动编辑
    console.log('编辑专场活动:', eventId);
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
        const url = categoryId ? `/admin/categories/${categoryId}` : '/admin/categories';
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
        const url = eventId ? `/admin/events/${eventId}` : '/admin/events';
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
        await apiRequest('/admin/messages/system', {
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
        const response = await apiRequest(`/admin/batch/${action}`, {
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
        const response = await apiRequest('/admin/statistics/overview', {
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
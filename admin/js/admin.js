// 全局变量
const API_BASE_URL = 'http://localhost:8000/api';
let currentSection = 'dashboard';
let authToken = localStorage.getItem('admin_token') || null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    if (!authToken) {
        showLoginModal();
        return;
    }
    
    initCharts();
    loadDashboardData();
    loadCurrentAdminInfo();
});

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
        // 模拟API调用
        const stats = {
            totalUsers: 12345,
            totalProducts: 8967,
            todayOrders: 156,
            todayRevenue: 23456
        };
        
        // 更新统计数据
        document.getElementById('total-users').textContent = stats.totalUsers.toLocaleString();
        document.getElementById('total-products').textContent = stats.totalProducts.toLocaleString();
        document.getElementById('today-orders').textContent = stats.todayOrders.toLocaleString();
        document.getElementById('today-revenue').textContent = '¥' + stats.todayRevenue.toLocaleString();
        
    } catch (error) {
        console.error('加载仪表盘数据失败:', error);
    }
}

// 加载用户数据
async function loadUsers() {
    try {
        // 模拟用户数据
        const users = [
            {
                id: 1,
                username: 'user001',
                phone: '13800138001',
                email: 'user001@example.com',
                status: 1,
                created_at: '2024-01-15 10:30:00'
            },
            {
                id: 2,
                username: 'user002',
                phone: '13800138002',
                email: 'user002@example.com',
                status: 1,
                created_at: '2024-01-16 14:20:00'
            }
        ];
        
        const tbody = document.querySelector('#usersTable tbody');
        if (tbody) {
            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.phone}</td>
                    <td>${user.email}</td>
                    <td>
                        <span class="badge ${getStatusClass(user.status)}">
                            ${getStatusText(user.status)}
                        </span>
                    </td>
                    <td>${user.created_at}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})">
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
    }
}

// 加载商品数据
async function loadProducts() {
    try {
        // 模拟商品数据
        const products = [
            {
                id: 1,
                title: '可爱金毛幼犬',
                category: '宠物',
                seller: 'seller001',
                current_price: 2000.00,
                status: 2,
                created_at: '2024-01-15 10:30:00'
            },
            {
                id: 2,
                title: '热带鱼套装',
                category: '水族',
                seller: 'seller002',
                current_price: 150.00,
                status: 2,
                created_at: '2024-01-16 14:20:00'
            }
        ];
        
        const tbody = document.querySelector('#productsTable tbody');
        if (tbody) {
            tbody.innerHTML = products.map(product => `
                <tr>
                    <td>${product.id}</td>
                    <td>${product.title}</td>
                    <td>${product.category}</td>
                    <td>${product.seller}</td>
                    <td>¥${product.current_price.toFixed(2)}</td>
                    <td>
                        <span class="badge ${getProductStatusClass(product.status)}">
                            ${getProductStatusText(product.status)}
                        </span>
                    </td>
                    <td>${product.created_at}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editProduct(${product.id})">
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
    }
}

// 获取状态样式类
function getStatusClass(status) {
    const statusClasses = {
        1: 'status-active',
        2: 'status-inactive',
        3: 'status-banned'
    };
    return statusClasses[status] || 'status-inactive';
}

// 获取状态文本
function getStatusText(status) {
    const statusTexts = {
        1: '正常',
        2: '冻结',
        3: '禁用'
    };
    return statusTexts[status] || '未知';
}

// 获取商品状态样式类
function getProductStatusClass(status) {
    const statusClasses = {
        1: 'status-pending',
        2: 'status-active',
        3: 'status-inactive',
        4: 'status-banned'
    };
    return statusClasses[status] || 'status-inactive';
}

// 获取商品状态文本
function getProductStatusText(status) {
    const statusTexts = {
        1: '待审核',
        2: '拍卖中',
        3: '已结束',
        4: '已下架'
    };
    return statusTexts[status] || '未知';
}

// 编辑用户
function editUser(userId) {
    alert('编辑用户功能开发中...');
}

// 删除用户
function deleteUser(userId) {
    if (confirm('确定要删除这个用户吗？')) {
        alert('删除用户功能开发中...');
    }
}

// 编辑商品
function editProduct(productId) {
    alert('编辑商品功能开发中...');
}

// 删除商品
function deleteProduct(productId) {
    if (confirm('确定要删除这个商品吗？')) {
        alert('删除商品功能开发中...');
    }
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
    alert('错误: ' + message);
}

// 显示成功信息
function showSuccess(message) {
    alert('成功: ' + message);
}

// 退出登录
function logout() {
    if (confirm('确定要退出登录吗？')) {
        // 清除本地存储的token
        localStorage.removeItem('admin_token');
        authToken = null;
        
        // 显示退出成功消息
        showSuccess('退出登录成功');
        
        // 延迟一下再重新加载页面，让用户看到成功消息
        setTimeout(() => {
            // 重新加载页面，会触发登录检查
            window.location.reload();
        }, 1000);
    }
}

// 显示用户资料
function showProfile() {
    alert('管理员资料功能开发中...');
}

// 加载当前管理员信息
function loadCurrentAdminInfo() {
    // 这里可以从token中解析用户信息，或者调用API获取
    // 暂时显示默认的admin
    const adminSpan = document.getElementById('current-admin');
    if (adminSpan) {
        adminSpan.textContent = 'admin';
    }
}

// 显示登录模态框
function showLoginModal() {
    // 创建登录表单
    const loginModal = document.createElement('div');
    loginModal.innerHTML = `
        <div class="modal fade" id="loginModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">管理员登录</h5>
                    </div>
                    <div class="modal-body">
                        <form id="loginForm">
                            <div class="mb-3">
                                <label for="username" class="form-label">用户名</label>
                                <input type="text" class="form-control" id="username" value="admin" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">密码</label>
                                <input type="password" class="form-control" id="password" placeholder="请输入密码" required>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">登录</button>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <small class="text-muted">默认账号: admin, 密码: 123456</small>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(loginModal);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('loginModal'), {
        backdrop: 'static',
        keyboard: false
    });
    modal.show();
    
    // 绑定登录表单提交事件
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
}

// 处理登录
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showError('请输入用户名和密码');
        return;
    }
    
    try {
        // 这里应该调用实际的登录API
        // const response = await apiRequest('/v1/admin/login', {
        //     method: 'POST',
        //     body: JSON.stringify({ username, password })
        // });
        
        // 暂时模拟登录验证
        if (username === 'admin' && password === '123456') {
            // 模拟token
            const token = 'mock-admin-token-' + Date.now();
            localStorage.setItem('admin_token', token);
            authToken = token;
            
            // 关闭登录模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            modal.hide();
            
            // 移除模态框元素
            setTimeout(() => {
                const modalElement = document.getElementById('loginModal');
                if (modalElement) {
                    modalElement.remove();
                }
            }, 300);
            
            showSuccess('登录成功');
            
            // 初始化页面
            setTimeout(() => {
                initCharts();
                loadDashboardData();
                loadCurrentAdminInfo();
            }, 1000);
        } else {
            showError('用户名或密码错误');
        }
    } catch (error) {
        showError('登录失败: ' + error.message);
    }
}




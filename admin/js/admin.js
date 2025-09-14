// 全局变量
const API_BASE_URL = 'http://localhost:8000/api';
let currentSection = 'dashboard';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadDashboardData();
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




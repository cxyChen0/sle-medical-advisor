// API服务封装

const API_BASE_URL = 'http://127.0.0.1:8000';

// 通用请求函数
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // 只有当请求体不是FormData时才设置默认的Content-Type
  const defaultHeaders = {};
  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// 健康检查
export async function healthCheck() {
  return request('/health');
}

// 表单名称归一化
export async function normalizeTerms(terms) {
  return request('/normalize', {
    method: 'POST',
    body: JSON.stringify({ terms }),
  });
}

// 获取患者病史
export async function getMedicalHistory(patientId) {
  return request(`/medical-history/${patientId}`);
}

// 解析检查单
export async function parseReport(file, reportType) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('report_type', reportType);
  
  return request('/parse-report', {
    method: 'POST',
    headers: {}, // 不需要Content-Type，FormData会自动设置
    body: formData,
  });
}

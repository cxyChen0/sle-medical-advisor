import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  ChevronDown, 
  Upload, 
  BarChart3, 
  MessageCircle, 
  Settings, 
  Activity, 
  Users, 
  FileText, 
  CheckCircle, 
  Calendar, 
  Code, 
  BrainCircuit, 
  AlertCircle, 
  Loader2 
} from 'lucide-react'
import { healthCheck, parseReport, normalizeTerms } from '../services/api'

function Dashboard() {
  const location = useLocation()
  const [scrolled, setScrolled] = useState(false)
  const [file, setFile] = useState(null)
  const [reportType, setReportType] = useState('lab')
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [parseResult, setParseResult] = useState(null)
  const [systemStatus, setSystemStatus] = useState(null)
  const [checkingStatus, setCheckingStatus] = useState(false)
  const [normalizationResult, setNormalizationResult] = useState(null)
  const [normalizationError, setNormalizationError] = useState('')
  
  // 检查滚动状态，用于导航栏样式变化
  useEffect(() => {
    const handleScroll = () => {
      const offset = window.scrollY
      setScrolled(offset > 20)
    }
    
    window.addEventListener('scroll', handleScroll)
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])
  
  // 检查系统状态
  useEffect(() => {
    checkSystemStatus()
  }, [])
  
  // 检查系统状态函数
  const checkSystemStatus = async () => {
    setCheckingStatus(true)
    try {
      const response = await healthCheck()
      setSystemStatus(response.status === 'healthy')
    } catch (error) {
      setSystemStatus(false)
      console.error('System status check failed:', error)
    } finally {
      setCheckingStatus(false)
    }
  }
  
  // 文件上传处理函数
  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setUploadError('')
    setUploadSuccess(false)
    setParseResult(null)
  }
  
  // 上传文件函数
  const handleUpload = async () => {
    if (!file) {
      setUploadError('请选择文件')
      return
    }
    
    setUploading(true)
    setUploadError('')
    setUploadSuccess(false)
    
    try {
      console.log('Uploading file:', file.name, 'Report type:', reportType)
      const response = await parseReport(file, reportType)
      console.log('Upload success:', response)
      setParseResult(response)
      setUploadSuccess(true)
    } catch (error) {
      console.error('File upload failed:', error)
      setUploadError('文件上传失败，请重试')
    } finally {
      setUploading(false)
    }
  }
  
  // 测试表单归一化
  const testNormalization = async () => {
    try {
      const terms = ['ANA', '白细胞', '尿蛋白', 'C3补体', '抗dsDNA抗体']
      setNormalizationError('')
      const response = await normalizeTerms(terms)
      console.log('Normalization result:', response)
      setNormalizationResult(response)
    } catch (error) {
      console.error('Normalization test failed:', error)
      setNormalizationError('表单归一化测试失败')
    }
  }
  
  // 检查当前路径，用于导航栏高亮
  const isActive = (path) => {
    return location.pathname === path
  }
  
  return (
    <div>
      {/* 导航栏 */}
      <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
        <div className="navbar-container">
          <Link to="/dashboard" className="navbar-brand">
            <Activity className="h-6 w-6" />
            SLE智能辅助分析系统
          </Link>
          <ul className="navbar-links">
            <li><Link to="/dashboard" className={isActive('/dashboard') ? 'active' : ''}>首页</Link></li>
            <li><Link to="/visualization" className={isActive('/visualization') ? 'active' : ''}>数据可视化</Link></li>
            <li><Link to="/login">退出登录</Link></li>
          </ul>
        </div>
      </nav>

      {/* 主内容 */}
      <div className="container">
        <div className="page-header" style={{ margin: 'var(--spacing-xl) 0', textAlign: 'center' }}>
          <h1>欢迎使用SLE智能辅助分析系统</h1>
          <p className="text-gray-500">专业的系统性红斑狼疮辅助诊断与分析平台</p>
        </div>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: 'var(--spacing-lg)',
          marginBottom: 'var(--spacing-xl)'
        }}>
          {/* 功能卡片 */}
          <div className="card">
            <h3 className="card-title">
              <Upload className="h-5 w-5" />
              数据上传
            </h3>
            <div className="card-content">
              <p>上传患者检查报告单，系统将自动识别并分析数据，提供专业的诊断参考</p>
              
              <div style={{ marginTop: 'var(--spacing-md)' }}>
                <div style={{ marginBottom: 'var(--spacing-sm)' }}>
                  <label style={{ display: 'block', marginBottom: 'var(--spacing-xs)', fontWeight: '500' }}>选择文件</label>
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,.docx,.xlsx,.xls,.csv,.txt,.md"
                    onChange={handleFileChange}
                    style={{ padding: 'var(--spacing-sm)' }}
                  />
                  {file && (
                    <p style={{ marginTop: 'var(--spacing-xs)', fontSize: '0.9rem', color: 'var(--gray-600)' }}>
                      已选择: {file.name}
                    </p>
                  )}
                </div>
                
                <div style={{ marginBottom: 'var(--spacing-sm)' }}>
                  <label style={{ display: 'block', marginBottom: 'var(--spacing-xs)', fontWeight: '500' }}>报告类型</label>
                  <select
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                    style={{ 
                      width: '100%', 
                      padding: 'var(--spacing-sm)', 
                      border: '1px solid var(--gray-200)', 
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: 'white'
                    }}
                  >
                    <option value="lab">实验室检查</option>
                    <option value="pathology">病理检查</option>
                  </select>
                </div>
                
                <button
                  className="btn btn-primary"
                  onClick={handleUpload}
                  disabled={uploading}
                  style={{ 
                    width: '100%', 
                    marginTop: 'var(--spacing-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 'var(--spacing-xs)'
                  }}
                >
                  {uploading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      上传中...
                    </>
                  ) : (
                    '上传文件'
                  )}
                </button>
                
                {uploadError && (
                  <div style={{ 
                    marginTop: 'var(--spacing-sm)', 
                    padding: 'var(--spacing-sm)', 
                    backgroundColor: 'var(--error-light)', 
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--error-color)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-xs)'
                  }}>
                    <AlertCircle className="h-4 w-4" />
                    {uploadError}
                  </div>
                )}
                
                {uploadSuccess && parseResult && (
                  <div style={{ 
                    marginTop: 'var(--spacing-sm)', 
                    padding: 'var(--spacing-sm)', 
                    backgroundColor: 'var(--success-light)', 
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--success-color)'
                  }}>
                    <p>文件上传成功！</p>
                    <p style={{ marginTop: 'var(--spacing-xs)', fontSize: '0.9rem' }}>
                      患者ID: {parseResult.patient_id}
                    </p>
                    <p style={{ fontSize: '0.9rem' }}>
                      报告日期: {parseResult.report_date}
                    </p>
                    
                    {/* 显示归一化结果 */}
                    <div style={{ marginTop: 'var(--spacing-md)' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>归一化结果：</h4>
                      {parseResult.normalization_results && parseResult.normalization_results.length > 0 ? (
                        <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-sm)', padding: 'var(--spacing-sm)', backgroundColor: 'white' }}>
                          {parseResult.normalization_results.map((item, index) => (
                            <div key={index} style={{ marginBottom: 'var(--spacing-xs)', fontSize: '0.9rem' }}>
                              <span style={{ fontWeight: '500' }}>{item.original}</span>
                              <span style={{ margin: '0 var(--spacing-xs)', color: 'var(--gray-400)' }}>→</span>
                              <span style={{ color: 'var(--primary-color)' }}>{item.normalized}</span>
                              <span style={{ marginLeft: 'var(--spacing-xs)', fontSize: '0.8rem', color: 'var(--gray-500)' }}>(置信度: {Math.round(item.confidence * 100)}%)</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ 
                          padding: 'var(--spacing-sm)', 
                          backgroundColor: 'var(--gray-50)', 
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--gray-600)',
                          textAlign: 'center'
                        }}>
                          <p>未解析出任何医学指标，无法进行归一化处理</p>
                          <p style={{ fontSize: '0.8rem', marginTop: 'var(--spacing-xs)' }}>请上传包含医学检查指标的文件，如血常规、尿常规等检查单</p>
                        </div>
                      )}
                    </div>
                    
                    {/* 显示解析的指标 */}
                    <div style={{ marginTop: 'var(--spacing-md)' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>解析指标：</h4>
                      {parseResult.indicators && parseResult.indicators.length > 0 ? (
                        <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-sm)', padding: 'var(--spacing-sm)', backgroundColor: 'white' }}>
                          {parseResult.indicators.map((indicator, index) => (
                            <div key={index} style={{ marginBottom: 'var(--spacing-xs)', fontSize: '0.9rem' }}>
                              <span style={{ fontWeight: '500' }}>{indicator.name}</span>
                              {indicator.normalized_name && indicator.normalized_name !== indicator.name && (
                                <span style={{ margin: '0 var(--spacing-xs)', color: 'var(--gray-400)' }}>→</span>
                              )}
                              {indicator.normalized_name && indicator.normalized_name !== indicator.name && (
                                <span style={{ color: 'var(--primary-color)' }}>{indicator.normalized_name}</span>
                              )}
                              <span style={{ marginLeft: 'var(--spacing-xs)', color: 'var(--gray-600)' }}>{indicator.value}</span>
                              {indicator.unit && (
                                <span style={{ color: 'var(--gray-500)' }}> {indicator.unit}</span>
                              )}
                              {indicator.is_abnormal && (
                                <span style={{ marginLeft: 'var(--spacing-xs)', color: 'var(--error-color)' }}>(异常)</span>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ 
                          padding: 'var(--spacing-sm)', 
                          backgroundColor: 'var(--gray-50)', 
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--gray-600)',
                          textAlign: 'center'
                        }}>
                          <p>未解析出任何医学指标</p>
                          <p style={{ fontSize: '0.8rem', marginTop: 'var(--spacing-xs)' }}>请上传包含医学检查指标的文件，如血常规、尿常规等检查单</p>
                        </div>
                      )}
                    </div>
                    
                    {/* 显示原始文本 */}
                    {parseResult.original_text && (
                      <div style={{ marginTop: 'var(--spacing-md)' }}>
                        <h4 style={{ fontSize: '0.95rem', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>原始文本：</h4>
                        <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-sm)', padding: 'var(--spacing-sm)', backgroundColor: 'white', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                          <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{parseResult.original_text}</pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            <button
              onClick={testNormalization}
              className="btn btn-secondary"
              style={{ marginTop: 'var(--spacing-md)', display: 'inline-block' }}
            >
              测试表单归一化
            </button>
            
            {/* 显示测试表单归一化结果 */}
            {normalizationError && (
              <div style={{ 
                marginTop: 'var(--spacing-sm)', 
                padding: 'var(--spacing-sm)', 
                backgroundColor: 'var(--error-light)', 
                borderRadius: 'var(--radius-sm)',
                color: 'var(--error-color)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-xs)'
              }}>
                <AlertCircle className="h-4 w-4" />
                {normalizationError}
              </div>
            )}
            
            {normalizationResult && (
              <div style={{ marginTop: 'var(--spacing-md)' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>测试归一化结果：</h4>
                <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-sm)', padding: 'var(--spacing-sm)', backgroundColor: 'white' }}>
                  {normalizationResult.normalized_terms.map((item, index) => (
                    <div key={index} style={{ marginBottom: 'var(--spacing-xs)', fontSize: '0.9rem' }}>
                      <span style={{ fontWeight: '500' }}>{item.original}</span>
                      <span style={{ margin: '0 var(--spacing-xs)', color: 'var(--gray-400)' }}>→</span>
                      <span style={{ color: 'var(--primary-color)' }}>{item.normalized}</span>
                      <span style={{ marginLeft: 'var(--spacing-xs)', fontSize: '0.8rem', color: 'var(--gray-500)' }}>(置信度: {Math.round(item.confidence * 100)}%)</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <h3 className="card-title">
              <BarChart3 className="h-5 w-5" />
              数据分析
            </h3>
            <div className="card-content">
              <p>查看患者检查数据的异常指标和历史趋势，生成详细的分析报告</p>
            </div>
            <Link to="/visualization" className="btn btn-primary" style={{ marginTop: 'var(--spacing-lg)', display: 'inline-block' }}>
              查看分析
            </Link>
          </div>

          <div className="card">
            <h3 className="card-title">
              <MessageCircle className="h-5 w-5" />
              智能问答
            </h3>
            <div className="card-content">
              <p>针对SLE相关问题进行智能问答，获取专业建议和健康指导</p>
            </div>
            <Link to="#" className="btn btn-primary" style={{ marginTop: 'var(--spacing-lg)', display: 'inline-block' }}>
              开始问答
            </Link>
          </div>

          <div className="card">
            <h3 className="card-title">
              <Settings className="h-5 w-5" />
              系统设置
            </h3>
            <div className="card-content">
              <p>管理用户信息和系统配置，个性化您的使用体验</p>
            </div>
            <Link to="#" className="btn btn-primary" style={{ marginTop: 'var(--spacing-lg)', display: 'inline-block' }}>
              系统设置
            </Link>
          </div>
        </div>

        {/* 系统状态 */}
        <div className="card" style={{ marginTop: 'var(--spacing-xl)' }}>
          <h3 className="card-title">
            <Activity className="h-5 w-5" />
            系统状态
          </h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: 'var(--spacing-lg)',
            marginTop: 'var(--spacing-md)'
          }}>
            <div className="status-item" style={{ textAlign: 'center', padding: 'var(--spacing-md)', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)' }}>
              <Users className="h-5 w-5 mx-auto mb-2 text-primary" />
              <p className="text-sm text-gray-500">当前在线用户</p>
              <p className="text-xl font-semibold text-primary">1</p>
            </div>
            <div className="status-item" style={{ textAlign: 'center', padding: 'var(--spacing-md)', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)' }}>
              <FileText className="h-5 w-5 mx-auto mb-2 text-success" />
              <p className="text-sm text-gray-500">已分析报告</p>
              <p className="text-xl font-semibold text-success">12</p>
            </div>
            <div className="status-item" style={{ textAlign: 'center', padding: 'var(--spacing-md)', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)' }}>
              {checkingStatus ? (
                <>
                  <Loader2 className="h-5 w-5 mx-auto mb-2 text-primary animate-spin" />
                  <p className="text-sm text-gray-500">系统状态</p>
                  <p className="text-xl font-semibold text-primary">检查中...</p>
                </>
              ) : systemStatus === true ? (
                <>
                  <CheckCircle className="h-5 w-5 mx-auto mb-2 text-success" />
                  <p className="text-sm text-gray-500">系统状态</p>
                  <p className="text-xl font-semibold text-success">正常</p>
                </>
              ) : systemStatus === false ? (
                <>
                  <AlertCircle className="h-5 w-5 mx-auto mb-2 text-error" />
                  <p className="text-sm text-gray-500">系统状态</p>
                  <p className="text-xl font-semibold text-error">异常</p>
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm text-gray-500">系统状态</p>
                  <p className="text-xl font-semibold text-gray-400">未知</p>
                </>
              )}
            </div>
            <div className="status-item" style={{ textAlign: 'center', padding: 'var(--spacing-md)', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)' }}>
              <Calendar className="h-5 w-5 mx-auto mb-2 text-info" />
              <p className="text-sm text-gray-500">最近更新</p>
              <p className="text-xl font-semibold text-info">2026-02-10</p>
            </div>
            <div className="status-item" style={{ textAlign: 'center', padding: 'var(--spacing-md)', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)' }}>
              <Code className="h-5 w-5 mx-auto mb-2 text-info" />
              <p className="text-sm text-gray-500">版本号</p>
              <p className="text-xl font-semibold text-info">1.0.0</p>
            </div>
            <div className="status-item" style={{ textAlign: 'center', padding: 'var(--spacing-md)', backgroundColor: 'var(--gray-50)', borderRadius: 'var(--radius-md)' }}>
              <BrainCircuit className="h-5 w-5 mx-auto mb-2 text-warning" />
              <p className="text-sm text-gray-500">AI模块</p>
              <p className="text-xl font-semibold text-warning">未启用</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
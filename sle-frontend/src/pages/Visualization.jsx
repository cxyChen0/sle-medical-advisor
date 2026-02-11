import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import { Activity, BarChart3, Users, Search, Loader2, AlertCircle } from 'lucide-react'
import { getMedicalHistory } from '../services/api'

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

function Visualization() {
  const location = useLocation()
  const [scrolled, setScrolled] = useState(false)
  const [patientId, setPatientId] = useState('1')
  const [testType, setTestType] = useState('blood')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [medicalHistory, setMedicalHistory] = useState(null)
  const [chartData, setChartData] = useState(null)
  
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
  
  // 获取患者病史数据
  useEffect(() => {
    fetchMedicalHistory()
  }, [patientId])
  
  // 当测试类型变化时，更新图表数据
  useEffect(() => {
    if (medicalHistory) {
      updateChartData()
    }
  }, [medicalHistory, testType])
  
  // 获取患者病史函数
  const fetchMedicalHistory = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await getMedicalHistory(patientId)
      setMedicalHistory(response)
    } catch (err) {
      setError('获取患者病史失败，请重试')
      console.error('Failed to fetch medical history:', err)
    } finally {
      setLoading(false)
    }
  }
  
  // 更新图表数据
  const updateChartData = () => {
    if (!medicalHistory || !medicalHistory.medical_history) {
      setChartData(null)
      return
    }
    
    const history = medicalHistory.medical_history
    const labels = history.map((record, index) => (index + 1).toString())
    
    if (testType === 'blood') {
      // 血常规数据
      const whiteBloodCells = history.map(record => {
        if (record.lab_results && record.lab_results['白细胞计数']) {
          return parseFloat(record.lab_results['白细胞计数'])
        }
        return null
      })
      
      setChartData({
        labels,
        datasets: [
          {
            label: '白细胞计数',
            data: whiteBloodCells,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            tension: 0.1
          }
        ]
      })
    } else if (testType === 'urine') {
      // 尿常规数据
      const urineProtein = history.map(record => {
        if (record.lab_results && record.lab_results['尿蛋白']) {
          const value = record.lab_results['尿蛋白']
          if (value === '阳性' || value === '1+') return 1
          if (value === '2+') return 2
          if (value === '3+') return 3
          if (value === '4+') return 4
          return parseFloat(value) || 0
        }
        return 0
      })
      
      setChartData({
        labels,
        datasets: [
          {
            label: '尿蛋白',
            data: urineProtein,
            borderColor: 'rgb(53, 162, 235)',
            backgroundColor: 'rgba(53, 162, 235, 0.5)',
            tension: 0.1
          }
        ]
      })
    } else if (testType === 'autoantibody') {
      // 自身抗体数据
      const ana = history.map(record => {
        if (record.lab_results && record.lab_results['抗核抗体']) {
          const value = record.lab_results['抗核抗体']
          if (value === '阳性') return 1
          if (value === '阴性') return 0
          return 0
        }
        return 0
      })
      
      setChartData({
        labels,
        datasets: [
          {
            label: '抗核抗体',
            data: ana,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            tension: 0.1
          }
        ]
      })
    }
  }
  
  // 处理查询按钮点击
  const handleQuery = () => {
    fetchMedicalHistory()
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
          <h1>患者数据可视化</h1>
          <p className="text-gray-500">专业的系统性红斑狼疮患者数据趋势分析</p>
        </div>
        
        {/* 患者选择和测试类型选择 */}
        <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
          <h3 className="card-title">
            <Search className="h-5 w-5" />
            查询条件
          </h3>
          <div style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
              <label>患者ID:</label>
              <input
                type="text"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                style={{ padding: 'var(--spacing-sm)', width: '120px', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-sm)' }}
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
              <label>测试类型:</label>
              <select
                value={testType}
                onChange={(e) => setTestType(e.target.value)}
                style={{ padding: 'var(--spacing-sm)', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-sm)' }}
              >
                <option value="blood">血常规</option>
                <option value="urine">尿常规</option>
                <option value="autoantibody">自身抗体</option>
              </select>
            </div>
            <button 
              className="btn btn-primary"
              onClick={handleQuery}
              disabled={loading}
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  查询中...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4" />
                  查询
                </>
              )}
            </button>
          </div>
        </div>

        {/* 数据趋势图 */}
        <div className="card">
          <h3 className="card-title">
            <BarChart3 className="h-5 w-5" />
            患者历史趋势图（横轴为检查次数）
          </h3>
          <div className="chart-container">
            {loading ? (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '400px',
                gap: 'var(--spacing-md)'
              }}>
                <Loader2 className="h-8 w-8 text-primary animate-spin" />
                <p>加载数据中...</p>
              </div>
            ) : error ? (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '400px',
                gap: 'var(--spacing-md)',
                color: 'var(--error-color)'
              }}>
                <AlertCircle className="h-8 w-8" />
                <p>{error}</p>
              </div>
            ) : !chartData ? (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '400px'
              }}>
                <p>暂无数据</p>
              </div>
            ) : (
              <Line 
                data={chartData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                    title: {
                      display: true,
                      text: '患者检查指标趋势'
                    }
                  },
                  scales: {
                    x: {
                      title: {
                        display: true,
                        text: '检查次数'
                      }
                    },
                    y: {
                      title: {
                        display: true,
                        text: '指标值'
                      }
                    }
                  }
                }}
              />
            )}
          </div>
        </div>

        {/* 异常指标表格 */}
        <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
          <h3 className="card-title">
            <Users className="h-5 w-5" />
            异常指标记录
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 'var(--spacing-md)' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--gray-200)', backgroundColor: 'var(--gray-50)' }}>
                  <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--gray-700)' }}>检查次数</th>
                  <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--gray-700)' }}>检查日期</th>
                  <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--gray-700)' }}>异常指标</th>
                  <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--gray-700)' }}>数值</th>
                  <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--gray-700)' }}>参考范围</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="5" style={{ padding: 'var(--spacing-lg)', textAlign: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-sm)' }}>
                        <Loader2 className="h-4 w-4 text-primary animate-spin" />
                        <span>加载数据中...</span>
                      </div>
                    </td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan="5" style={{ padding: 'var(--spacing-lg)', textAlign: 'center', color: 'var(--error-color)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-sm)' }}>
                        <AlertCircle className="h-4 w-4" />
                        <span>{error}</span>
                      </div>
                    </td>
                  </tr>
                ) : !medicalHistory || !medicalHistory.medical_history ? (
                  <tr>
                    <td colSpan="5" style={{ padding: 'var(--spacing-lg)', textAlign: 'center' }}>
                      暂无数据
                    </td>
                  </tr>
                ) : (
                  medicalHistory.medical_history.map((record, recordIndex) => {
                    // 这里简单处理，实际应该根据参考范围判断异常值
                    const abnormalIndicators = [];
                    if (record.lab_results) {
                      for (const [key, value] of Object.entries(record.lab_results)) {
                        // 简单判断异常值的逻辑，实际应该根据具体指标的参考范围
                        if (key === '白细胞计数' && parseFloat(value) < 4.0) {
                          abnormalIndicators.push({ name: key, value, reference: '4.0-10.0' });
                        } else if (key === '尿蛋白' && (value === '阳性' || value === '1+' || value === '2+' || value === '3+' || value === '4+')) {
                          abnormalIndicators.push({ name: key, value, reference: '阴性' });
                        } else if (key === '抗核抗体' && value === '阳性') {
                          abnormalIndicators.push({ name: key, value, reference: '阴性' });
                        }
                      }
                    }
                    
                    if (abnormalIndicators.length === 0) {
                      return null;
                    }
                    
                    return abnormalIndicators.map((indicator, indicatorIndex) => (
                      <tr 
                        key={`${recordIndex}-${indicatorIndex}`}
                        style={{ 
                          borderBottom: '1px solid var(--gray-200)', 
                          transition: 'background-color var(--transition-normal)'
                        }}
                      >
                        <td style={{ padding: 'var(--spacing-md)' }}>{recordIndex + 1}</td>
                        <td style={{ padding: 'var(--spacing-md)' }}>{record.date}</td>
                        <td style={{ padding: 'var(--spacing-md)' }}>{indicator.name}</td>
                        <td style={{ padding: 'var(--spacing-md)', color: 'var(--error-color)', fontWeight: '500' }}>
                          {indicator.value}
                        </td>
                        <td style={{ padding: 'var(--spacing-md)' }}>{indicator.reference}</td>
                      </tr>
                    ));
                  }).filter(Boolean)
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Visualization

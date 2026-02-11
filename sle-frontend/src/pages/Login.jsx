import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // 简单的表单验证
    if (!formData.username || !formData.password) {
      setError('请输入用户名和密码')
      return
    }

    // 模拟登录请求
    console.log('登录请求:', formData)
    
    // 登录成功后跳转到仪表盘
    navigate('/dashboard')
  }

  return (
    <div className="form-container">
      <h1 className="form-title">SLE智能辅助分析系统</h1>
      <h2 className="form-title">登录</h2>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '15px' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">用户名</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="请输入用户名"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">密码</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="请输入密码"
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px', fontSize: '16px' }}>
          登录
        </button>
      </form>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <p>
          还没有账号？ <Link to="/register" className="link">立即注册</Link>
        </p>
        <p>
          <Link to="/reset-password" className="link">忘记密码？</Link>
        </p>
      </div>
    </div>
  )
}

export default Login
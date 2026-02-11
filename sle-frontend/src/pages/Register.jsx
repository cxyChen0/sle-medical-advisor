import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
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
    setError('')
    setSuccess('')

    // 表单验证
    if (!formData.username || !formData.password || !formData.confirmPassword) {
      setError('请填写所有字段')
      return
    }

    if (formData.password.length < 6) {
      setError('密码长度至少为6位')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }

    // 模拟注册请求
    console.log('注册请求:', formData)
    
    // 注册成功
    setSuccess('注册成功，请登录')
    
    // 3秒后跳转到登录页面
    setTimeout(() => {
      navigate('/login')
    }, 3000)
  }

  return (
    <div className="form-container">
      <h1 className="form-title">SLE智能辅助分析系统</h1>
      <h2 className="form-title">注册</h2>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '15px' }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ color: 'green', marginBottom: '15px' }}>
          {success}
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
            placeholder="请输入密码（至少6位）"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">确认密码</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="请再次输入密码"
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px', fontSize: '16px' }}>
          注册
        </button>
      </form>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <p>
          已有账号？ <Link to="/login" className="link">立即登录</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
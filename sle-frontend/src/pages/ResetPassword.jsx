import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function ResetPassword() {
  const [formData, setFormData] = useState({
    username: '',
    newPassword: '',
    confirmNewPassword: ''
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
    if (!formData.username || !formData.newPassword || !formData.confirmNewPassword) {
      setError('请填写所有字段')
      return
    }

    if (formData.newPassword.length < 6) {
      setError('新密码长度至少为6位')
      return
    }

    if (formData.newPassword !== formData.confirmNewPassword) {
      setError('两次输入的新密码不一致')
      return
    }

    // 模拟修改密码请求
    console.log('修改密码请求:', formData)
    
    // 修改密码成功
    setSuccess('密码修改成功，请登录')
    
    // 3秒后跳转到登录页面
    setTimeout(() => {
      navigate('/login')
    }, 3000)
  }

  return (
    <div className="form-container">
      <h1 className="form-title">SLE智能辅助分析系统</h1>
      <h2 className="form-title">修改密码</h2>
      
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
          <label htmlFor="newPassword">新密码</label>
          <input
            type="password"
            id="newPassword"
            name="newPassword"
            value={formData.newPassword}
            onChange={handleChange}
            placeholder="请输入新密码（至少6位）"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmNewPassword">确认新密码</label>
          <input
            type="password"
            id="confirmNewPassword"
            name="confirmNewPassword"
            value={formData.confirmNewPassword}
            onChange={handleChange}
            placeholder="请再次输入新密码"
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px', fontSize: '16px' }}>
          确认修改
        </button>
      </form>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <p>
          <Link to="/login" className="link">返回登录</Link>
        </p>
      </div>
    </div>
  )
}

export default ResetPassword
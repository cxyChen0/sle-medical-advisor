-- SLE 医疗顾问数据库表结构

-- 患者基本信息表
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_name VARCHAR(100) NOT NULL,
    gender ENUM('male', 'female') NOT NULL,
    birth_date DATE,
    contact_phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (patient_name),
    INDEX idx_contact (contact_phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 病史记录表
CREATE TABLE IF NOT EXISTS medical_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    record_date DATE NOT NULL,
    diagnosis TEXT,
    symptoms TEXT COMMENT 'JSON格式存储症状列表',
    doctor_name VARCHAR(100),
    hospital_name VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 检查单表
CREATE TABLE IF NOT EXISTS medical_reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    report_type ENUM('pathology', 'lab') NOT NULL COMMENT '病理报告/化验报告',
    report_date DATE NOT NULL,
    hospital_name VARCHAR(200),
    doctor_name VARCHAR(100),
    file_path VARCHAR(500) COMMENT '原始文件路径',
    parsed_data JSON COMMENT '解析后的检查数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, report_date),
    INDEX idx_type (report_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 检查指标表
CREATE TABLE IF NOT EXISTS lab_indicators (
    indicator_id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL,
    indicator_name VARCHAR(100) NOT NULL,
    indicator_value VARCHAR(100) NOT NULL,
    unit VARCHAR(50),
    reference_range VARCHAR(200),
    is_abnormal BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES medical_reports(report_id) ON DELETE CASCADE,
    INDEX idx_report (report_id),
    INDEX idx_name (indicator_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 用药记录表
CREATE TABLE IF NOT EXISTS medications (
    medication_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    medication_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 咨询记录表
CREATE TABLE IF NOT EXISTS consultations (
    consultation_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    consultation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    symptoms TEXT COMMENT 'JSON格式存储症状',
    questions TEXT COMMENT 'JSON格式存储咨询问答',
    advice TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, consultation_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

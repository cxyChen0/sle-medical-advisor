-- 常见病医疗顾问数据库扩展
-- 与SLE Medical Advisor共用MySQL数据库

-- 过敏记录表(新增)
CREATE TABLE IF NOT EXISTS allergies (
    allergy_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    allergen_type ENUM('drug', 'food', 'other') NOT NULL COMMENT '过敏原类型:药物/食物/其他',
    allergen_name VARCHAR(200) NOT NULL COMMENT '过敏原名称',
    severity ENUM('mild', 'moderate', 'severe') NOT NULL COMMENT '严重程度',
    symptoms TEXT COMMENT '过敏症状,JSON格式',
    diagnosed_date DATE COMMENT '确诊日期',
    notes TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient (patient_id),
    INDEX idx_type (allergen_type),
    INDEX idx_severity (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='患者过敏记录表';

-- 咨询分类表(新增,用于标记常见病咨询的类型)
CREATE TABLE IF NOT EXISTS consultation_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='咨询分类表';

-- 咨询记录表(新增字段)
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS category_id INT COMMENT '咨询分类ID';
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recommended_medications TEXT COMMENT '推荐的药品,JSON格式';
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS disease_diagnosis VARCHAR(200) COMMENT '初步诊断';
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS follow_up_status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending' COMMENT '随访状态';

-- 插入初始咨询分类数据
INSERT INTO consultation_categories (category_name, description) VALUES
('respiratory', '呼吸系统疾病:感冒、咳嗽、咽炎等'),
('digestive', '消化系统疾病:胃炎、腹泻、呕吐等'),
('neurological', '神经系统疾病:头痛、头晕等'),
('dermatological', '皮肤疾病:荨麻疹、湿疹等'),
('other', '其他疾病')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- 症状记录表(新增,用于存储详细症状)
CREATE TABLE IF NOT EXISTS symptom_records (
    symptom_id INT PRIMARY KEY AUTO_INCREMENT,
    consultation_id INT NOT NULL,
    symptom_category VARCHAR(50) NOT NULL COMMENT '症状分类',
    symptom_name VARCHAR(100) NOT NULL COMMENT '症状名称',
    severity ENUM('mild', 'moderate', 'severe') COMMENT '严重程度',
    duration_days INT COMMENT '持续天数',
    notes TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES consultations(consultation_id) ON DELETE CASCADE,
    INDEX idx_consultation (consultation_id),
    INDEX idx_category (symptom_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='症状记录表';

-- 药品推荐记录表(新增)
CREATE TABLE IF NOT EXISTS medication_recommendations (
    recommendation_id INT PRIMARY KEY AUTO_INCREMENT,
    consultation_id INT NOT NULL,
    medication_name VARCHAR(200) NOT NULL COMMENT '药品名称',
    generic_name VARCHAR(200) NOT NULL COMMENT '通用名',
    dosage TEXT COMMENT '推荐剂量',
    frequency TEXT COMMENT '用药频次',
    precautions TEXT COMMENT '注意事项',
    is_accepted BOOLEAN DEFAULT NULL COMMENT '患者是否接受',
    accepted_at TIMESTAMP NULL COMMENT '接受时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES consultations(consultation_id) ON DELETE CASCADE,
    INDEX idx_consultation (consultation_id),
    INDEX idx_medication (medication_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='药品推荐记录表';

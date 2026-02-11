"""
MySQL数据库连接器
用于连接SLE医疗顾问系统的MySQL数据库
"""

import mysql.connector
from mysql.connector import Error
import json
from typing import Dict, List, Optional
import os

# 数据库配置 - 从环境变量读取或使用默认值
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'sle_medical_advisor')
}


def get_db_connection():
    """
    获取数据库连接

    Returns:
        mysql.connector.connection: 数据库连接对象
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("成功连接到MySQL数据库")
            return conn
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None


def close_connection(conn):
    """
    关闭数据库连接

    Args:
        conn: 数据库连接对象
    """
    if conn and conn.is_connected():
        conn.close()
        print("数据库连接已关闭")


def execute_query(query: str, params: Optional[tuple] = None, fetch: bool = True) -> Optional[List[tuple]]:
    """
    执行SQL查询

    Args:
        query: SQL查询语句
        params: 查询参数
        fetch: 是否返回查询结果

    Returns:
        查询结果列表(如果fetch=True)
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)  # 使用字典游标
        cursor.execute(query, params)

        if fetch:
            result = cursor.fetchall()
            cursor.close()
            close_connection(conn)
            return result
        else:
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            close_connection(conn)
            return affected_rows

    except Error as e:
        print(f"查询执行错误: {e}")
        close_connection(conn)
        return None


def insert_record(table: str, data: Dict) -> Optional[int]:
    """
    插入记录到指定表

    Args:
        table: 表名
        data: 字段数据字典

    Returns:
        插入的记录ID,失败返回None
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        # 构建插入语句
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        cursor.execute(query, tuple(data.values()))
        conn.commit()

        record_id = cursor.lastrowid
        cursor.close()
        close_connection(conn)

        print(f"成功插入记录到 {table}, ID: {record_id}")
        return record_id

    except Error as e:
        print(f"插入记录错误: {e}")
        close_connection(conn)
        return None


def update_record(table: str, data: Dict, condition: str, params: tuple) -> bool:
    """
    更新记录

    Args:
        table: 表名
        data: 要更新的字段字典
        condition: WHERE条件
        params: 条件参数

    Returns:
        是否成功
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # 构建更新语句
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"

        all_params = tuple(data.values()) + params
        cursor.execute(query, all_params)
        conn.commit()

        affected_rows = cursor.rowcount
        cursor.close()
        close_connection(conn)

        print(f"成功更新 {affected_rows} 条记录")
        return affected_rows > 0

    except Error as e:
        print(f"更新记录错误: {e}")
        close_connection(conn)
        return False


def check_database_exists() -> bool:
    """
    检查数据库是否存在

    Returns:
        数据库是否存在
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (DB_CONFIG['database'],))
        result = cursor.fetchone()
        cursor.close()
        close_connection(conn)
        return result is not None

    except Error as e:
        print(f"检查数据库错误: {e}")
        close_connection(conn)
        return False


if __name__ == "__main__":
    # 测试数据库连接
    print("测试数据库连接...")
    conn = get_db_connection()
    if conn:
        print("连接成功!")
        close_connection(conn)
    else:
        print("连接失败!")

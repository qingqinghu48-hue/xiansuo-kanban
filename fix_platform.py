#!/usr/bin/env python3
"""
修复平台分类：将"抖音广告"改为"抖音"
用于一次性修复数据库中的平台分类问题
"""
import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'leads.db')

def fix_platform():
    if not os.path.exists(DB_FILE):
        print(f"数据库文件不存在: {DB_FILE}")
        return
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 查看当前分类
    print("修复前：")
    c.execute("SELECT DISTINCT platform, COUNT(*) as cnt FROM new_leads GROUP BY platform ORDER BY cnt DESC")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}条")
    
    # 1. 把"抖音广告"改为"抖音"
    c.execute("UPDATE new_leads SET platform = '抖音' WHERE platform = '抖音广告'")
    changed1 = c.rowcount
    
    # 2. 删除平台名异常（包含特殊字符或长度过长的记录）
    # 这些是错误数据，需要删除
    c.execute("SELECT phone, platform FROM new_leads WHERE LENGTH(platform) > 20 OR platform LIKE '%🤔%' OR platform LIKE '%？%'")
    bad_records = c.fetchall()
    if bad_records:
        print(f"\n发现 {len(bad_records)} 条异常记录：")
        for phone, plat in bad_records:
            print(f"  手机: {phone}, 平台: {plat}")
        # 删除这些异常记录
        c.execute("DELETE FROM new_leads WHERE LENGTH(platform) > 20 OR platform LIKE '%🤔%' OR platform LIKE '%？%'")
        changed2 = c.rowcount
        print(f"\n已删除 {changed2} 条异常记录")
    
    conn.commit()
    conn.close()
    
    print(f"\n已将 {changed1} 条'抖音广告'改为'抖音'")
    print("\n修复后请重启服务：pkill -f 'python3 server.py' && nohup python3 server.py > server.log 2>&1 &")

if __name__ == '__main__':
    fix_platform()

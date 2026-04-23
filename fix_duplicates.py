#!/usr/bin/env python3
"""清理数据库中的重复线索，保留最新的一条"""
import sqlite3
from datetime import datetime

DB_FILE = 'leads.db'

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# 查找重复的手机号
c.execute('''
    SELECT phone, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
    FROM new_leads
    GROUP BY phone
    HAVING COUNT(*) > 1
''')
duplicates = c.fetchall()

print(f"发现 {len(duplicates)} 个重复手机号")
total_deleted = 0

for phone, cnt, ids in duplicates:
    id_list = ids.split(',')
    # 保留最后一个（最新插入的），删除其他的
    keep_id = int(id_list[-1])
    delete_ids = id_list[:-1]
    
    print(f"  手机号 {phone}: {cnt}条, 保留id={keep_id}, 删除 {[int(x) for x in delete_ids]}")
    
    placeholders = ','.join(['?' for _ in delete_ids])
    c.execute(f'DELETE FROM new_leads WHERE id IN ({placeholders})', delete_ids)
    total_deleted += len(delete_ids)

conn.commit()

# 验证
c.execute('SELECT COUNT(*) FROM new_leads')
total = c.fetchone()[0]
c.execute('SELECT COUNT(DISTINCT phone) FROM new_leads')
unique = c.fetchone()[0]

print(f"\n清理完成！删除了 {total_deleted} 条重复记录")
print(f"当前总记录数: {total}, 唯一手机号: {unique}")

conn.close()

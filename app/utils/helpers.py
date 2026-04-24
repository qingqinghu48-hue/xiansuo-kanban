"""
工具函数
"""


def _clean_val(val):
    """清理字符串值，去除换行和回车，避免破坏 JSON/JS 格式"""
    if val is None:
        return ''
    s = str(val)
    s = s.replace('\r', ' ').replace('\n', ' ')
    return s.strip()


def _html_escape(val):
    """HTML 转义，防止 XSS"""
    if val is None:
        return ''
    s = str(val)
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    return s

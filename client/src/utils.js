export function splitRegions(val) {
  if (!val) return []
  return String(val).split(/[,，、]\s*/).map(s => s.trim()).filter(Boolean)
}

/**
 * 平台颜色系统
 */
const PLAT_PALETTE = ['#f43f5e','#f59e0b','#3b82f6','#10b981','#6366f1','#ec4899','#14b8a6','#f97316']
const platColorMap = {}
const platBgMap = {
  '#f43f5e': '#fee2e2', '#f59e0b': '#fef3c7', '#3b82f6': '#dbeafe', '#10b981': '#d1fae5',
  '#6366f1': '#ede9fe', '#ec4899': '#fce7f3', '#14b8a6': '#d1fae5', '#f97316': '#ffedd5'
}

export function platColor(p) {
  if (platColorMap[p]) return platColorMap[p]
  const keys = Object.keys(platColorMap)
  const c = PLAT_PALETTE[keys.length % PLAT_PALETTE.length]
  platColorMap[p] = c
  return c
}

export function platStyle(p) {
  const c = platColor(p)
  return { background: platBgMap[c] || '#f1f5f9', color: c }
}

/**
 * HTML 转义
 */
export function esc(s) {
  s = s == null ? '' : String(s)
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;')
}

export function splitRegions(val) {
  if (!val) return []
  return String(val).split(/[,，、]\s*/).map(s => s.trim()).filter(Boolean)
}

/**
 * 线索路由
 */
const express = require('express');
const db = require('../db');
const { requireAuth, requireAdmin } = require('../middleware/auth');
const { cleanVal, formatDateTime } = require('../utils/helpers');
const { parseExcel, findCol, getVal, parseDate } = require('../utils/excel');
const { getValidPlatforms, normalizePlatform } = require('../utils/platform');
const multer = require('multer');

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });

// 线索字段定义（数据库列名），新增字段只需修改此数组
const LEAD_FIELDS = [
  'phone', 'platform', 'agent', 'entry_date', 'name', 'city', 'region',
  'validity', 'can_wechat', 'remark',
  '二次联系时间', '二次联系备注', '最近一次电联时间', '到访时间', '签约时间',
  'xhs_account', 'flow_type',
  'is_duplicate', 'xhs_nickname', 'xhs_user_id', 'xhs_uid', 'source_note',
  'creative_name', 'creative_id', 'conversion_method', 'wechat_id', 'detail_json',
  'intention_type', 'intention_store', 'intention_store_id', 'follow_up_account',
  'latest_follow_note', 'lead_stage', 'lead_tags', 'call_count', 'marketing_type',
  'last_call_time', 'smart_intention', 'interaction_scene', 'latest_lead_record'
];

/**
 * 动态构建 INSERT SQL
 */
function buildInsertSql() {
  const fields = [...LEAD_FIELDS, 'created_at'];
  return `INSERT INTO new_leads (${fields.join(', ')}) VALUES (${fields.map(() => '?').join(', ')})`;
}

/**
 * 动态构建导入 UPDATE SQL（按 phone 匹配）
 */
function buildImportUpdateSql() {
  const sets = LEAD_FIELDS.map(f => `${f} = ?`).join(', ');
  return `UPDATE new_leads SET ${sets} WHERE phone = ?`;
}

/**
 * 从 SQLite 加载新录入线索
 * 返回格式与 Python 版一致：字段名用中文键名
 */
function loadNewLeads() {
  const rows = db.prepare('SELECT * FROM new_leads ORDER BY entry_date DESC, created_at DESC').all();
  const leads = [];
  for (const row of rows) {
    leads.push({
      id: row.id,
      '手机号': cleanVal(row.phone),
      '平台': cleanVal(row.platform),
      '所属招商': cleanVal(row.agent),
      '入库日期': cleanVal(row.entry_date),
      '创建时间': (cleanVal(row.created_at) || '').slice(0, 10),
      '姓名': cleanVal(row.name),
      '省份': cleanVal(row.city),
      '线索有效性': cleanVal(row.validity),
      '所属大区': cleanVal(row.region),
      '是否能加上微信': cleanVal(row.can_wechat),
      '备注': cleanVal(row.remark),
      '是否已读': row.is_read || 0,
      '二次联系时间': cleanVal(row['二次联系时间']),
      '二次联系备注': cleanVal(row['二次联系备注']),
      '最近一次电联时间': cleanVal(row['最近一次电联时间']),
      '到访时间': cleanVal(row['到访时间']),
      '签约时间': cleanVal(row['签约时间']),
      '小红书账号': cleanVal(row.xhs_account),
      '流量类型': cleanVal(row.flow_type),
      '来源文件': '手动录入',
      // 招商线索管理表扩展字段
      '是否重复': cleanVal(row.is_duplicate),
      // 小红书线索扩展字段
      '用户小红书昵称': cleanVal(row.xhs_nickname),
      '用户小红书ID': cleanVal(row.xhs_user_id),
      '用户ID': cleanVal(row.xhs_uid),
      '来源笔记': cleanVal(row.source_note),
      '创意名称': cleanVal(row.creative_name),
      '创意ID': cleanVal(row.creative_id),
      '转化方式': cleanVal(row.conversion_method),
      '微信号': cleanVal(row.wechat_id),
      '详情': cleanVal(row.detail_json),
      // 抖音客资扩展字段
      '意向线索': cleanVal(row.intention_type),
      '意向门店': cleanVal(row.intention_store),
      '意向门店ID': cleanVal(row.intention_store_id),
      '跟进户': cleanVal(row.follow_up_account),
      '最新跟进记录': cleanVal(row.latest_follow_note),
      '线索阶段': cleanVal(row.lead_stage),
      '线索标签': cleanVal(row.lead_tags),
      '线索拨打次数': row.call_count || 0,
      '营销类型': cleanVal(row.marketing_type),
      '最近拨打时间': cleanVal(row.last_call_time),
      '智能意向': cleanVal(row.smart_intention),
      '互动场景': cleanVal(row.interaction_scene),
      '最近留资记录': cleanVal(row.latest_lead_record),
    });
  }
  return leads;
}

// GET /api/leads
router.get('/api/leads', requireAuth, (req, res) => {
  try {
    const user = req.session.user;
    const newLeads = loadNewLeads();

    // 管理员和游客看全部
    if (user.role === 'admin' || user.role === 'guest') {
      return res.json({ records: newLeads, total: newLeads.length, new_leads_count: newLeads.length });
    }

    // 招商员只看自己分配的
    const agentName = user.name;
    const agentNewLeads = newLeads.filter(r => r['所属招商'] === agentName);
    const unread = agentNewLeads.filter(r => r['是否已读'] === 0).length;

    return res.json({
      records: agentNewLeads,
      total: agentNewLeads.length,
      role: 'agent',
      new_leads_count: agentNewLeads.length,
      unread_count: unread,
    });
  } catch (e) {
    console.error('[线索列表错误]', e);
    return res.status(500).json({ success: false, message: '获取线索列表失败: ' + e.message });
  }
});

// GET /api/agents — 返回所有招商员列表（去重排序）
router.get('/api/agents', requireAuth, (req, res) => {
  try {
    const rows = db.prepare("SELECT DISTINCT agent FROM new_leads WHERE agent IS NOT NULL AND agent != ? ORDER BY agent").all('');
    const agents = rows.map(r => r.agent).filter(Boolean);
    return res.json({ success: true, agents });
  } catch (e) {
    console.error('[招商员列表错误]', e);
    return res.status(500).json({ success: false, message: '获取招商员列表失败: ' + e.message });
  }
});

// POST /api/leads/add
router.post('/api/leads/add', requireAdmin, (req, res) => {
  try {
    const data = req.body;
    const phone = (data.phone || '').trim();
    const platform = (data.platform || '').trim();
    const agent = (data.agent || '').trim();
    const entryDate = (data.entry_date || '').trim() || new Date().toISOString().slice(0, 10);

    if (!phone || !platform || !agent) {
      return res.json({ success: false, message: '请填写完整信息' });
    }

    const existing = db.prepare('SELECT id FROM new_leads WHERE phone = ?').get(phone);
    if (existing) {
      return res.json({ success: false, message: '该手机号已录入' });
    }

    const now = formatDateTime();
    db.prepare('INSERT INTO new_leads (phone, platform, agent, entry_date, created_at) VALUES (?, ?, ?, ?, ?)')
      .run(phone, platform, agent, entryDate, now);

    return res.json({ success: true, message: '线索录入成功' });
  } catch (e) {
    console.error('[录入错误]', e);
    return res.json({ success: false, message: '录入失败: ' + e.message });
  }
});

// POST /api/leads/update
router.post('/api/leads/update', requireAuth, (req, res) => {
  try {
    const user = req.session.user;
    const data = req.body;
    const phone = (data.phone || '').trim();

    if (!phone) {
      return res.json({ success: false, message: '请提供手机号' });
    }

    const row = db.prepare('SELECT id, agent FROM new_leads WHERE phone = ?').get(phone);
    if (!row) {
      return res.json({ success: false, message: '线索不存在' });
    }

    const leadId = row.id;
    const leadAgent = row.agent;

    if (user.role !== 'admin' && leadAgent !== user.name) {
      return res.json({ success: false, message: '无权修改此线索' });
    }

    // 如果修改了手机号，检查是否与其他记录冲突
    const newPhone = (data['手机号'] || data.phone || '').trim();
    if (newPhone && newPhone !== phone) {
      const dup = db.prepare('SELECT id FROM new_leads WHERE phone = ?').get(newPhone);
      if (dup) {
        return res.json({ success: false, message: '已有重复线索，更新失败' });
      }
    }

    const name = data.name || '';
    const city = data.city || '';
    const validity = data.validity || '';
    const region = data.region || '';
    const canWechat = data.can_wechat || '';
    const remark = data.remark || '';
    const entryDate = data.entry_date || '';
    const contactTime = data['二次联系时间'] || '';
    const contactRemark = data['二次联系备注'] || '';
    const callTime = data['最近一次电联时间'] || '';
    const visitTime = data['到访时间'] || '';
    const signTime = data['签约时间'] || '';
    const platform = data.platform || '';
    const xhsAccount = data.xhs_account || '';
    const flowType = data.flow_type || data['流量类型'] || '';
    const xhsUserId = data.xhs_user_id || '';
    const agent = data.agent || '';

    if (user.role === 'admin') {
      db.prepare(`UPDATE new_leads SET
        phone = ?, name = ?, city = ?, validity = ?, region = ?, can_wechat = ?, remark = ?,
        platform = ?, entry_date = ?, 二次联系时间 = ?, 二次联系备注 = ?, 最近一次电联时间 = ?, 到访时间 = ?, 签约时间 = ?,
        xhs_account = ?, flow_type = ?, xhs_user_id = ?, agent = ?
        WHERE id = ?`).run(
        newPhone || phone, name, city, validity, region, canWechat, remark,
        platform, entryDate, contactTime, contactRemark, callTime, visitTime, signTime,
        xhsAccount, flowType, xhsUserId, agent, leadId
      );
    } else {
      db.prepare(`UPDATE new_leads SET
        phone = ?, name = ?, city = ?, validity = ?, region = ?, can_wechat = ?, remark = ?,
        二次联系时间 = ?, 二次联系备注 = ?, 最近一次电联时间 = ?, 到访时间 = ?, 签约时间 = ?,
        xhs_account = ?, flow_type = ?, xhs_user_id = ?
        WHERE id = ?`).run(
        newPhone || phone, name, city, validity, region, canWechat, remark,
        contactTime, contactRemark, callTime, visitTime, signTime,
        xhsAccount, flowType, xhsUserId, leadId
      );
    }

    return res.json({ success: true, message: '更新成功' });
  } catch (e) {
    console.error('[更新错误]', e);
    return res.json({ success: false, message: '更新失败: ' + e.message });
  }
});

// POST /api/leads/delete（仅管理员可删除）
router.post('/api/leads/delete', requireAdmin, (req, res) => {
  const user = req.session.user;
  const data = req.body;
  if (!data) {
    return res.json({ success: false, message: '请求数据为空' });
  }

  const leadId = data.id;
  const phone = String(data.phone || '').trim();

  if (!leadId && !phone) {
    return res.json({ success: false, message: '请提供id或手机号' });
  }

  try {
    let row;
    if (leadId) {
      row = db.prepare('SELECT id, agent FROM new_leads WHERE id = ?').get(leadId);
    } else {
      row = db.prepare('SELECT id, agent FROM new_leads WHERE phone = ?').get(phone);
    }

    if (!row) {
      return res.json({ success: false, message: '线索不存在或无法删除（仅支持删除手动录入的线索）' });
    }

    if (user.role !== 'admin' && row.agent !== user.name) {
      return res.json({ success: false, message: '无权删除此线索' });
    }

    db.prepare('DELETE FROM new_leads WHERE id = ?').run(row.id);
    return res.json({ success: true, message: '删除成功' });
  } catch (e) {
    console.error('[删除错误]', e);
    return res.json({ success: false, message: '删除出错: ' + e.message });
  }
});

// POST /api/leads/batch-delete（仅管理员可删除）
router.post('/api/leads/batch-delete', requireAdmin, (req, res) => {
  const user = req.session.user;
  const data = req.body;
  if (!data) {
    return res.json({ success: false, message: '请求数据为空' });
  }

  const phones = data.phones || [];
  if (!Array.isArray(phones) || phones.length === 0) {
    return res.json({ success: false, message: '请提供要删除的手机号列表' });
  }

  try {
    let deleted = 0;
    let skipped = 0;

    for (const p of phones) {
      const phone = String(p).trim();
      if (!phone) {
        skipped++;
        continue;
      }

      const row = db.prepare('SELECT id, agent FROM new_leads WHERE phone = ?').get(phone);
      if (!row) {
        skipped++;
        continue;
      }

      if (user.role !== 'admin' && row.agent !== user.name) {
        skipped++;
        continue;
      }

      db.prepare('DELETE FROM new_leads WHERE id = ?').run(row.id);
      deleted++;
    }

    return res.json({ success: true, message: `批量删除完成：成功 ${deleted} 条，跳过 ${skipped} 条` });
  } catch (e) {
    console.error('[批量删除错误]', e);
    return res.json({ success: false, message: '删除出错: ' + e.message });
  }
});

// POST /api/leads/mark_read
router.post('/api/leads/mark_read', requireAuth, (req, res) => {
  try {
    const data = req.body;
    const leadId = data.id;
    db.prepare('UPDATE new_leads SET is_read = 1 WHERE id = ?').run(leadId);
    return res.json({ success: true });
  } catch (e) {
    console.error('[标记已读错误]', e);
    return res.json({ success: false, message: '标记已读失败: ' + e.message });
  }
});

/**
 * 通用导入处理函数
 */
function handleImport(req, res) {
  if (!req.file) {
    return res.json({ success: false, message: '请选择文件' });
  }

  try {
    const filename = req.file.originalname;
    const df = parseExcel(req.file.buffer, filename);

    if (!df || df.length === 0) {
      return res.json({ success: false, message: 'Excel 文件为空（0行数据）' });
    }

    const cols = Object.keys(df[0]).map(c => String(c).trim());
    console.log(`[导入] 文件=${filename}, 行数=${df.length}, 列名=${cols.join(',')}`);

    // 智能识别列
    const phoneCol = findCol(cols, ['手机号', '手机号码', '电话', '联系电话', '手机', 'phone', '客户电话']);
    const weixinCol = findCol(cols, ['微信号', '微信', '微信账号']);
    const platformCol = findCol(cols, ['平台', '来源', '渠道', '来源平台', '线索来源']);
    const agentCol = findCol(cols, ['所属招商', '跟进员工', '负责人', '招商员', '员工', '分配']);
    const dateCol = findCol(cols, ['入库日期', '录入日期', '日期', '入库时间', '录入时间', '线索生成时间', '线索创建时间', '创建时间', '时间']);
    const xhsAccountCol = findCol(cols, ['归属账号', '小红书账号', '账号']);
    const leadTypeCol = findCol(cols, ['流量类型', '线索类型', '类型']);
    const nameCol = findCol(cols, ['姓名', '名字', '客户姓名', '联系人']);
    const cityCol = findCol(cols, ['城市', '省份', '地区', '所在城市', '省']);
    const regionCol = findCol(cols, ['所属大区', '大区', '区域']);
    const validityCol = findCol(cols, ['线索有效性', '有效性', '客户类型', '等级']);
    const wechatCol = findCol(cols, ['是否能加上微信', '能否加微', '加微信']);
    const remarkCol = findCol(cols, ['备注', '说明', '备注信息', '客户情况备注']);
    const followTimeCol = findCol(cols, ['二次联系时间', '跟进时间', '下次联系时间']);
    const followNoteCol = findCol(cols, ['二次联系备注', '跟进备注', '联系备注']);
    const callTimeCol = findCol(cols, ['最近一次电联时间', '电联时间', '最近联系时间']);
    const visitTimeCol = findCol(cols, ['到访时间', '到店时间', '来访时间']);
    const signTimeCol = findCol(cols, ['签约时间', '成交时间', '签约日期']);

    // 招商线索管理表特有列
    const isDuplicateCol = findCol(cols, ['是否重复', '重复']);

    // 小红书线索列表数据特有列
    const xhsNicknameCol = findCol(cols, ['用户小红书昵称', '小红书昵称', '昵称']);
    const xhsUserIdCol = findCol(cols, ['用户小红书ID', '小红书ID']);
    const xhsUidCol = findCol(cols, ['用户ID']);
    const sourceNoteCol = findCol(cols, ['来源笔记', '笔记']);
    const creativeNameCol = findCol(cols, ['创意名称', '创意']);
    const creativeIdCol = findCol(cols, ['创意ID', '创意id']);
    const conversionMethodCol = findCol(cols, ['转化方式', '转化']);
    const detailJsonCol = findCol(cols, ['详情', '详细信息']);

    // 抖音客资中心特有列（通用导入时也可能遇到）
    const intentionTypeCol = findCol(cols, ['意向线索', '线索意向']);
    const intentionStoreCol = findCol(cols, ['意向门店']);
    const intentionStoreIdCol = findCol(cols, ['意向门店ID', '意向门店id']);
    const followUpAccountCol = findCol(cols, ['跟进户']);
    const latestFollowNoteCol = findCol(cols, ['最新跟进记录']);
    const leadStageCol = findCol(cols, ['线索阶段', '阶段']);
    const leadTagsCol = findCol(cols, ['线索标签', '标签']);
    const callCountCol = findCol(cols, ['线索拨打次数', '拨打次数']);
    const marketingTypeCol = findCol(cols, ['营销类型']);
    const lastCallTimeCol = findCol(cols, ['最近拨打时间']);
    const smartIntentionCol = findCol(cols, ['智能意向']);
    const interactionSceneCol = findCol(cols, ['互动场景']);
    const latestLeadRecordCol = findCol(cols, ['最近留资记录']);

    if (!phoneCol) {
      return res.json({ success: false, message: `无法识别手机号列。当前列名: ${cols.join(',')}` });
    }

    console.log(`[导入] 列映射: 手机=${phoneCol}, 平台=${platformCol}, 招商=${agentCol}, 日期=${dateCol}`);

    // 文件类型判断
    const reqType = req.body.type || '';
    const isZhaoshang = filename.includes('招商') || reqType === 'zhaoshang';
    const isDouyinChannel = reqType === 'douyin';
    const isXhsChannel = reqType === 'xiaohongshu';
    const isDouyinKezi = filename.includes('客资') || (filename.includes('抖音') && !isZhaoshang);

    const parsed = [];
    const badRows = [];

    for (let idx = 0; idx < df.length; idx++) {
      const row = df[idx];
      const raw = row[phoneCol];
      const weixinRaw = weixinCol ? row[weixinCol] : undefined;

      let phone = '';
      if (raw !== undefined && raw !== null && raw !== '') {
        const s = String(raw).trim();
        const digits = s.replace(/\D/g, '');
        if (digits.length >= 7) {
          phone = digits;
        } else if (s.length >= 5) {
          phone = s;
        }
      } else if (weixinRaw !== undefined && weixinRaw !== null && weixinRaw !== '') {
        phone = String(weixinRaw).trim();
      }

      if (!phone) {
        badRows.push({ row: idx + 2, raw: String(raw), reason: '联系方式为空' });
        continue;
      }

      // 入库日期
      let entryDate = parseDate(row, dateCol);
      if (!entryDate) {
        for (const fc of ['日期', '时间', '创建日期', '添加日期', '线索创建时间']) {
          const col = findCol(cols, [fc]);
          if (col) {
            entryDate = parseDate(row, col);
            if (entryDate) break;
          }
        }
      }
      if (!entryDate) {
        entryDate = new Date().toISOString().slice(0, 10);
      }

      // 招商员分配
      let agent;
      if (isDouyinChannel || isDouyinKezi) {
        // 抖音/客资渠道：优先读取表格里的"跟进员工"列
        agent = getVal(row, findCol(cols, ['跟进员工'])) || getVal(row, agentCol) || '郑建军';
      } else if (isXhsChannel) {
        agent = getVal(row, agentCol) || '郑建军';
      } else {
        agent = getVal(row, findCol(cols, ['所属招商'])) || getVal(row, findCol(cols, ['跟进员工'])) || getVal(row, agentCol) || '郑建军';
      }

      let platform;
      if (isXhsChannel) {
        platform = '小红书';
      } else if (isDouyinChannel) {
        platform = '抖音';
      } else if (isZhaoshang) {
        // 招商线索管理表导入：平台标准化映射
        const rawPlatform = getVal(row, platformCol);
        const validPlatforms = getValidPlatforms();
        const normalized = normalizePlatform(rawPlatform, validPlatforms);
        if (!normalized) {
          badRows.push({
            row: idx + 2,
            raw: rawPlatform || '(空)',
            reason: `平台来源"${rawPlatform || '(空)'}"无法识别，有效平台：${validPlatforms.join('、')}`
          });
          continue;
        }
        platform = normalized;
      } else {
        // 通用导入：同样做平台标准化
        const rawPlatform = getVal(row, platformCol) || '抖音';
        const validPlatforms = getValidPlatforms();
        platform = normalizePlatform(rawPlatform, validPlatforms) || rawPlatform;
      }

      parsed.push({
        phone,
        platform,
        agent,
        entry_date: entryDate,
        name: getVal(row, nameCol),
        city: getVal(row, cityCol),
        region: getVal(row, regionCol),
        validity: getVal(row, validityCol),
        can_wechat: getVal(row, wechatCol),
        remark: getVal(row, remarkCol),
        '二次联系时间': parseDate(row, followTimeCol),
        '二次联系备注': getVal(row, followNoteCol),
        '最近一次电联时间': parseDate(row, callTimeCol),
        '到访时间': parseDate(row, visitTimeCol),
        '签约时间': parseDate(row, signTimeCol),
        xhs_account: isXhsChannel ? getVal(row, xhsAccountCol) : '',
        flow_type: getVal(row, leadTypeCol) || '',
        // 招商扩展字段
        is_duplicate: getVal(row, isDuplicateCol),
        // 小红书扩展字段
        xhs_nickname: isXhsChannel ? getVal(row, xhsNicknameCol) : '',
        xhs_user_id: isXhsChannel ? getVal(row, xhsUserIdCol) : '',
        xhs_uid: isXhsChannel ? getVal(row, xhsUidCol) : '',
        source_note: isXhsChannel ? getVal(row, sourceNoteCol) : '',
        creative_name: isXhsChannel ? getVal(row, creativeNameCol) : '',
        creative_id: isXhsChannel ? getVal(row, creativeIdCol) : '',
        conversion_method: isXhsChannel ? getVal(row, conversionMethodCol) : '',
        wechat_id: isXhsChannel ? getVal(row, weixinCol) : '',
        detail_json: isXhsChannel ? getVal(row, detailJsonCol) : '',
        // 抖音扩展字段（通用导入也可能遇到）
        intention_type: getVal(row, intentionTypeCol),
        intention_store: getVal(row, intentionStoreCol),
        intention_store_id: getVal(row, intentionStoreIdCol),
        follow_up_account: getVal(row, followUpAccountCol),
        latest_follow_note: getVal(row, latestFollowNoteCol),
        lead_stage: getVal(row, leadStageCol),
        lead_tags: getVal(row, leadTagsCol),
        call_count: (() => {
          const v = getVal(row, callCountCol);
          const n = parseInt(v, 10);
          return isNaN(n) ? 0 : n;
        })(),
        marketing_type: getVal(row, marketingTypeCol),
        last_call_time: parseDate(row, lastCallTimeCol),
        smart_intention: getVal(row, smartIntentionCol),
        interaction_scene: getVal(row, interactionSceneCol),
        latest_lead_record: getVal(row, latestLeadRecordCol),
      });
    }

    if (parsed.length === 0) {
      return res.json({ success: false, message: '未能解析出任何有效数据' });
    }

    console.log(`[导入] 解析成功: ${parsed.length} 条, 空值跳过: ${badRows.length} 条`);

    // 事务保护下的数据库写入
    const importTx = db.transaction((items, flags) => {
      const { isDouyinChannel, isXhsChannel, isZhaoshang } = flags;

      // 1) 清理已有重复
      const dupRows = db.prepare('SELECT phone, COUNT(*) as cnt FROM new_leads GROUP BY phone HAVING cnt > 1').all();
      for (const dr of dupRows) {
        db.prepare('DELETE FROM new_leads WHERE phone = ? AND id NOT IN (SELECT MIN(id) FROM new_leads WHERE phone = ?)').run(dr.phone, dr.phone);
      }

      // 2) 加载已有线索
      const existingRows = db.prepare('SELECT phone, platform, entry_date FROM new_leads').all();
      const existing = {};
      for (const er of existingRows) {
        existing[er.phone] = { platform: er.platform, entry_date: er.entry_date };
      }

      let added = 0, updated = 0, dupSkip = 0, skipped = 0;
      const seenInFile = new Set();
      const now = formatDateTime();

      const insertStmt = db.prepare(buildInsertSql());
      const updateStmt = db.prepare(buildImportUpdateSql());

      for (const item of items) {
        const phone = item.phone;
        if (seenInFile.has(phone)) {
          dupSkip++;
          continue;
        }
        seenInFile.add(phone);

        const platform = item.platform;
        const agent = item.agent;
        let entryDate = item.entry_date;

        if (existing[phone]) {
          const old = existing[phone];
          // 抖音/小红书渠道导入时，已存在的线索直接跳过
          if (isDouyinChannel || isXhsChannel) {
            skipped++;
            continue;
          }

          // 招商线索管理表导入时，若导入的平台是抖音/小红书，入库日期不变
          if (isZhaoshang && ((platform || '').includes('抖音') || (platform || '').includes('小红书'))) {
            entryDate = old.entry_date;
          }

          item.entry_date = entryDate;

          const values = LEAD_FIELDS.map(f => item[f] !== undefined ? item[f] : '');
          values.push(phone);
          updateStmt.run(...values);
          updated++;
        } else {
          // 招商线索管理表导入时，抖音/小红书的新线索不创建
          if (isZhaoshang && ((platform || '').includes('抖音') || (platform || '').includes('小红书'))) {
            skipped++;
            continue;
          }

          const values = LEAD_FIELDS.map(f => item[f] !== undefined ? item[f] : '');
          values.push(now);
          insertStmt.run(...values);
          added++;
          existing[phone] = { platform, entry_date: entryDate };
        }
      }

      return { added, updated, dupSkip, skipped };
    });

    const result = importTx(parsed, { isDouyinChannel, isXhsChannel, isZhaoshang });

    let msg = `导入完成！新增 ${result.added} 条，更新 ${result.updated} 条`;
    if (result.skipped) {
      if (isDouyinChannel || isXhsChannel) {
        msg += `，已存在线索跳过 ${result.skipped} 条`;
      } else {
        msg += `，抖音/小红书新线索跳过 ${result.skipped} 条（请通过渠道表格导入）`;
      }
    }
    if (result.dupSkip) {
      msg += `，Excel内重复跳过 ${result.dupSkip} 条`;
    }
    if (badRows.length) {
      msg += `，空值跳过 ${badRows.length} 条`;
    }

    return res.json({
      success: true,
      message: msg,
      added: result.added,
      updated: result.updated,
      dup_skip: result.dupSkip,
      bad: badRows.length,
      bad_rows: badRows.slice(0, 5),
    });
  } catch (e) {
    console.error(`[导入错误] ${e.message}\n${e.stack}`);
    return res.json({ success: false, message: `导入失败: ${e.message}` });
  }
}

// POST /api/leads/import
router.post('/api/leads/import', requireAdmin, upload.single('file'), handleImport);

// POST /api/leads/import-douyin — 复用通用导入逻辑
router.post('/api/leads/import-douyin', requireAdmin, upload.single('file'), (req, res) => {
  req.body.type = 'douyin';
  handleImport(req, res);
});

module.exports = router;
module.exports.loadNewLeads = loadNewLeads;

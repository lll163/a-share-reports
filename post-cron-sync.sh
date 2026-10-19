#!/bin/bash
# post-cron-sync.sh - 收盘/龙虎榜报告自动同步到 Hugo + GitHub Pages
# 用法：bash post-cron-sync.sh [closing|longhubang] YYYY-MM-DD
# 示例：bash post-cron-sync.sh closing 2026-10-19
#       bash post-cron-sync.sh longhubang 2026-10-19

set -e

REPORT_TYPE="${1:-closing}"
REPORT_DATE="${2:-$(date +%Y-%m-%d)}"

REPORTS_DIR="/root/.openclaw/workspace/memory/daily_reports"
HUGO_DIR="/root/a-share-reports"
SSH_KEY="/root/.ssh/id_ed25519_openclaw"

# 确定源文件和 Hugo 分类
if [ "$REPORT_TYPE" = "longhubang" ]; then
    SRC_FILE="${REPORTS_DIR}/${REPORT_DATE}-龙虎榜.md"
    HUGO_DIR_TYPE="longhubang"
    HUGO_CATEGORY="龙虎榜"
    HUGO_TAG="龙虎榜"
else
    SRC_FILE="${REPORTS_DIR}/${REPORT_DATE}.md"
    HUGO_DIR_TYPE="closing"
    HUGO_CATEGORY="复盘"
    HUGO_TAG="收盘复盘"
fi

# 检查源文件是否存在
if [ ! -f "$SRC_FILE" ]; then
    echo "ERROR: 报告文件不存在: $SRC_FILE"
    exit 1
fi

# 生成 Hugo frontmatter
TITLE="A股收盘复盘 ${REPORT_DATE}"
if [ "$REPORT_TYPE" = "longhubang" ]; then
    TITLE="游资龙虎榜 ${REPORT_DATE}"
fi

# 读取报告内容（跳过原始 markdown 标题）
CONTENT=$(sed '1{/^# /d}' "$SRC_FILE")

# 写入 Hugo 格式文件
HUGO_FILE_NAME="${REPORT_DATE}.md"
if [ "$REPORT_TYPE" = "longhubang" ]; then
    HUGO_FILE_NAME="${REPORT_DATE}-龙虎榜.md"
fi

OUT_FILE="${HUGO_DIR}/content/${HUGO_DIR_TYPE}/${HUGO_FILE_NAME}"

mkdir -p "${HUGO_DIR}/content/${HUGO_DIR_TYPE}"

cat > "$OUT_FILE" << EOF
---
title: "${TITLE}"
date: ${REPORT_DATE}T16:00:00+08:00
draft: false
categories: ["${HUGO_CATEGORY}"]
tags: ["${HUGO_TAG}"]
summary: "${REPORT_DATE} ${HUGO_CATEGORY}"
---

${CONTENT}
EOF

echo "✅ 生成: ${OUT_FILE}"

# Git commit + push
cd "$HUGO_DIR"
git add -A
git commit -m "auto-sync: ${REPORT_DATE} ${REPORT_TYPE} report" 2>/dev/null || echo "No new changes"
GIT_SSH_COMMAND="ssh -i ${SSH_KEY} -o IdentitiesOnly=yes" git push origin main 2>/dev/null

echo "✅ 已推送到 GitHub Pages: ${REPORT_DATE} ${HUGO_CATEGORY}"

#!/usr/bin/env python3
"""
自动生成 A 股复盘报告封面图 (SVG)
- 红色 = 涨，绿色 = 跌（A 股惯例）
- 显示：日期 + 上证涨跌 + 总成交额
"""

import os
import re
import glob

COVERS_DIR = "/root/a-share-reports/static/images/covers"
CONTENT_DIR = "/root/a-share-reports/content"

def extract_report_info(filepath):
    """从报告内容中提取关键数据"""
    with open(filepath) as f:
        content = f.read()
    
    # 提取日期
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filepath)
    date = date_match.group(1) if date_match else "未知日期"
    
    # 提取类型（收盘复盘 or 龙虎榜）
    is_longhubang = "龙虎榜" in filepath
    
    # 从内容提取上证指数涨跌幅
    sh_change = None
    total_volume = None
    
    # 匹配表格行中的上证指数数据
    sh_match = re.search(r'\| 上证指数 \|[^|]*\|[^|]*\| ([+-]?\d+\.?\d*)%', content)
    if sh_match:
        sh_change = float(sh_match.group(1))
    
    # 提取总成交额
    volume_match = re.search(r'总成交[^\d]*(\d+\.?\d*)万亿', content)
    if volume_match:
        total_volume = volume_match.group(1)
    
    return {
        "date": date,
        "is_longhubang": is_longhubang,
        "sh_change": sh_change,
        "total_volume": total_volume,
        "title": "游资龙虎榜" if is_longhubang else "A股收盘复盘",
    }

def generate_cover_svg(info, output_path):
    """生成封面 SVG"""
    date = info["date"]
    sh_change = info["sh_change"]
    total_volume = info["total_volume"]
    is_longhubang = info["is_longhubang"]
    
    # A 股颜色：涨=红，跌=绿
    if is_longhubang:
        main_color = "#ff6b35"  # 橙色（龙虎榜）
        bg_gradient_start = "#1a1a2e"
        bg_gradient_end = "#16213e"
        title = "🐉 游资龙虎榜"
        subtitle = date
    elif sh_change is not None:
        if sh_change > 0:
            main_color = "#ff3333"  # 红色 = 涨
            change_text = f"+{sh_change:.2f}%"
        elif sh_change < 0:
            main_color = "#00cc44"  # 绿色 = 跌
            change_text = f"{sh_change:.2f}%"
        else:
            main_color = "#ffaa00"  # 黄色 = 平
            change_text = "0.00%"
        bg_gradient_start = "#0f0f23"
        bg_gradient_end = "#1a1a3e"
        title = "📊 A股收盘复盘"
        subtitle = f"{date} | 上证 {change_text}"
        if total_volume:
            subtitle += f" | 成交 {total_volume}万亿"
    else:
        main_color = "#888888"
        bg_gradient_start = "#1a1a2e"
        bg_gradient_end = "#16213e"
        title = "📊 A股复盘"
        subtitle = date
    
    # 生成 SVG
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_gradient_start}"/>
      <stop offset="100%" style="stop-color:{bg_gradient_end}"/>
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="rgba(0,0,0,0.5)"/>
    </filter>
  </defs>
  
  <!-- 背景 -->
  <rect width="1200" height="630" fill="url(#bg)" rx="0"/>
  
  <!-- 装饰线条 -->
  <line x1="60" y1="120" x2="1140" y2="120" stroke="{main_color}" stroke-width="2" opacity="0.3"/>
  <line x1="60" y1="520" x2="1140" y2="520" stroke="{main_color}" stroke-width="1" opacity="0.2"/>
  
  <!-- 左上角装饰点 -->
  <circle cx="80" cy="80" r="6" fill="{main_color}" opacity="0.8"/>
  <circle cx="100" cy="80" r="6" fill="{main_color}" opacity="0.5"/>
  <circle cx="120" cy="80" r="6" fill="{main_color}" opacity="0.3"/>
  
  <!-- 标题 -->
  <text x="600" y="280" font-family="-apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="72" font-weight="bold" fill="white" text-anchor="middle" filter="url(#shadow)">
    {title}
  </text>
  
  <!-- 副标题/数据 -->
  <text x="600" y="370" font-family="-apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="36" fill="{main_color}" text-anchor="middle" opacity="0.9">
    {subtitle}
  </text>
  
  <!-- 底部装饰 -->
  <rect x="450" y="560" width="300" height="4" fill="{main_color}" rx="2" opacity="0.4"/>
</svg>'''
    
    with open(output_path, 'w') as f:
        f.write(svg)

def process_all_reports():
    """处理所有报告"""
    os.makedirs(COVERS_DIR, exist_ok=True)
    
    # 查找所有报告
    files = []
    for ext in ["closing", "longhubang"]:
        files.extend(glob.glob(f"{CONTENT_DIR}/{ext}/*.md"))
    
    files.sort()
    
    count = 0
    for filepath in files:
        info = extract_report_info(filepath)
        date = info["date"]
        filename = date + ("-龙虎榜" if info["is_longhubang"] else "") + ".svg"
        output_path = os.path.join(COVERS_DIR, filename)
        
        if os.path.exists(output_path):
            print(f"  跳过已存在: {filename}")
            continue
        
        generate_cover_svg(info, output_path)
        print(f"  ✅ {filename} | {info['title']} | 上证{'涨' if (info['sh_change'] or 0) > 0 else '跌'}")
        count += 1
    
    print(f"\n共生成 {count} 个封面")

if __name__ == "__main__":
    process_all_reports()

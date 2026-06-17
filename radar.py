import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import google.generativeai as genai
import json
import re

def run_radar():
    print("🚀 [雷达启动] 正在初始化全球智库RSS+网页双重并网版...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("PUBLISH_WEBHOOK_URL")
    
    if not gemini_key or not webhook_url:
        print("❌ [错误] 缺少必要密钥，请检查 GitHub Settings 里的 Secrets 配置！")
        return

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 🌐 顶尖财讯的多路由布局（网页爬取与官方RSS通道结合）
    urls = {
        "CNBC_Economy": {"type": "html", "url": "https://www.cnbc.com/economy/"},
        "Yahoo_Finance_Macro": {"type": "html", "url": "https://finance.yahoo.com/topic/economic-news/"},
        "Reuters_Financial": {"type": "html", "url": "https://www.reuters.com/markets/"},
        "WallStreet_CN": {"type": "html", "url": "https://wallstreetcn.com/news/global"},
        "MarketWatch_Macro": {"type": "html", "url": "https://www.marketwatch.com/economy-politics?mod=top_nav"}
    }

    combined_text = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    # 📥 阶段一：多源并网提取
    for name, config in urls.items():
        print(f"📡 [正在扫描] 目标入口: {name} ({config['type'].upper()})")
        try:
            res = requests.get(config["url"], headers=headers, timeout=20)
            if res.status_code != 200:
                print(f"⚠️ [跳过] {name} 状态码异常: {res.status_code}")
                continue
            
            # 路由 A：传统的 HTML 网页解析
            if config["type"] == "html":
                soup = BeautifulSoup(res.text, 'html.parser')
                page_text = " ".join([p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p'])])
                cleaned = " ".join(page_text.split())[:3500]
            
            # 路由 B：高级 RSS XML 绿色通道解析
            else:
                root = ET.fromstring(res.content)
                rss_items = []
                for item in root.findall('.//item')[:12]: # 提取最新的12条重磅快讯
                    title = item.find('title').text if item.find('title') is not None else ""
                    desc = item.find('description').text if item.find('description') is not None else ""
                    rss_items.append(f"Title: {title} | Summary: {desc}")
                cleaned = " \n".join(rss_items)

            if len(cleaned) > 150:
                combined_text += f"\n\n--- 来自权威媒体【{name}】的最新高价值情报块 ---\n{cleaned}"
                print(f"✅ [暂存成功] {name} 数据流已成功并入内存")
        except Exception as e:
            print(f"⚠️ [网络失联] 提取 {name} 失败: {e}")

    if len(combined_text) < 500:
        print("❌ [终止] 全网抓取到的有效宏观文本总量不足，本次巡航结束。")
        return

    # 🧠 阶段二：交给 AI 首席经济学家全盘析读
    system_prompt = (
        "你是一位专注于跨国供应链、全球宏观经贸政策与产融结合的首席经济学家。\n"
        "请评估以下从全球顶级财经媒体及官方RSS源合并抓取的英文文本。提取出真正具备战略震荡的重磅新闻（如美联储利率转向、Section 301/232关税变动、多边经贸博弈、跨国结汇异动、大宗原油及航运运力危机）。\n"
        "【输出格式限制】\n"
        "必须严格只返回一个标准的 JSON 数组（Array）列表，不要包含任何 markdown 标记（如 ```json ）。格式如下：\n"
        "[\n"
        "  {\"source\": \"具体媒体名\", \"score\": 数字打分, \"title\": \"一针见血的中文标题\", \"summary\": \"150字内中文逻辑摘要，切中供应链核心实质影响\"}\n"
        "]"
    )

    print("\n🤖 [大脑并网] 正在把全景情报大合集打包递给 Gemini 首席经济学家...")
    try:
        prompt_payload = f"{system_prompt}\n\n以下是全球多源财讯大合集：{combined_text}"
        response = model.generate_content(prompt_payload)
        ai_output = response.text.strip()
        
        # 剥离可能存在的 markdown 伪装
        json_match = re.search(r'(\[.*\]|\{.*\})', ai_output, re.DOTALL)
        clean_json_str = json_match.group(0) if json_match else ai_output
        
        parsed_data = json.loads(clean_json_str)
        news_list = parsed_data if isinstance(parsed_data, list) else [parsed_data]
        
        print(f"📊 [智库研判完毕] 本轮共筛选出 {len(news_list)} 条高价值宏观动态。")

        # 🚀 阶段三：循环定向投递
        for news in news_list:
            score = float(news.get("score", 0))
            title = news.get("title", "未命名重磅新闻")
            src = news.get("source", "未知全球媒体")
            
            if score >= 6.0: # 门槛线
                print(f"🔥 [高能预警] 发现重磅情报《{title}》(打分: {score}) 正在冲锋推送至 Make...")
                payload = {
                    "source": src,
                    "title": title,
                    "score": score,
                    "summary": news.get("summary", "无摘要"),
                    "origin_url": "[https://wallstreetcn.com](https://wallstreetcn.com)" if "WallStreet" in src else "[https://www.reuters.com](https://www.reuters.com)" if "Reuters" in src else "[https://www.marketwatch.com](https://www.marketwatch.com)" if "MarketWatch" in src else "[https://finance.yahoo.com](https://finance.yahoo.com)"
                }
                post_res = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"})
                print(f"🚀 [推送状态] Make 接收反馈码: {post_res.status_code}")
            else:
                print(f"🍃 [噪音过滤] 忽略低分动态: 《{title}》")

    except Exception as e:
        print(f"❌ [研判层异常]: {e}")

if __name__ == "__main__":
    run_radar()

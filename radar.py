import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import re

def run_radar():
    print("🚀 [雷达启动] 开始读取环境保护密钥...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("PUBLISH_WEBHOOK_URL")
    
    if not gemini_key or not webhook_url:
        print("❌ [错误] 缺少必要的环境变量，请检查 GitHub Settings 里的 Secrets 配置！")
        return

    # 1. 初始化 Google Gemini
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 2. 优化：重点保留容易抓取、且宏观密度极高的 5 个全局入口
    urls = {
        "Reuters_Macro": "https://www.reuters.com/markets/macro/",
        "Bloomberg_Markets": "https://www.bloomberg.com/markets",
        "CNBC_Economy": "https://www.cnbc.com/economy/",
        "MarketWatch_Latest": "https://www.marketwatch.com/latest-news",
        "Yahoo_Finance_Macro": "https://finance.yahoo.com/topic/economic-news/"
    }

    # 🌟 重新设计的硬核 Prompt：强力约束输出结构为单一的 JSON 列表 🌟
    system_prompt = (
        "你是一位专注于跨国供应链、全球宏观经贸政策与产融结合的首席经济学家。请评估以下从西方主流财经媒体主页抓取的英文文本。\n"
        "【筛选标准】\n"
        "1. 严格筛选美联储货币政策、地缘博弈、最新关税与制裁（如Section 301/232及2026地缘变动）、大宗商品与能源航运异动的重磅新闻。\n"
        "2. 跨国供应链有实质冲击的重大异动打 7.5 分以上；常规美股涨跌或普通企业公关打 3 分以下。\n"
        "【输出格式限制】\n"
        "如果有多条核心新闻，请务必将其组合封装进一个统一的 JSON 数组（Array）列表中返回。\n"
        "严格只返回一个标准的 JSON 结构，不要包含任何 markdown 标记（如 ```json ）。格式必须如下：\n"
        "[\n"
        "  {\"score\": 数字打分, \"title\": \"中文标题\", \"summary\": \"150字内一针见血的中文逻辑摘要\"},\n"
        "  {\"score\": 数字打分, \"title\": \"中文标题\", \"summary\": \"150字内一针见血的中文逻辑摘要\"}\n"
        "]"
    )

    for name, url in urls.items():
        print(f"\n📡 [正在扫描] 目标媒体: {name} | 网址: {url}")
        try:
            # 增强型请求头，尽量减少 403 拦截
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "[https://www.google.com/](https://www.google.com/)"
            }
            res = requests.get(url, headers=headers, timeout=20)
            
            if res.status_code in [401, 403]:
                print(f"⚠️ [反爬跳过] {name} 返回状态码 {res.status_code}，触发了高频墙，自动跳过。")
                continue
            elif res.status_code != 200:
                print(f"⚠️ [跳过] {name} 返回异常状态码 {res.status_code}")
                continue
            
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = " ".join([p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p'])])
            cleaned_text = " ".join(page_text.split())[:9000]

            if len(cleaned_text) < 200:
                print(f"⚠️ [数据过短] {name} 抓取到的有效文本过少。")
                continue

            prompt_payload = f"{system_prompt}\n\n以下是来自 {name} 的网页源数据：\n{cleaned_text}"
            response = model.generate_content(prompt_payload)
            
            ai_output = response.text.strip()
            print(f"🤖 [Gemini 回应原始文本]: \n{ai_output}")

            # 🛠️ 智能兼容：清洗出可能是数组 [ ... ] 或者是单对象 { ... } 的纯净 JSON
            json_match = re.search(r'(\[.*\]|\{.*\})', ai_output, re.DOTALL)
            if json_match:
                clean_json_str = json_match.group(0)
            else:
                clean_json_str = ai_output

            # 解析为 Python 对象
            parsed_data = json.loads(clean_json_str)
            
            # 统一转化为列表处理，兼容单条或多条返回
            news_list = parsed_data if isinstance(parsed_data, list) else [parsed_data]

            print(f"📊 [解析成功] 媒体: {name} | 共提取到 {len(news_list)} 条分析结果")

            # 🔄 循环检查并逐个把高分新闻砸向 Make 接收端
            for news in news_list:
                score = float(news.get("score", 0))
                title = news.get("title", "未命名重磅新闻")
                
                # 设置正式运行门槛为 5.0 分
                if score >= 5.0:
                    print(f"🔥 [高能预警] 发现重磅情报《{title}》(AI 评分: {score}) 正在打包推送...")
                    payload = {
                        "source": name,
                        "title": title,
                        "score": score,
                        "summary": news.get("summary", "无摘要"),
                        "origin_url": url
                    }
                    post_res = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"})
                    print(f"🚀 [推送状态] Make 响应码: {post_res.status_code}")
                else:
                    print(f"🍃 [过滤] 发现低分噪音《{title}》(AI 评分: {score})，自动忽略。")

        except Exception as e:
            print(f"❌ [系统错误] 扫描 {name} 时发生系统错误: {e}")

if __name__ == "__main__":
    run_radar()

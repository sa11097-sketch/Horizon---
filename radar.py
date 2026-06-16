import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

def run_radar():
    print("🚀 [雷达启动] 开始读取环境变量...")
    
    # 从 GitHub Secrets 中安全读取钥匙
    gemini_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("PUBLISH_WEBHOOK_URL")
    
    if not gemini_key or not webhook_url:
        print("❌ [错误] 缺少必要的环境变量，请检查 GitHub Settings 里的 Secrets 配置！")
        return

    # 1. 初始化 Google Gemini 大脑
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 2. 定向狙击：5家西方顶级财经与宏观主页
    urls = {
        "Reuters_Macro": "https://www.reuters.com/markets/macro/",
        "Bloomberg_Markets": "https://www.bloomberg.com/markets",
        "CNBC_Economy": "https://www.cnbc.com/economy/",
        "MarketWatch_Latest": "https://www.marketwatch.com/latest-news",
        "Yahoo_Finance_Macro": "https://finance.yahoo.com/topic/economic-news/"
    }

    # 全球宏观、跨国供应链与产融首席经济学家专属 Prompt
    system_prompt = (
        "你是一位专注于跨国供应链、全球宏观经贸政策与产融结合的首席经济学家。请评估以下从西方主流财经媒体主页抓取的英文文本。\n"
        "【筛选标准】\n"
        "1. 严格筛选关于美联储货币政策转向、多边经贸博弈、对华最新关税与制裁法案（如Section 301/232及2026最新地缘变动）、大宗商品与航运指数异动的核心新闻。\n"
        "2. 如果属于对企业跨国供应链有实质性冲击的重大宏观异动，打分必须在 7.5 分以上；常规美股个股涨跌或普通企业公关，一律打 3 分以下。\n"
        "【输出格式】\n"
        "请严格使用合法的纯 JSON 格式输出，不要包含任何 markdown 标记（如 ```json ），结构如下：\n"
        "{\"score\": 数字打分, \"title\": \"原新闻标题翻译成中文\", \"summary\": \"150字以内一针见血的中文逻辑摘要，切中供应链核心企业实质影响\"}"
    )

    for name, url in urls.items():
        print(f"\n📡 [正在扫描] 目标媒体: {name} | 网址: {url}")
        try:
            # 模拟浏览器行为敲门，防止被机房封锁
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            res = requests.get(url, headers=headers, timeout=15)
            
            if res.status_code != 200:
                print(f"⚠️ [跳过] {name} 返回状态码 {res.status_code}，可能触发了高频保护。")
                continue
            
            # 解析网页，扒出所有的标题和核心段落
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = " ".join([p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p'])])
            # 裁剪前 8000 个字符，防止 Token 溢出，足够提取首页头条
            cleaned_text = " ".join(page_text.split())[:8000]

            if len(cleaned_text) < 200:
                print(f"⚠️ [数据过短] {name} 抓取到的文本过少，可能被付费墙或反爬阻挡。")
                continue

            # 召唤 Gemini 进行深度战略洗稿与打分
            prompt_payload = f"{system_prompt}\n\n以下是来自 {name} 的网页源数据：\n{cleaned_text}"
            response = model.generate_content(prompt_payload)
            
            ai_output = response.text.strip()
            print(f"🤖 [Gemini 回应原始文本]: {ai_output}")

            # 解析大模型吐出来的 JSON
            import json
            # 移除可能存在的杂质字符
            if ai_output.startswith("```"):
                ai_output = ai_output.split("```")[1]
                if ai_output.startswith("json"):
                    ai_output = ai_output[4:]
            
            data = json.loads(ai_output.strip())
            score = data.get("score", 0)

            print(f"📊 [评估结果] 媒体: {name} | AI 评分: {score}")

            # 🎯 核心机制：只要分数达标，立刻一发入魂打向 Make
            if score >= 5.0:
                print(f"🔥 [高能预警] 分数 {score} 达标！正在打包推送至 Make Webhook...")
                payload = {
                    "source": name,
                    "title": data.get("title", "未命名重磅新闻"),
                    "score": score,
                    "summary": data.get("summary", "无摘要"),
                    "origin_url": url
                }
                # 发送 POST 请求给 Make
                post_res = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"})
                print(f"🚀 [推送状态] Make 响应码: {post_res.status_code}")
            else:
                print(f"🍃 [过滤] 分数低于5.0，自动忽略。")

        except Exception as e:
            print(f"❌ [异常] 扫描 {name} 时发生系统错误: {e}")

if __name__ == "__main__":
    run_radar()

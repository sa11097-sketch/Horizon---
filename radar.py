import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import re

def run_radar():
    print("🚀 [雷达启动] 正在初始化5合1低碳节能版宏观雷达...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("PUBLISH_WEBHOOK_URL")
    
    if not gemini_key or not webhook_url:
        print("❌ [错误] 缺少必要密钥，请检查 GitHub Settings 里的 Secrets 配置！")
        return

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 精选高价值、机房IP易穿透的全球宏观经贸高地
    urls = {
        "CNBC_Economy": "https://www.cnbc.com/economy/",
        "Yahoo_Finance_Macro": "https://finance.yahoo.com/topic/economic-news/",
        "MarketWatch_Economy": "https://www.marketwatch.com/economy-politics",
        "WSJ_Economy": "https://www.wsj.com/news/economy"
    }

    combined_text = ""
    
    # 📥 阶段一：全网联播抓取，进行内存大合并
    for name, url in urls.items():
        print(f"📡 [正在扫描] 目标入口: {name}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code != 200:
                print(f"⚠️ [跳过] {name} 状态码异常: {res.status_code}")
                continue
            
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = " ".join([p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p'])])
            cleaned = " ".join(page_text.split())[:3000] # 每家精简截取最核心的头条区
            
            if len(cleaned) > 200:
                combined_text += f"\n\n--- 来自媒体【{name}】的今日高价值数据块 ---\n{cleaned}"
                print(f"✅ [暂存成功] {name} 成功并网")
        except Exception as e:
            print(f"⚠️ [临时失联] 抓取 {name} 失败: {e}")

    if len(combined_text) < 500:
        print("❌ [终止] 全网抓取到的有效宏观文本过少，本次巡航结束。")
        return

    # 🧠 阶段二：单次消耗额度，调用大模型（每天可稳跑20次巡航）
    system_prompt = (
        "你是一位专注于跨国供应链、全球宏观经贸政策与产融结合的首席经济学家。\n"
        "请评估以下从全球主流财经媒体主页合并抓取的英文文本。提取出真正具备战略震荡的重磅新闻（如美联储利率、 Section 301/232关税异动、大宗原油暴跌、航运指数危机）。\n"
        "【输出格式限制】\n"
        "必须严格只返回一个标准的 JSON 数组（Array）列表，不要包含任何 markdown 标记（如 ```json ）。格式如下：\n"
        "[\n"
        "  {\"source\": \"媒体名\", \"score\": 数字打分, \"title\": \"一针见血的中文标题\", \"summary\": \"150字内中文逻辑摘要，切中供应链核心实质影响\"}\n"
        "]"
    )

    print("\n🤖 [大脑并网] 正在把大合集打包递给 Gemini 首席经济学家进行全盘析读...")
    try:
        prompt_payload = f"{system_prompt}\n\n以下是全球多源财讯大合集：{combined_text}"
        response = model.generate_content(prompt_payload)
        ai_output = response.text.strip()
        
        # 强力剥离外壳
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
            
            if score >= 5.0: # 门槛线
                print(f"🔥 [高能预警] 发现高价值情报《{title}》(打分: {score}) 正在冲锋推送至 Make...")
                payload = {
                    "source": src,
                    "title": title,
                    "score": score,
                    "summary": news.get("summary", "无摘要"),
                    "origin_url": urls.get(src, "[https://finance.yahoo.com](https://finance.yahoo.com)")
                }
                post_res = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"})
                print(f"🚀 [推送状态] Make 接收反馈码: {post_res.status_code}")
            else:
                print(f"🍃 [噪音过滤] 忽略低分动态: 《{title}》")

    except Exception as e:
        print(f"❌ [研判层异常]: {e}")

if __name__ == "__main__":
    run_radar()

import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import time
import random

def run_radar():
    print("🚀 [雷达启动] 正在初始化全球智库全线并网（高阶穿透与额度精算版）...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ [错误] 缺少必要密钥，请检查 GitHub Settings 里的 Secrets 配置！")
        return

    genai.configure(api_key=gemini_key)
    # 🌟 额度精算：继续锁死高性价比、极速响应的 2.5-flash 核心
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 1. 深度伪装请求头，规避 403 防火墙拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

    combined_text = ""

    # ==========================================
    # 🗺️ 管道 A：华尔街见闻核心 API 接口深度对接
    # ==========================================
    print("📡 [专属管道] 正在直连华尔街见闻原生数据流 API...")
    try:
        wscn_api = "https://api-prod.wallstreetcn.com/apiv1/content/fabric/articles?channel=global&limit=10"
        res = requests.get(wscn_api, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            articles = data.get("data", {}).get("items", [])
            wscn_chunk = ""
            for art in articles:
                title = art.get("title", "")
                summary = art.get("content_short", "")
                wscn_chunk += f" 标题:{title} | 简述:{summary};"
            combined_text += f"\n【华尔街见闻核心动态】{wscn_chunk[:1500]}"
            print("✅ 华尔街见闻 API 数据突围并网成功！")
    except Exception as e:
        print(f"⚠️ [跳过] 华尔街见闻 API 异常: {e}")

    # ==========================================
    # 🗺️ 管道 B：西方顶尖财经媒体矩阵（高阶防爬伪装）
    # ==========================================
    western_medias = {
        "CNBC_Economy": "https://www.cnbc.com/economy/",
        "Reuters_Financial": "https://www.reuters.com/markets/",
        "MarketWatch_Macro": "https://www.marketwatch.com/economy-politics",
        "Financial_Times_Global": "https://finance.yahoo.com/m/news/financial-times/", # 穿透并网：通过 Yahoo 节点高维复刻 FT 的高管必读讯息
        "Bloomberg_Insight": "https://finance.yahoo.com/bonds" # 战略性加装：彭博社宏观债市与结汇异动雷达
    }

    for name, url in western_medias.items():
        print(f"📡 [正在穿透] 目标堡垒: {name}")
        try:
            # 引入微调反爬：添加随机延迟，降低云服务器特征
            time.sleep(random.uniform(1.0, 2.5))
            res = requests.get(url, headers=headers, timeout=20)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # 极限初筛：只抽干 h1, h2, h3 和段落，控住入厂体积
                page_text = " ".join([p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p'])])
                # 严控单源 Input Token，把废话和噪声锁死在外
                cleaned = " ".join(page_text.split())[:1500]
                
                if len(cleaned) > 150:
                    combined_text += f"\n【源:{name}】{cleaned}"
                    print(f"✅ {name} 全球情报截流成功！")
            else:
                print(f"⚠️ [状态异常] {name} 返回状态码: {res.status_code}，已启动后备拦截保护。")
        except Exception as e:
            print(f"⚠️ [网络限制] {name} 提取受阻: {e}")

    # ==========================================
    # 🧠 🧠 阶段三：精打细算 · 单次打包递交决策脑
    # ==========================================
    if len(combined_text) < 400:
        print("❌ [终止] 原材料并网总量未达战略基准线，本次巡航熔断，保护 AI 额度。")
        return

    # 深度精算提示词：强制 AI 砍掉所有过场废话，提高信息密度，压榨每一粒 Output Token
    system_prompt = (
        "你是一位专注于跨国供应链安全、地缘经贸博弈与产融结合方向的顶级首席经济学家。\n"
        "请全盘析读以下由多源并网雷达高密度压缩后的英中文财经原材料。剔除垃圾噪声，提取出真正具备战略震荡、会穿透到外贸关税、结汇汇率或大宗运输的重磅头条。\n"
        "【极其严格的铁律】\n"
        "1. 不要带有任何 ```html 等 Markdown 代码壳，直接输出最纯粹、能被邮件客户端完美解析的 HTML 正文代码。\n"
        "2. 字数必须精练，直击要害。拒绝一切背景空话、套话、客套过渡句。将所有提炼出来的新闻合并在同一封信中输出。结构如下：\n"
        "<h3>【高管决策内参 · 全球经贸雷达日报】</h3>\n"
        "<hr>\n"
        "<b>【重磅战略动向】中文核心标题</b> (情报源: xxx)<br>\n"
        "<b>核心实质影响与产融研判：</b>120字内一针见血直接指出对供应链安全、关税政策或结汇层面的穿透性影响。<br>\n"
        "<hr>"
    )

    print("\n🤖 [大脑析读] 正在全盘合并调阅 Gemini 首席经济学家（已启用多源合拢节约模式）...")
    try:
        prompt_payload = f"{system_prompt}\n\n【多源高密情报合集（绝无RSS）】\n{combined_text}"
        response = model.generate_content(prompt_payload)
        ai_output = response.text.strip()
        
        # 深度清洗，确保文件纯净
        clean_html = ai_output.replace("```html", "").replace("```", "").strip()
        
        # 写入本地文件，供给 GitHub Actions 直接读取发送
        with open("email_content.html", "w", encoding="utf-8") as f:
            f.write(clean_html)
        print("✅ [本地打包完成] 智库级总合并长信已完美封印至 email_content.html 容器！")

    except Exception as e:
        print(f"❌ [智能体研判异常]: {e}")

if __name__ == "__main__":
    run_radar()

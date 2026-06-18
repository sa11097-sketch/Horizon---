import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

def run_radar():
    print("🚀 [雷达启动] 正在初始化全球智库极简闭合版（精打细算控流版）...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ [错误] 缺少必要密钥，请检查 GitHub Settings 里的 Secrets 配置！")
        return

    genai.configure(api_key=gemini_key)
    # 🌟 额度精算核心：使用性价比极高的 2.5-flash 模型，速度极快且极省 Token
    model = genai.GenerativeModel('gemini-2.5-flash')

    urls = {
        "CNBC_Economy": "https://www.cnbc.com/economy/",
        "Yahoo_Finance_Macro": "https://finance.yahoo.com/topic/economic-news/",
        "Reuters_Financial": "https://www.reuters.com/markets/",
        "WallStreet_CN": "https://wallstreetcn.com/news/global",
        "MarketWatch_Macro": "https://www.marketwatch.com/economy-politics?mod=top_nav"
    }

    combined_text = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # 📥 阶段一：前端严控入口（初筛与极限压缩）
    for name, url in urls.items():
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # 仅提取标题和段落文本，彻底抛弃网页无关广告和干扰标签
                page_text = " ".join([p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p'])])
                # 极简正则：压缩连续空格，且严格限制单源最大入厂字数（控住 Input Token）
                cleaned = " ".join(page_text.split())[:1800] 
                
                if len(cleaned) > 100:
                    combined_text += f"\n【源:{name}】{cleaned}"
        except Exception as e:
            print(f"⚠️ [跳过] {name} 抓取受限: {e}")

    if len(combined_text) < 300:
        print("❌ [终止] 有效原材料总量不足，本次巡航结束。")
        return

    # 🧠 阶段二：合并请求（单次总攻，拒绝重复计费）
    # 在提示词中剥离一切客套话，让 AI 直接出干货，压缩 Output Token
    system_prompt = (
        "你是一位跨国供应链与全球宏观经贸政策领域的顶级专家。\n"
        "请对以下合并抓取的英文文本进行全面审视，严格筛选出真正具备战略震荡、影响供应链安全、关税政策或大宗结汇的重磅新闻。\n"
        "【严格格式要求】\n"
        "1. 不要带有任何 ```html 等 Markdown 伪装，直接输出最纯粹的 HTML 代码片段。\n"
        "2. 字数精炼，一针见血，去掉所有背景废话，多条新闻并在一封信中输出。结构如下：\n"
        "<h3>【高管决策内参 · 全球经贸雷达日报】</h3>\n"
        "<hr>\n"
        "<b>【重磅】具体中文核心标题</b> (来源: xxx)<br>\n"
        "<b>核心实质影响：</b>120字内直接指出对跨国贸易及供应链的穿透性影响。<br>\n"
        "<hr>"
    )

    print("🤖 [大脑析读] 正在单次打包调阅 Gemini 首席经济学家（已启用额度优化模式）...")
    try:
        prompt_payload = f"{system_prompt}\n\n【多源财讯并网大合集（已压缩）】\n{combined_text}"
        response = model.generate_content(prompt_payload)
        ai_output = response.text.strip()
        
        # 深度清洗，防止插件无法识别
        clean_html = ai_output.replace("```html", "").replace("```", "").strip()
        
        # 写入临时文件，供 GitHub Action 动作读取发送
        with open("email_content.html", "w", encoding="utf-8") as f:
            f.write(clean_html)
        print("✅ [打包完成] 全球情报已高密度缝合至本地临时容器！")

    except Exception as e:
        print(f"❌ [研判层异常]: {e}")

if __name__ == "__main__":
    run_radar()

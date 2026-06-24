import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import time
import random

def run_radar():
    print("🚀 [雷达启动] 正在初始化全球智库终极稳健版...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ [错误] 缺少必要密钥，请检查 GitHub Settings 里的 Secrets 配置！")
        return

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Connection": "keep-alive"
    }

    combined_text = ""

    # ==========================================
    # 🏅 华尔街见闻核心 API 
    # ==========================================
    try:
        wscn_api = "https://api-prod.wallstreetcn.com/apiv1/content/fabric/articles?channel=global&limit=10"
        res = requests.get(wscn_api, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            articles = data.get("data", {}).get("items", [])
            wscn_chunk = ""
            for art in articles:
                wscn_chunk += f" 标题:{art.get('title', '')} | 简述:{art.get('content_short', '')};"
            combined_text += f"\n【华尔街见闻核心动态】{wscn_chunk[:1500]}"
            print("✅ 华尔街见闻 API 稳稳截流！")
    except Exception as e:
        print(f"⚠️ [跳过] 华尔街见闻 API 异常: {e}")

    # ==========================================
    # 🏅 CNBC 全球经济版块
    # ==========================================
    try:
        res = requests.get("https://www.cnbc.com/economy/", headers=headers, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = " ".join([p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p'])])
            combined_text += f"\n【源:CNBC_Economy】{' '.join(page_text.split())[:1500]}"
            print("✅ CNBC 全球情报固化并网成功！")
    except Exception as e:
        print(f"⚠️ [网络限制] CNBC 提取受阻: {e}")

    # ==========================================
    # 🎯 Yahoo Finance 宏观总池
    # ==========================================
    try:
        time.sleep(random.uniform(1.0, 2.0))
        res = requests.get("https://finance.yahoo.com/topic/economic-news/", headers=headers, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = " ".join([p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p'])])
            combined_text += f"\n【源:Yahoo_Finance】{' '.join(page_text.split())[:1500]}"
            print("✅ Yahoo 宏观主力通道全面恢复！")
    except Exception as e:
        print(f"⚠️ [网络限制] Yahoo 恢复失败: {e}")

    # ==========================================
    # 🎯 MarketWatch 免费开放节点
    # ==========================================
    try:
        time.sleep(random.uniform(1.0, 2.0))
        res = requests.get("https://www.marketwatch.com/latest-news", headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = " ".join([p.get_text() for p in soup.find_all(['h3', 'p'])])
            combined_text += f"\n【源:MarketWatch_Latest】{' '.join(page_text.split())[:1200]}"
            print("✅ MarketWatch 免费数据管道顺利通航！")
    except Exception as e:
        print(f"⚠️ [网络限制] MarketWatch 降级管线受阻: {e}")

    # ==========================================
    # 🧠 🧠 阶段三：安全流式架构（绝不在中途中断）
    # ==========================================
    clean_html = ""

    if len(combined_text.strip()) < 100:
        print("❌ [数据匮乏] 启动免额度保底防线...")
        clean_html = (
            "<h3>【高管决策内参 · 全球经贸雷达日报】</h3><hr>"
            "<p style='color: #666;'>📢 今日全网主流财经智库交投清淡，未捕获到宏观战略动态，系统自动拦截无意义调用以保护您的 AI 额度。</p>"
        )
    else:
        system_prompt = (
            "你是一位专注于跨国供应链安全、地缘经幕博弈与产融结合方向的顶级首席经济学家。\n"
            "请全盘析读以下由多源并网雷达高密度压缩后的英中文财经原材料。剔除垃圾广告，提取出真正具备战略震荡、会穿透到外贸关税、结汇汇率或大宗运输的重磅头条。\n"
            "【极其严格的铁律】\n"
            "不要带有任何 ```html 等 Markdown 代码壳，直接输出最纯粹、能被邮件客户端完美解析的 HTML 正文代码。结构如下：\n"
            "<h3>【高管决策内参 · 全球经贸雷达日报】</h3><hr>\n"
            "<b>【重磅战略动向】中文核心标题</b> (情报源: xxx)<br>\n"
            "<b>核心实质影响与产融研判：</b>120字内一针见血直接指出对供应链安全、关税政策或结汇层面的穿透性影响。<br><hr>"
        )

        print("\n🤖 [大脑析读] 正在单次调阅 Gemini 首席经济学家...")
        try:
            prompt_payload = f"{system_prompt}\n\n【四源并网情报合集】\n{combined_text}"
            response = model.generate_content(prompt_payload)
            ai_output = response.text.strip()
            clean_html = ai_output.replace("```html", "").replace("```", "").strip()
        except Exception as e:
            # 🌟 绝杀性改动：即使在这里遭遇异常，也只做信息登记，绝不允许 return 退出！
            print(f"❌ [智能体研判层异常]: {e}。启动防红仓紧急自救...")
            clean_html = f"<h3>【高管决策内参】</h3><hr><p>今日智能体进行宏观深度研判时遭遇临时网络波折: {e}。请查阅下方未经提炼的抓取原生流：</p><br><pre>{combined_text[:600]}</pre>"

    # ==========================================
    # 💾 💾 阶段四：大坝死锁落盘（无视任何异常，100%必出货）
    # ==========================================
    print("💾 正在执行大坝合拢落盘机制...")
    with open("email_content.html", "w", encoding="utf-8") as f:
        f.write(clean_html)
        f.flush()
    print("✅ [出厂完毕] email_content.html 容器已百分之百锁死到磁盘中！")

if __name__ == "__main__":
    run_radar()

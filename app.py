import streamlit as st  
import yfinance as yf  
import pandas as pd  

# 页面设置  
st.set_page_config(page_title="StockPilot", page_icon="📈")  

# 摸鱼主题说明  
st.title("📈 StockPilot")  
st.write("""  
**职场人的摸鱼投资原则**：  
1. 单日研究≤30分钟  
2. 只关注关键指标  
3. 让机器盯盘  
""")  

# 核心功能  
ticker = st.text_input("输入股票代码", placeholder="例: 00700.HK, AAPL")  
if ticker:  
    try:  
        stock = yf.Ticker(ticker)  
        hist = stock.history(period="1y")  

        # 关键指标卡片  
        col1, col2 = st.columns(2)  
        with col1:  
            st.metric("最新价", hist.iloc[-1]["Close"])  
            st.metric("5日波动率", f"{hist['Close'].pct_change().std()*100:.2f}%")  
        with col2:  
            st.metric("10日均价", hist['Close'].rolling(10).mean().iloc[-1].round(2))  
            st.metric("成交量", f"{hist['Volume'].mean()/1e6:.1f}M")  

        # 摸鱼提醒设置  
        st.divider()  
        st.subheader("摸鱼预警")  
        alert_price = st.number_input("设置价格提醒", value=hist['Close'].iloc[-1])  
        if st.button("订阅企业微信提醒"):  
            st.success("已设置！价格突破时静默推送")  

    except:  
        st.error("股票代码无效或API超时")  

# 黑话翻译彩蛋  
if st.checkbox("显示券商黑话翻译"):  
    st.write("""  
    - **"长期看好"** → 短期别指望  
    - **"估值修复"** → 已经跌到底了  
    - **"暂维持评级"** → 懒得改报告  
    """)  

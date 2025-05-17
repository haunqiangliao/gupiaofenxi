import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 页面配置
st.set_page_config(
    page_title="简易股票分析",
    page_icon="📈",
    layout="wide"
)

# 标题
st.title("📈 简易股票分析工具")
st.write("这是一个简单的股票分析工具，帮助您查看股票走势和关键指标。")

# 侧边栏 - 股票选择
with st.sidebar:
    st.header("股票选择")
    ticker = st.text_input("输入股票代码 (例如 AAPL, MSFT, BABA, 600519.SS)", "AAPL")
    
    # 时间范围选择
    time_range = st.selectbox(
        "选择时间范围",
        ["1个月", "3个月", "6个月", "1年", "2年", "5年"],
        index=3  # 默认1年
    )
    
    # 转换时间范围为天数
    time_mapping = {
        "1个月": 30,
        "3个月": 90,
        "6个月": 180,
        "1年": 365,
        "2年": 730,
        "5年": 1825
    }
    
    days = time_mapping[time_range]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 技术指标选择
    st.header("技术指标")
    show_ma = st.checkbox("显示移动平均线", value=True)
    ma_period = st.slider("移动平均周期", min_value=5, max_value=100, value=20, step=5) if show_ma else 0
    
    show_volume = st.checkbox("显示成交量", value=True)
    
    # 获取数据按钮
    if st.button("获取数据"):
        with st.spinner(f"正在获取{ticker}的股票数据..."):
            try:
                stock_data = yf.download(ticker, start=start_date, end=end_date)
                if not stock_data.empty:
                    st.session_state.stock_data = stock_data
                    st.session_state.ticker = ticker
                    st.success("数据获取成功！")
                else:
                    st.error(f"未能获取到{ticker}的股票数据，请检查股票代码是否正确。")
            except Exception as e:
                st.error(f"获取数据时出错: {str(e)}")

# 主内容区
if 'stock_data' in st.session_state and not st.session_state.stock_data.empty:
    stock_data = st.session_state.stock_data
    ticker = st.session_state.ticker
    
    # 获取股票信息
    try:
        stock_info = yf.Ticker(ticker).info
    except:
        stock_info = {}
    
    # 显示股票基本信息
    st.subheader(f"{ticker} - {stock_info.get('longName', '未知股票')}")
    
    # 数据概览
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("当前价格", f"${stock_data['Close'].iloc[-1]:.2f}")
        st.metric("今日开盘", f"${stock_data['Open'].iloc[-1]:.2f}")
    
    with col2:
        change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
        change_pct = (change / stock_data['Close'].iloc[-2]) * 100
        st.metric("涨跌额", f"${change:.2f}", f"{change_pct:.2f}%")
        st.metric("52周最高", f"${stock_info.get('fiftyTwoWeekHigh', 'N/A')}")
    
    with col3:
        st.metric("成交量", f"{stock_data['Volume'].iloc[-1]:,}")
        st.metric("52周最低", f"${stock_info.get('fiftyTwoWeekLow', 'N/A')}")
    
    with col4:
        st.metric("市值", f"${stock_info.get('marketCap', 'N/A'):,}")
        st.metric("市盈率", f"{stock_info.get('trailingPE', 'N/A')}")
    
    # 绘制价格走势图
    st.subheader(f"{time_range}价格走势图")
    
    # 创建图表
    fig = go.Figure()
    
    # 添加收盘价线
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['Close'],
            name="收盘价",
            line=dict(color='royalblue', width=2)
        )
    )
    
    # 添加移动平均线
    if show_ma:
        stock_data[f'MA_{ma_period}'] = stock_data['Close'].rolling(window=ma_period).mean()
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data[f'MA_{ma_period}'],
                name=f'{ma_period}日移动平均',
                line=dict(color='red', width=1.5)
            )
        )
    
    # 更新图表布局
    fig.update_layout(
        title=f"{ticker} {time_range}价格走势",
        xaxis_title="日期",
        yaxis_title="价格 (美元)",
        hovermode="x unified",
        height=500,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    # 显示图表
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示成交量
    if show_volume:
        st.subheader("成交量")
        
        fig_volume = go.Figure()
        
        fig_volume.add_trace(
            go.Bar(
                x=stock_data.index,
                y=stock_data['Volume'],
                name="成交量",
                marker_color='rgba(158, 202, 225, 0.7)'
            )
        )
        
        fig_volume.update_layout(
            title=f"{ticker} {time_range}成交量",
            xaxis_title="日期",
            yaxis_title="成交量",
            height=300,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
    
    # 显示最近数据
    st.subheader("最近交易数据")
    st.dataframe(stock_data.tail(10).style.format("{:.2f}"), use_container_width=True)
    
    # 简单分析
    st.subheader("趋势分析")
    
    # 计算基本统计数据
    latest_price = stock_data['Close'].iloc[-1]
    week_ago = stock_data['Close'].iloc[-5]
    month_ago = stock_data['Close'].iloc[-20] if len(stock_data) >= 20 else latest_price
    
    week_change = (latest_price - week_ago) / week_ago * 100
    month_change = (latest_price - month_ago) / month_ago * 100
    
    # 计算趋势
    if latest_price > week_ago:
        week_trend = "上涨"
        week_icon = "📈"
    else:
        week_trend = "下跌"
        week_icon = "📉"
    
    if latest_price > month_ago:
        month_trend = "上涨"
        month_icon = "📈"
    else:
        month_trend = "下跌"
        month_icon = "📉"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(f"近一周趋势", f"{week_trend} {week_icon}", f"{week_change:.2f}%")
    
    with col2:
        st.metric(f"近一月趋势", f"{month_trend} {month_icon}", f"{month_change:.2f}%")
    
    # 移动平均线信号
    if show_ma:
        ma_signal = "中性"
        ma_icon = "➖"
        
        if latest_price > stock_data[f'MA_{ma_period}'].iloc[-1]:
            ma_signal = "看涨"
            ma_icon = "📈"
        elif latest_price < stock_data[f'MA_{ma_period}'].iloc[-1]:
            ma_signal = "看跌"
            ma_icon = "📉"
        
        st.metric(f"{ma_period}日移动平均线信号", f"{ma_signal} {ma_icon}")
    
    st.warning("⚠️ 注意: 本工具仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
else:
    st.info("请在侧边栏输入股票代码并点击'获取数据'按钮开始分析。")

# 页脚
st.markdown("---")
st.markdown("© 2023 简易股票分析工具 | 数据来源: Yahoo Finance")

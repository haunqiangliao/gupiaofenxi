import random
import datetime
import math
from typing import List, Dict, Tuple

# 模拟股票数据生成器
class StockDataGenerator:
    def __init__(self, symbol: str, base_price: float = 100.0, volatility: float = 0.02):
        self.symbol = symbol
        self.base_price = base_price
        self.volatility = volatility
    
    def generate_data(self, days: int = 30) -> List[Dict[str, float]]:
        """生成模拟股票数据"""
        data = []
        price = self.base_price
        
        for i in range(days):
            # 计算日期 (从今天往前推)
            date = (datetime.datetime.now() - datetime.timedelta(days=days-i-1)).strftime('%Y-%m-%d')
            
            # 生成随机价格变动
            change = price * self.volatility * (random.random() * 2 - 1)
            price = round(price + change, 2)
            
            # 生成当日高低价 (在收盘价的±1%范围内)
            high = round(price * (1 + random.random() * 0.01), 2)
            low = round(price * (1 - random.random() * 0.01), 2)
            
            # 确保高低价逻辑正确
            if low > high:
                low, high = high, low
            
            data.append({
                'date': date,
                'open': round(price, 2),
                'high': high,
                'low': low,
                'close': round(price + (random.random() * 2 - 1) * price * 0.005, 2),
                'volume': random.randint(1000000, 10000000)
            })
        
        return data

# 股票分析器
class StockAnalyzer:
    def __init__(self, data: List[Dict[str, float]]):
        self.data = data
    
    def calculate_moving_average(self, days: int = 5) -> List[float]:
        """计算移动平均线"""
        if len(self.data) < days:
            return [None] * len(self.data)
        
        averages = []
        for i in range(len(self.data)):
            if i < days - 1:
                averages.append(None)
            else:
                sum_close = sum([self.data[j]['close'] for j in range(i-days+1, i+1)])
                averages.append(round(sum_close / days, 2))
        
        return averages
    
    def calculate_rsi(self, period: int = 14) -> List[float]:
        """计算相对强弱指数 (RSI)"""
        if len(self.data) < period + 1:
            return [None] * len(self.data)
        
        rsi_values = [None] * len(self.data)
        
        # 计算价格变动
        deltas = [self.data[i]['close'] - self.data[i-1]['close'] for i in range(1, len(self.data))]
        
        for i in range(period, len(self.data)):
            # 获取最近period天的价格变动
            recent_deltas = deltas[i-period:i]
            
            # 计算平均上涨和平均下跌
            avg_gain = sum([d for d in recent_deltas if d > 0]) / period
            avg_loss = abs(sum([d for d in recent_deltas if d < 0])) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = round(100 - (100 / (1 + rs)), 2)
            
            rsi_values[i] = rsi
        
        return rsi_values
    
    def get_latest_price(self) -> float:
        """获取最新价格"""
        return self.data[-1]['close'] if self.data else 0
    
    def get_price_change(self) -> Tuple[float, float]:
        """获取价格变动和变动百分比"""
        if len(self.data) < 2:
            return (0, 0)
        
        latest = self.data[-1]['close']
        prev = self.data[-2]['close']
        change = latest - prev
        change_pct = (change / prev) * 100
        
        return (round(change, 2), round(change_pct, 2))
    
    def get_trend(self) -> str:
        """判断短期趋势"""
        if len(self.data) < 5:
            return "无法判断"
        
        recent_prices = [d['close'] for d in self.data[-5:]]
        slope = (recent_prices[-1] - recent_prices[0]) / 4
        
        if slope > 0:
            return "上升"
        elif slope < 0:
            return "下降"
        else:
            return "横盘"

# 终端UI显示
class StockApp:
    def __init__(self):
        self.stocks = {
            "AAPL": {"name": "Apple Inc.", "base_price": 175.0},
            "MSFT": {"name": "Microsoft Corp.", "base_price": 340.0},
            "GOOGL": {"name": "Alphabet Inc.", "base_price": 130.0},
            "AMZN": {"name": "Amazon.com Inc.", "base_price": 125.0},
            "TSLA": {"name": "Tesla Inc.", "base_price": 240.0}
        }
        self.current_stock = None
        self.data = []
        self.analyzer = None
    
    def run(self):
        """运行应用"""
        while True:
            self._display_menu()
            choice = input("请选择操作 (1-5, q): ")
            
            if choice == "1":
                self._select_stock()
            elif choice == "2":
                self._show_stock_info()
            elif choice == "3":
                self._show_price_chart()
            elif choice == "4":
                self._show_analysis()
            elif choice == "5":
                self._change_time_period()
            elif choice.lower() == "q":
                print("感谢使用股票分析工具，再见！")
                break
            else:
                print("无效选择，请重试。")
    
    def _display_menu(self):
        """显示主菜单"""
        print("\n" + "="*40)
        print("           股票分析工具 (极简版)")
        print("="*40)
        
        if self.current_stock:
            print(f"当前股票: {self.current_stock} - {self.stocks[self.current_stock]['name']}")
        else:
            print("当前股票: 未选择")
        
        print("\n1. 选择股票")
        print("2. 查看股票信息")
        print("3. 查看价格走势图")
        print("4. 查看技术分析")
        print("5. 更改时间周期")
        print("q. 退出")
    
    def _select_stock(self):
        """选择股票"""
        print("\n可用股票:")
        for i, symbol in enumerate(self.stocks.keys(), 1):
            print(f"{i}. {symbol} - {self.stocks[symbol]['name']}")
        
        choice = input("请选择股票 (1-5): ")
        
        try:
            choice_idx = int(choice) - 1
            symbols = list(self.stocks.keys())
            
            if 0 <= choice_idx < len(symbols):
                self.current_stock = symbols[choice_idx]
                self._generate_data()
                print(f"已选择 {self.current_stock} - {self.stocks[self.current_stock]['name']}")
            else:
                print("无效选择，请重试。")
        except ValueError:
            print("无效输入，请输入数字。")
    
    def _generate_data(self, days: int = 30):
        """生成模拟数据"""
        if not self.current_stock:
            return
        
        generator = StockDataGenerator(
            self.current_stock,
            self.stocks[self.current_stock]['base_price']
        )
        
        self.data = generator.generate_data(days)
        self.analyzer = StockAnalyzer(self.data)
    
    def _show_stock_info(self):
        """显示股票基本信息"""
        if not self.current_stock or not self.analyzer:
            print("\n请先选择股票。")
            return
        
        print(f"\n{self.current_stock} - {self.stocks[self.current_stock]['name']}")
        print("-"*40)
        
        latest_price = self.analyzer.get_latest_price()
        change, change_pct = self.analyzer.get_price_change()
        
        print(f"最新价格: ${latest_price:.2f}")
        print(f"价格变动: ${change:.2f} ({change_pct:.2f}%)")
        print(f"时间周期: {len(self.data)} 天")
        print(f"最高价: ${max([d['high'] for d in self.data]):.2f}")
        print(f"最低价: ${min([d['low'] for d in self.data]):.2f}")
        print(f"趋势: {self.analyzer.get_trend()}")
    
    def _show_price_chart(self):
        """显示价格走势图"""
        if not self.current_stock or not self.analyzer:
            print("\n请先选择股票。")
            return
        
        print(f"\n{self.current_stock} 价格走势图 ({len(self.data)}天)")
        print("-"*40)
        
        # 提取价格数据
        prices = [d['close'] for d in self.data]
        dates = [d['date'] for d in self.data]
        
        # 计算价格范围
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        # 确定图表高度和宽度
        height = 15
        width = min(80, len(prices))
        
        # 缩放价格到图表高度
        scaled_prices = [(p - min_price) / price_range * (height - 1) for p in prices]
        
        # 选择显示的日期标签 (每隔一定间隔显示一个)
        date_labels = [dates[i] if i % (len(dates) // 5) == 0 else "" for i in range(len(dates))]
        
        # 创建图表
        chart = [[' ' for _ in range(width)] for _ in range(height)]
        
        # 绘制价格线
        for i in range(width):
            idx = int(i * len(prices) / width)
            row = int(round(scaled_prices[idx]))
            chart[row][i] = '•'
        
        # 打印图表
        for row in reversed(chart):
            print(''.join(row))
        
        # 打印价格刻度
        print(f"最高价: ${max_price:.2f}")
        print(f"最低价: ${min_price:.2f}")
        
        # 打印日期标签
        date_str = "日期: "
        for i, label in enumerate(date_labels):
            if label and i % (len(date_labels) // 5) == 0:
                date_str += f"{label}  "
        
        print(date_str[:80])  # 限制长度以保持美观
    
    def _show_analysis(self):
        """显示技术分析结果"""
        if not self.current_stock or not self.analyzer:
            print("\n请先选择股票。")
            return
        
        print(f"\n{self.current_stock} 技术分析")
        print("-"*40)
        
        # 计算移动平均线
        ma5 = self.analyzer.calculate_moving_average(5)
        ma20 = self.analyzer.calculate_moving_average(20)
        
        # 计算RSI
        rsi = self.analyzer.calculate_rsi(14)
        
        # 获取最新指标值
        latest_ma5 = ma5[-1] if ma5[-1] else "N/A"
        latest_ma20 = ma20[-1] if ma20[-1] else "N/A"
        latest_rsi = rsi[-1] if rsi[-1] else "N/A"
        
        print(f"5日移动平均线: ${latest_ma5}")
        print(f"20日移动平均线: ${latest_ma20}")
        print(f"RSI (14天): {latest_rsi}")
        
        # 趋势分析
        print("\n趋势分析:")
        latest_price = self.analyzer.get_latest_price()
        
        if latest_ma5 != "N/A" and latest_ma20 != "N/A":
            if latest_price > latest_ma5 > latest_ma20:
                print("强势上涨趋势 - 价格高于短期和长期均线")
            elif latest_price < latest_ma5 < latest_ma20:
                print("强势下跌趋势 - 价格低于短期和长期均线")
            elif latest_price > latest_ma5 and latest_ma5 < latest_ma20:
                print("可能反弹 - 价格突破短期均线但仍低于长期均线")
            elif latest_price < latest_ma5 and latest_ma5 > latest_ma20:
                print("可能回调 - 价格跌破短期均线但仍高于长期均线")
            else:
                print("趋势不明朗")
        
        if latest_rsi != "N/A":
            if latest_rsi > 70:
                print("RSI超买 - 可能回调")
            elif latest_rsi < 30:
                print("RSI超卖 - 可能反弹")
            else:
                print("RSI中性 - 市场平衡")
    
    def _change_time_period(self):
        """更改时间周期"""
        if not self.current_stock:
            print("\n请先选择股票。")
            return
        
        try:
            days = int(input("请输入天数 (7-180): "))
            if 7 <= days <= 180:
                self._generate_data(days)
                print(f"已更新时间周期为 {days} 天")
            else:
                print("天数超出范围，请输入7-180之间的数字。")
        except ValueError:
            print("无效输入，请输入数字。")

# 主程序入口
if __name__ == "__main__":
    app = StockApp()
    app.run()

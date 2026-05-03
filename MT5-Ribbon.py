import MetaTrader5 as mt5
import customtkinter as ctk
import threading
import time

# تحسين أداء النظام لإعطاء بايثون أولوية عالية
try:
    import win32api, win32process, win32con
    win32process.SetPriorityClass(win32api.GetCurrentProcess(), win32con.HIGH_PRIORITY_CLASS)
except:
    pass

class UltimateGoldTerminalV5_Final(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.symbol = "XAUUSD"
        self.title("MT5 Ribbon V5.0 - Aggressive Mode")
        self.geometry("400x950")
        self.configure(fg_color="#1a1a1a")
        self.attributes("-topmost", True)

        if not mt5.initialize():
            print("MT5 Initialization Failed")
            return

        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        # 1. شريط الحالة العلوي
        self.top_bar = ctk.CTkFrame(self, fg_color="#252525", height=40, corner_radius=0)
        self.top_bar.pack(side="top", fill="x")
        self.market_status = ctk.CTkLabel(self.top_bar, text="MARKET: ●", text_color="gray", font=("Arial", 11, "bold"))
        self.market_status.pack(side="left", padx=15)
        self.conn_status = ctk.CTkLabel(self.top_bar, text="MT5 API: ●", text_color="gray", font=("Arial", 11, "bold"))
        self.conn_status.pack(side="right", padx=15)

        # 2. عرض الرصيد
        self.balance_frame = ctk.CTkFrame(self, fg_color="#2ecc71", corner_radius=0, height=30)
        self.balance_frame.pack(fill="x")
        self.balance_label = ctk.CTkLabel(self.balance_frame, text="Balance: $0.00", text_color="#1a1a1a", font=("Arial", 14, "bold"))
        self.balance_label.pack()

        # 3. شاشة الأرباح والخسائر
        self.pnl_label = ctk.CTkLabel(self, text="$0.00", font=("Orbitron", 50, "bold"), text_color="#ffffff")
        self.pnl_label.pack(pady=(15, 5))
        
        self.log_label = ctk.CTkLabel(self, text="Aggressive Mode Active", font=("Arial", 11), text_color="#f1c40f")
        self.log_label.pack()

        # --- قسم الشعار واختيار العملة ---
        self.symbol_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=10)
        self.symbol_frame.pack(pady=10, padx=20, fill="x")
        
        self.logo_label = ctk.CTkLabel(self.symbol_frame, text="🟡", font=("Arial", 30))
        self.logo_label.pack(side="left", padx=15, pady=5)
        
        self.symbol_display = ctk.CTkLabel(self.symbol_frame, text=self.symbol, font=("Arial", 18, "bold"), text_color="#f1c40f")
        self.symbol_display.pack(side="left", padx=5)

        self.symbol_selector = ctk.CTkOptionMenu(
            self.symbol_frame, 
            values=["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD"],
            command=self.change_symbol,
            width=100,
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555"
        )
        self.symbol_selector.set(self.symbol)
        self.symbol_selector.pack(side="right", padx=15)

        # 4. إحصائيات الهامش
        self.risk_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=10)
        self.risk_frame.pack(pady=10, padx=20, fill="x")
        self.risk_label = ctk.CTkLabel(self.risk_frame, text="Margin Usage: 0.00%", font=("Arial", 14, "bold"))
        self.risk_label.pack(pady=5)
        
        # 5. منطقة المدخلات
        self.input_container = ctk.CTkFrame(self, fg_color="transparent")
        self.input_container.pack(pady=10, padx=20, fill="x")
        
        self.lot_box = ctk.CTkFrame(self.input_container, fg_color="#333333", corner_radius=8)
        self.lot_box.pack(side="left", expand=True, padx=5, fill="both")
        ctk.CTkLabel(self.lot_box, text="LOT SIZE", font=("Arial", 10, "bold")).pack(pady=(5,0))
        self.lot_input = ctk.CTkEntry(self.lot_box, width=80, border_width=0, justify="center", font=("Arial", 16, "bold"), fg_color="transparent")
        self.lot_input.insert(0, "0.10")
        self.lot_input.pack(pady=5)

        self.count_box = ctk.CTkFrame(self.input_container, fg_color="#333333", corner_radius=8)
        self.count_box.pack(side="left", expand=True, padx=5, fill="both")
        ctk.CTkLabel(self.count_box, text="COUNT", font=("Arial", 10, "bold")).pack(pady=(5,0))
        self.count_input = ctk.CTkEntry(self.count_box, width=80, border_width=0, justify="center", font=("Arial", 16, "bold"), fg_color="transparent")
        self.count_input.insert(0, "1")
        self.count_input.pack(pady=5)

        self.max_label = ctk.CTkLabel(self, text="Available to Open: 0", font=("Arial", 12, "italic"), text_color="#3498db")
        self.max_label.pack(pady=5)

        # 6. أزرار التنفيذ
        self.btn_buy = ctk.CTkButton(self, text="BUY", fg_color="#2ecc71", hover_color="#27ae60", height=60, font=("Arial", 25, "bold"), command=lambda: self.fire("buy"))
        self.btn_buy.pack(pady=5, padx=25, fill="x")

        self.btn_sell = ctk.CTkButton(self, text="SELL", fg_color="#e74c3c", hover_color="#c0392b", height=60, font=("Arial", 25, "bold"), command=lambda: self.fire("sell"))
        self.btn_sell.pack(pady=5, padx=25, fill="x")

        self.btn_be = ctk.CTkButton(self, text="BREAK EVEN (Safe)", fg_color="#ffffff", hover_color="#e0e0e0", 
                                    text_color="#000000", height=40, font=("Arial", 14, "bold"), command=self.break_even_all)
        self.btn_be.pack(pady=5, padx=25, fill="x")

        self.btn_close = ctk.CTkButton(self, text="CLOSE ALL POSITIONS", fg_color="#444444", height=40, font=("Arial", 14, "bold"), command=self.nuke)
        self.btn_close.pack(pady=(5, 10), padx=25, fill="x")

        # --- قسم مراقبة الصفقات ---
        self.monitor_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=10)
        self.monitor_frame.pack(pady=10, padx=20, fill="both", expand=True)
        ctk.CTkLabel(self.monitor_frame, text="LIVE TRADES MONITOR", font=("Arial", 11, "bold"), text_color="gray").pack(pady=5)
        self.scroll_frame = ctk.CTkScrollableFrame(self.monitor_frame, fg_color="transparent", height=150)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def update_positions_display(self, positions):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        if not positions:
            ctk.CTkLabel(self.scroll_frame, text="No active trades", text_color="#555555").pack(pady=20)
            return
        for p in positions:
            color = "#2ecc71" if p.profit >= 0 else "#e74c3c"
            type_str = "BUY" if p.type == mt5.ORDER_TYPE_BUY else "SELL"
            row = ctk.CTkFrame(self.scroll_frame, fg_color="#333333", height=35, corner_radius=5)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"#{p.ticket}", font=("Arial", 10), width=60).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{type_str} {p.volume}", font=("Arial", 10, "bold"), text_color=color, width=80).pack(side="left")
            ctk.CTkLabel(row, text=f"${p.profit:.2f}", font=("Arial", 11, "bold"), text_color=color).pack(side="right", padx=10)

    def change_symbol(self, new_symbol):
        self.symbol = new_symbol
        self.symbol_display.configure(text=self.symbol)
        icons = {"XAUUSD": "🟡", "BTCUSD": "₿", "EURUSD": "🇪🇺", "GBPUSD": "🇬🇧", "USDJPY": "🇯🇵"}
        self.logo_label.configure(text=icons.get(new_symbol, "📈"))

    def log_error(self, message):
        self.log_label.configure(text=f"SYSTEM: {message}", text_color="#e74c3c")
        self.after(2000, lambda: self.log_label.configure(text="Aggressive Mode Active", text_color="#f1c40f"))

    def update_loop(self):
        def run():
            while True:
                symbol_info = mt5.symbol_info(self.symbol)
                account = mt5.account_info()
                terminal = mt5.terminal_info()
                if terminal:
                    self.conn_status.configure(text_color="#2ecc71" if terminal.connected else "#e74c3c")
                if account:
                    self.after(0, lambda a=account: self.balance_label.configure(text=f"Balance: ${a.balance:,.2f}"))
                positions = mt5.positions_get(symbol=self.symbol)
                total_pnl = sum(p.profit for p in positions) if positions else 0.0
                pnl_color = "#2ecc71" if total_pnl > 0.01 else ("#e74c3c" if total_pnl < -0.01 else "#ffffff")
                self.after(0, lambda p=total_pnl, c=pnl_color: self.pnl_label.configure(text=f"${p:.2f}", text_color=c))
                self.after(0, lambda p=positions: self.update_positions_display(p))
                time.sleep(0.4)
        threading.Thread(target=run, daemon=True).start()

    def fire(self, side):
        try:
            count = int(self.count_input.get())
            lot = float(self.lot_input.get())
            for _ in range(count): threading.Thread(target=self.send_order, args=(side, lot)).start()
        except: self.log_error("Check Lot/Count")

    def send_order(self, side, lot):
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None: return

        # Aggressive Settings: Deviation 50 and Fill or Kill/Any
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY if side == "buy" else mt5.ORDER_TYPE_SELL,
            "price": tick.ask if side == "buy" else tick.bid,
            "deviation": 50, # سماح بانحراف كبير لضمان التنفيذ
            "magic": 2026,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC, # التنفيذ الفوري أو الإلغاء
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            # إذا فشل IOC، نحاول مرة أخرى بتنفيذ FOK كخيار أخير
            request["type_filling"] = mt5.ORDER_FILLING_FOK
            mt5.order_send(request)
            self.log_error(f"Slippage: {result.comment}")

    def nuke(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            for p in positions: threading.Thread(target=self.close_p, args=(p,)).start()

    def close_p(self, p):
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None: return
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": p.volume,
            "type": mt5.ORDER_TYPE_SELL if p.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": p.ticket,
            "price": tick.bid if p.type == mt5.ORDER_TYPE_BUY else tick.ask,
            "deviation": 50,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(request)

    def break_even_all(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if not positions: return
        for p in positions:
            if p.profit > 0: threading.Thread(target=self.set_be, args=(p,)).start()

    def set_be(self, pos):
        sl_price = pos.price_open + 0.05 if pos.type == mt5.ORDER_TYPE_BUY else pos.price_open - 0.05
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": pos.ticket,
            "sl": sl_price,
            "tp": pos.tp
        }
        mt5.order_send(request)

if __name__ == "__main__":
    app = UltimateGoldTerminalV5_Final()
    app.mainloop()
    mt5.shutdown()
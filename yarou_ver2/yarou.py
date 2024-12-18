import yfinance as yf
import pandas as pd
import tkinter as tk
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# 日経225の企業ティッカーシンボルをCSVファイルから読み込む
nikkei225 = pd.read_csv('nikkei225.csv', header = 0)
tickers = [f"{t}.T" for t in nikkei225.iloc[:, 1].tolist()]

# 必要なデータを取得する関数
def get_financial_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # 必要なデータを抽出
    data = {
        'ticker': ticker,
        'company_name': info.get('shortName', 'Unknown'),  # 企業名を取得
        'market_cap': info.get('marketCap'),
        'pe_ratio': info.get('trailingPE'),
        'eps': info.get('trailingEps'),
        'dividend_yield': info.get('dividendYield'),
        'price_to_book': info.get('priceToBook'),
        'total_revenue': info.get('totalRevenue'),
        'gross_profit': info.get('grossProfits'),
        'net_income': info.get('netIncomeToCommon'),
        'current_ratio': info.get('currentRatio')
    }
    
    return data

# すべてのティッカーのデータを取得
data_list = [get_financial_data(ticker) for ticker in tickers]
financial_data = pd.DataFrame(data_list)

# 欠損値の処理
financial_data = financial_data.fillna(0)

# 特徴量とターゲットを設定（ターゲットを前日の終値に変更）
def get_close_price(ticker):
    stock = yf.Ticker(ticker)
    historical_data = stock.history(period="1d")
    return historical_data['Close'][0]

# 前日の終値をターゲットに設定
financial_data['close_price'] = financial_data['ticker'].apply(get_close_price)

# 特徴量（X）とターゲット（y）
X = financial_data.drop(columns=['ticker', 'close_price', 'company_name'])
y = financial_data['close_price']

# トレーニングデータとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ランダムフォレスト回帰モデルのトレーニング
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# テストデータで予測
y_pred = model.predict(X_test)

# モデル評価
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")

# 上位10件の特徴量の重要度を表示
feature_importances = pd.Series(model.feature_importances_, index=X.columns)
top_10_features = feature_importances.nlargest(10)
print("Top 10 Features:")
print(top_10_features)

# GUIアプリケーションの作成
def create_gui():
    # GUIの基本設定
    root = tk.Tk()
    root.title("株 ヤロウ")
    
    # 終値や適正株価の表示エリア
    label_ticker = tk.Label(root, text="企業ティッカーシンボル:")
    label_ticker.grid(row=0, column=0)

     # エンターキーを押したときに計算を実行する
    def on_enter_pressed(event):
        show_result()

    ticker_entry = tk.Entry(root)
    ticker_entry.grid(row=0, column=1)   
    # エンターキーをエントリーウィジェットにバインド
    ticker_entry.bind("<Return>", on_enter_pressed)

    result_label = tk.Label(root, text="予測結果:")
    result_label.grid(row=1, column=0, columnspan=2)

    company_name_label = tk.Label(root, text="企業名:")
    company_name_label.grid(row=2, column=0, columnspan=2)

    # 結果表示用
    def show_result():
        ticker = ticker_entry.get()
        stock = yf.Ticker(ticker)
        historical_data = stock.history(period="1d")
        actual_close_price = historical_data['Close'][0]
        
        # 適正株価を予測する
        stock_data = get_financial_data(ticker)
        stock_features = pd.DataFrame([stock_data]).drop(columns=['ticker', 'company_name'])
        predicted_close_price = model.predict(stock_features)[0]
        price_difference = predicted_close_price - actual_close_price
        
        # 結果をラベルに表示
        result_label.config(text=f"適正株価: {predicted_close_price:.2f}\n前日の終値: {actual_close_price:.2f}\n差額: {price_difference:.2f}")
        company_name_label.config(text=f"企業名: {stock_data['company_name']}")  # 企業名を表示

    # 上位10特徴量の表示
    def show_top_features():
        # 新しいウィンドウを作成
        top_features_window = tk.Toplevel(root)
        top_features_window.title("重要特徴量")
        
        # 上位10特徴量を表示
        top_features_text = "\n".join([f"{feature}: {importance:.4f}" for feature, importance in top_10_features.items()])
        features_label = tk.Label(top_features_window, text=f"重要な特徴量:\n{top_features_text}")
        features_label.pack(padx=10, pady=10)
        
    # ボタン
    calc_button = tk.Button(root, text="予測", command=show_result)
    calc_button.grid(row=4, column=0, columnspan=2)
    
    show_features_button = tk.Button(root, text="重要特徴量", command=show_top_features)
    show_features_button.grid(row=5, column=0, columnspan=2)

    root.mainloop()

# アプリケーションを起動
create_gui()

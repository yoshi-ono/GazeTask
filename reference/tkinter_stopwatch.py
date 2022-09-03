# -*- coding:utf-8 -*-
import tkinter
import time

# ラベルを更新する間隔[ms]
INTERVAL = 10

# 計測開始時刻
start_time = 0

# 時間計測中フラグ
start_flag = False

# afterメソッドのID
after_id = 0

# 時間更新関数
def update_time():
    global start_time
    global app, label
    global after_id

    # update_time関数を再度INTERVAL[ms]後に実行
    after_id = app.after(INTERVAL, update_time)

    # 現在の時刻を取得
    now_time = time.time()

    # 現在の時刻と計測開始時刻の差から計測時間計算
    elapsed_time = now_time - start_time

    # 表示したい形式に変換（小数点第２位までに変換）
    elapsed_time_str = '{:.2f}'.format(elapsed_time)
    
    # 計測時間を表示
    label.config(text=elapsed_time_str)


# スタートボタンの処理
def start():
    global app
    global start_flag
    global start_time
    global after_id

    # 計測中でなければ時間計測開始
    if not start_flag:
        
        # 計測中フラグをON
        start_flag = True

        # 計測開始時刻を取得
        start_time = time.time()

        # update_timeをINTERVAL[ms] 後に実行
        after_id = app.after(INTERVAL, update_time)

# ストップボタンの処理
def stop():
    global start_flag
    global after_id

    # 計測中の場合は計測処理を停止
    if start_flag:

        # update_time関数の呼び出しをキャンセル
        app.after_cancel(after_id)

        # 計測中フラグをオフ
        start_flag = False

# メインウィンドウ作成
app = tkinter.Tk()
app.title("stop watch")
app.geometry("200x200")

# 時間計測結果表示ラベル
label = tkinter.Label(
    app,
    text="0.00",
    width=6,
    font=("", 50, "bold"),
)
label.pack(padx=10, pady=10)

# ストップウォッチのスタートボタン
start_button = tkinter.Button(
    app,
    text="START",
    command=start
)
start_button.pack(pady=5)

# ストップウォッチのストップボタン
stop_button = tkinter.Button(
    app,
    text="STOP",
    command=stop
)
stop_button.pack(pady=5)

# メインループ
app.mainloop()
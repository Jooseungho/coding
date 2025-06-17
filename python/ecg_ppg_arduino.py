import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import re

# 시리얼 포트 설정
ser = serial.Serial('COM4', 115200)
time.sleep(2)

# 시계열 윈도우 설정
window_size = 500
ecg_data = deque([0] * window_size, maxlen=window_size)
ppg_data = deque([0] * window_size, maxlen=window_size)

# 평균 BPM 계산용
ecg_bpm_values = deque(maxlen=100)
ppg_bpm_values = deque(maxlen=100)
last_print_time = time.time()
prev_ppg_bpm = None
ppg_same_count = 0

# 정규식: Serial 출력 파싱
pattern = re.compile(r"IR=(\d+) \| PPG_BPM=([\d.]+) \| ECG_BPM=([\d.]+) \| ECG=(\d+) \| P2P=(\d+)")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
line_ecg, = ax1.plot([], [], lw=2, color='blue')
line_ppg, = ax2.plot([], [], lw=2, color='green')
bpm_text_ecg = ax1.text(0.02, 0.92, '', transform=ax1.transAxes)
bpm_text_ppg = ax2.text(0.02, 0.92, '', transform=ax2.transAxes)


def init_plot():
    ax1.set_xlim(0, window_size)
    ax1.set_ylim(0, 4095)
    ax1.set_title("ECG Signal")
    ax1.set_ylabel("ECG Value")
    ax1.grid()

    ax2.set_xlim(0, window_size)
    ax2.set_title("PPG (IR) Signal")
    ax2.set_ylabel("IR Value")
    ax2.set_xlabel("Samples")
    ax2.grid()

    return line_ecg, line_ppg, bpm_text_ecg, bpm_text_ppg


def update(frame):
    global last_print_time, prev_ppg_bpm, ppg_same_count

    while ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            match = pattern.match(line)
            if match:
                ir, bpm_ppg, bpm_ecg, ecg, p2p = match.groups()
                ecg = int(ecg)
                ir = int(ir)
                bpm_ecg = float(bpm_ecg)
                bpm_ppg = float(bpm_ppg)

                ecg_data.append(ecg)
                ppg_data.append(ir)

                # 실시간 Y축 조정 (PPG)
                min_ppg = min(ppg_data)
                max_ppg = max(ppg_data)
                margin = (max_ppg - min_ppg) * 0.1 if max_ppg > min_ppg else 1000
                ax2.set_ylim(min_ppg - margin, max_ppg + margin)

                # 그래프 업데이트
                line_ecg.set_ydata(ecg_data)
                line_ecg.set_xdata(range(len(ecg_data)))
                line_ppg.set_ydata(ppg_data)
                line_ppg.set_xdata(range(len(ppg_data)))

                bpm_text_ecg.set_text(f"ECG BPM: {bpm_ecg:.1f}")
                bpm_text_ppg.set_text(f"PPG BPM: {bpm_ppg:.1f}")

                # ✅ ECG BPM: 비정상값 필터링
                if 40 < bpm_ecg < 160:
                    ecg_bpm_values.append(bpm_ecg)

                # ✅ PPG BPM: 일정값 반복 시 제외
                if 40 < bpm_ppg < 160:
                    if prev_ppg_bpm is not None and abs(bpm_ppg - prev_ppg_bpm) < 0.5:
                        ppg_same_count += 1
                    else:
                        ppg_same_count = 0
                        prev_ppg_bpm = bpm_ppg

                    if ppg_same_count < 5:
                        ppg_bpm_values.append(bpm_ppg)

                # 콘솔 출력 (2초마다)
                now = time.time()
                if now - last_print_time >= 2.0:
                    avg_ecg = sum(ecg_bpm_values) / len(ecg_bpm_values) if ecg_bpm_values else 0
                    avg_ppg = sum(ppg_bpm_values) / len(ppg_bpm_values) if ppg_bpm_values else 0
                    print(f"[BPM 평균] ECG: {avg_ecg:.2f} | PPG: {avg_ppg:.2f}")
                    last_print_time = now

        except Exception as e:
            print("⚠️ 파싱 오류:", e)
            continue

    return line_ecg, line_ppg, bpm_text_ecg, bpm_text_ppg


ani = animation.FuncAnimation(fig, update, init_func=init_plot, interval=50)
plt.tight_layout()
plt.show()

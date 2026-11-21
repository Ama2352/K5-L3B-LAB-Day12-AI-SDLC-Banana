"""Benchmark có render (TICKET-04 mục 1), chỉ thư viện chuẩn Python + trình duyệt.

    python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json

Cảnh đo: buổi sáng lõi (contract hiện hành: độ tươi, cá bơi/sinh, Cá Sấu Năm Chèo, hiệu ứng mặc định),
Út Sen đứng yên ở bến (không gửi input). Dùng CÙNG máy chủ/lớp sim của `chonoi.live` và CÙNG giao diện
Canvas `chonoi/web/index.html`, vẽ ở 1280×720 (tỉ lệ điểm ảnh 1). Trang tự đo bằng requestAnimationFrame:
làm nóng `--warmup` giây (mặc định 3) rồi đo `--duration` giây, gửi thời điểm từng khung về máy chủ.

Trình duyệt: Chrome/Chromium (cửa sổ 1280×720, mặc định headless) nếu tìm thấy, hoặc `--browser <đường dẫn>`
/ biến môi trường CHONOI_BENCH_BROWSER; không có thì mở trình duyệt mặc định của hệ thống.

bench.json (5 trường):
  frames, measured_s  số khung và số giây thực tế trong khoảng đo sau làm nóng
  avg_fps             frames / measured_s
  p1_low_fps          max(1, ceil(0.01 × frames)) khung chậm nhất → nghịch đảo thời gian trung bình (giây)
  load_ms             mili giây từ lúc khởi chạy lệnh đến khung hình đầu tiên của cảnh đo
Mã thoát: 0 ghi xong, 1 lỗi chạy / quá thời gian chờ, 2 cờ sai.
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser

T0_EPOCH_MS = time.time() * 1000.0  # "lúc khởi chạy" — đo sớm nhất có thể trong tiến trình

from .contract import load_contract  # noqa: E402
from .errors import BadInput  # noqa: E402
from .live import LiveGame, LiveServer, _Handler  # noqa: E402

WIDTH, HEIGHT = 1280, 720
MAX_RESULT_BODY = 8 * 1024 * 1024
CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
)


def compute(frame_ts_ms, first_frame_epoch_ms, t0_epoch_ms=T0_EPOCH_MS):
    """frame_ts_ms: mốc thời gian (ms) các khung trong khoảng đo, phần tử đầu là mốc bắt đầu đo."""
    if len(frame_ts_ms) < 2:
        raise ValueError("không đủ khung hình để đo")
    deltas = [(b - a) / 1000.0 for a, b in zip(frame_ts_ms, frame_ts_ms[1:])]
    frames = len(deltas)
    measured_s = (frame_ts_ms[-1] - frame_ts_ms[0]) / 1000.0
    k = max(1, math.ceil(0.01 * frames))
    slowest = sorted(deltas, reverse=True)[:k]
    return {
        "avg_fps": round(frames / measured_s, 3),
        "p1_low_fps": round(1.0 / (sum(slowest) / k), 3),
        "frames": frames,
        "measured_s": round(measured_s, 3),
        "load_ms": round(first_frame_epoch_ms - t0_epoch_ms, 1),
    }


def find_browser(explicit=None):
    for c in (explicit, os.environ.get("CHONOI_BENCH_BROWSER"), *CHROME_CANDIDATES):
        if not c:
            continue
        path = c if os.path.isabs(c) else shutil.which(c)
        if path and os.path.exists(path):
            return path
    return None


class _BenchHandler(_Handler):
    result = None
    done = None

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/bench-result":
            return super().do_POST()
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = -1
        if not 0 < n <= MAX_RESULT_BODY:
            self._send(400, b'{"error":"body sai"}')
            return
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8"))
            type(self).result = body
        except (ValueError, UnicodeDecodeError) as e:
            self._send(400, json.dumps({"error": str(e)}).encode("utf-8"))
            return
        self._send(200, b'{"ok":true}')
        type(self).done.set()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.bench", description="Benchmark cảnh lặn có render (TICKET-04).")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--duration", type=float, required=True, help="số giây đo sau làm nóng")
    p.add_argument("--out", required=True)
    p.add_argument("--warmup", type=float, default=3.0)
    p.add_argument("--browser", help="đường dẫn Chrome/Chromium")
    p.add_argument("--headed", action="store_true", help="mở cửa sổ thật thay vì headless")
    p.add_argument("--port", type=int, default=0)
    try:
        a = p.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.duration <= 0 or a.warmup < 0:
        sys.stderr.write("--duration phải > 0, --warmup ≥ 0\n")
        return 2
    try:
        tuning = load_contract()["tuning"]
        game = LiveGame("gather", tuning, {}, a.seed)  # cảnh lõi mặc định, đứng yên ở bến (vị trí xuất phát)
        handler = type("BenchHandler", (_BenchHandler,), {"game": game, "result": None, "done": threading.Event()})
        server = LiveServer(game, "127.0.0.1", a.port)
        server.httpd.RequestHandlerClass = handler
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2
    except OSError as e:
        sys.stderr.write(f"không mở được cổng: {e}\n")
        return 1

    url = f"{server.url}?bench=1&warmup={a.warmup}&duration={a.duration}&t0={T0_EPOCH_MS:.1f}"
    server.start()
    proc, profile = None, None
    try:
        browser = find_browser(a.browser)
        if browser:
            profile = tempfile.mkdtemp(prefix="chonoi-bench-")
            args = [browser, f"--window-size={WIDTH},{HEIGHT}", f"--user-data-dir={profile}", "--no-first-run",
                    "--no-default-browser-check", "--disable-background-timer-throttling",
                    "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows",
                    "--force-device-scale-factor=1"]
            if not a.headed:
                args.append("--headless=new")
            proc = subprocess.Popen([*args, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            sys.stderr.write("không thấy Chrome/Chromium, mở trình duyệt mặc định (giữ cửa sổ ở 1280×720)\n")
            webbrowser.open(url)
        if not handler.done.wait(a.warmup + a.duration + 90):
            sys.stderr.write("quá thời gian chờ kết quả bench từ trình duyệt\n")
            return 1
        r = handler.result
        out = compute(r["frame_ts_ms"], r["first_frame_epoch_ms"])
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(",", ":"))
            f.write("\n")
        print(json.dumps(out), flush=True)
        return 0
    except (KeyError, TypeError, ValueError, OSError) as e:
        sys.stderr.write(f"lỗi bench: {e}\n")
        return 1
    finally:
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        if profile:
            shutil.rmtree(profile, ignore_errors=True)
        server.stop()


if __name__ == "__main__":
    sys.exit(main())

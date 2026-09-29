from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import ProxyHandler, build_opener
import json
import threading

ROOT = Path(__file__).parent
CACHE_FILE = ROOT / 'lotto-history.json'
LOTTO_API = 'https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?srchStrLtEpsd=1&srchEndLtEpsd=9999'
opener = build_opener(ProxyHandler({}))
sync_lock = threading.Lock()
sync_state = {'running': False, 'message': '당첨 이력을 불러오지 않았습니다.', 'rounds': 0}


def cached_history():
    try:
        data = json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def fetch_history():
    with opener.open(LOTTO_API, timeout=20) as response:
        payload = json.load(response)
    rows = payload.get('data', {}).get('list', [])
    history = []
    for row in rows:
        numbers = tuple(sorted(int(row[f'tm{i}WnNo']) for i in range(1, 7)))
        history.append({'round': int(row['ltEpsd']), 'date': row.get('ltRflYmd', ''), 'numbers': numbers})
    if not history:
        raise RuntimeError('No lottery history received')
    return sorted(history, key=lambda item: item['round'])


def synchronize():
    if not sync_lock.acquire(blocking=False):
        return
    try:
        sync_state.update(running=True, message='동행복권 회차 데이터를 불러오는 중…')
        history = fetch_history()
        CACHE_FILE.write_text(json.dumps(history, ensure_ascii=False), encoding='utf-8')
        sync_state.update(rounds=len(history), message=f'{len(history)}개 회차의 1등 조합을 확인했습니다.')
    except Exception:
        sync_state.update(message='당첨 이력을 불러오지 못했습니다. 인터넷 연결 후 다시 시도해 주세요.')
    finally:
        sync_state['running'] = False
        sync_lock.release()


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/history':
            payload = {'history': cached_history(), 'sync': sync_state}
            self.respond(payload)
            return
        if path == '/api/sync':
            if not sync_state['running']:
                threading.Thread(target=synchronize, daemon=True).start()
            self.respond({'ok': True, 'sync': sync_state}, 202)
            return
        super().do_GET()

    def respond(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    with ThreadingHTTPServer(('127.0.0.1', 8001), Handler) as server:
        print('Lotto Gazua: http://localhost:8001', flush=True)
        server.serve_forever()

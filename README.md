# Lotto Gazua

과거 로또 6/45 1등 번호 조합을 제외해 번호를 생성하는 정적 웹 앱입니다.

## 공개 사이트

GitHub Pages 배포 후 아래 주소에서 누구나 사용할 수 있습니다.

`https://kineihiyama-kyc.github.io/lotto-gazua/`

## 동작 방식

- `lotto-history.json`에 포함된 과거 1등 조합과 같은 번호 조합은 생성하지 않습니다.
- 번호별 1등 출현 횟수는 배포된 이력 파일을 바탕으로 표시합니다.
- “당첨 이력 갱신”은 웹사이트에 배포된 최신 이력 파일을 다시 불러옵니다. 새 회차를 반영하려면 `lotto-history.json`을 갱신해 GitHub에 올려야 합니다.

## 로컬에서 미리 보기

별도 설치 없이 `index.html`을 브라우저에서 열 수 있습니다. 일부 브라우저의 로컬 파일 보안 정책 때문에 이력이 보이지 않으면 아래처럼 간단한 서버를 실행하세요.

```powershell
cd 'lotto gazua'
python -m http.server 8001
```

그다음 `http://localhost:8001`을 엽니다.

## 주의

이 앱은 과거 1등 조합을 피할 뿐, 특정 조합의 당첨 확률을 높이지 않습니다.

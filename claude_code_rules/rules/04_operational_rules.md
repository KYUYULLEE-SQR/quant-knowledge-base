# 🔧 Operational Rules (실무 규칙)

## Code Quality
1. **No Placeholders**: `pass`, `# TODO` 절대 금지
2. **Full Implementation**: 스켈레톤 코드 금지
3. **Error Handling**: Try-except + meaningful messages
4. **Validation**: Input validation (None/type/range check)
5. **Logging**: Critical steps에 logging
6. **Docstrings**: 함수마다 docstring

## File Operations
1. **pathlib** 사용 (os.path 금지)
2. **Absolute paths** 우선
3. **Existence check**: 파일 읽기 전 확인
4. **Atomic writes**: 임시 파일 → rename

## Database
1. **Parameterized queries**: SQL injection 방지
2. **Close connections**: finally 블록에서 닫기
3. **Batch operations**: executemany 사용
4. **Index awareness**: 쿼리 작성 시 인덱스 활용

## Performance
1. **Vectorization**: Loop 대신 NumPy/Pandas
2. **Lazy evaluation**: 필요한 만큼만 로드
3. **Caching**: 반복 계산 방지
4. **Memory**: 대용량 데이터 시 메모리 관리

## Backtesting
1. **No look-ahead bias**: 미래 데이터 절대 금지
2. **Realistic costs**: 수수료, 슬리피지 반영
3. **Multiple periods**: 최소 2-3개 기간 검증
4. **Walk-forward**: 학습/테스트 기간 분리


# D435i 지원 스트림 모드 README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** README에 연결된 Intel RealSense D435i의 RGB·Depth·IR 지원 캡처 모드를 정확하고 읽기 쉽게 문서화한다.

**Architecture:** `README.md`의 RGB 캡처 안내 바로 다음에 지원 모드 섹션을 추가한다. 코드가 요청하는 포맷(`bgr8`, `z16`, `y8`)만 대상으로, 같은 FPS 집합을 공유하는 해상도를 묶은 세 개의 표를 사용한다.

**Tech Stack:** GitHub Flavored Markdown, pyrealsense2로 조회한 D435i 프로파일.

## Global Constraints

- 대상 장치는 Intel RealSense D435i이며, 프로파일은 2026-07-23에 연결된 장치에서 조회했다.
- RGB는 `bgr8`, Depth는 `z16`, IR 1·2는 `y8`만 기록한다.
- `512×512`는 지원하지 않으므로 지원 프로파일로 캡처 후 크롭 또는 리사이즈하도록 안내한다.

---

### Task 1: README 지원 모드 표 추가

**Files:**
- Modify: `README.md:22` (기본 캡처 설정 설명 뒤)
- Test: `README.md`의 표 내용과 현재 D435i 프로파일 조회 결과

**Interfaces:**
- Consumes: D435i의 `bgr8` RGB, `z16` Depth, `y8` IR 지원 모드
- Produces: 사용자가 CLI 인자에 사용할 수 있는 해상도·FPS 조합 표

- [x] **Step 1: 문서 검증 조건을 정의한다**

README에는 다음 핵심 문구와 표 행이 있어야 한다.

```text
## D435i 지원 스트림 모드
512×512는 지원하지 않습니다.
640×480 | 6, 15, 30, 60 FPS
848×480 | 6, 15, 30, 60 FPS
```

- [x] **Step 2: 현재 README에서 조건이 아직 충족되지 않음을 확인한다**

Run: `rg -n "D435i 지원 스트림 모드|512×512|640×480" README.md`

Expected: 명령이 일치 항목 없이 종료한다.

- [x] **Step 3: 기본 캡처 설명 뒤에 지원 모드 섹션을 추가한다**

삽입할 Markdown은 다음과 같다.

```markdown
## D435i 지원 스트림 모드

아래 표는 현재 연결된 Intel RealSense D435i에서 확인한 지원 모드입니다. 이 프로젝트의 `start()`가 요청하는 포맷만 표시합니다.

### RGB (`bgr8`)

| 해상도 | 지원 FPS |
| --- | --- |
| 1920×1080 | 6, 15, 30 |
| 1280×720 | 6, 15, 30 |
| 960×540 | 6, 15, 30, 60 |
| 848×480 | 6, 15, 30, 60 |
| 640×480 | 6, 15, 30, 60 |
| 640×360 | 6, 15, 30, 60 |
| 424×240 | 6, 15, 30, 60 |
| 320×240 | 6, 30, 60 |
| 320×180 | 6, 30, 60 |

### Depth (`z16`)

| 해상도 | 지원 FPS |
| --- | --- |
| 1280×720 | 6, 15, 30 |
| 848×480 | 6, 15, 30, 60, 90 |
| 640×480 | 6, 15, 30, 60, 90 |
| 640×360 | 6, 15, 30, 60, 90 |
| 480×270 | 6, 15, 30, 60, 90 |
| 424×240 | 6, 15, 30, 60, 90 |
| 256×144 | 90, 300 |
| 848×100 | 100, 300 |

### IR 1 · IR 2 (`y8`)

| 해상도 | 지원 FPS |
| --- | --- |
| 1280×800 | 15, 30 |
| 1280×720 | 6, 15, 30 |
| 848×480 | 6, 15, 30, 60, 90 |
| 640×480 | 6, 15, 30, 60, 90 |
| 640×360 | 6, 15, 30, 60, 90 |
| 480×270 | 6, 15, 30, 60, 90 |
| 424×240 | 6, 15, 30, 60, 90 |
| 256×144 | 90, 300 |
| 848×100 | 100, 300 |

`512×512`는 지원하지 않습니다. 정사각형 결과가 필요하면 지원되는 해상도로 캡처한 뒤 중앙 크롭 또는 리사이즈하세요.
```

- [x] **Step 4: 표와 안내 문구가 반영되었는지 확인한다**

Run: `rg -n "D435i 지원 스트림 모드|1920×1080|848×100|512×512" README.md`

Expected: 섹션 제목, RGB/Depth/IR의 대표 행, 비지원 모드 안내가 모두 출력된다.

- [x] **Step 5: Markdown 구조를 점검한다**

Run: `sed -n '1,100p' README.md`

Expected: 표가 `3DGS용 RGB 영상 캡처` 다음, `COLMAP용 JPG 샘플링` 전이며 모든 열이 두 개다.

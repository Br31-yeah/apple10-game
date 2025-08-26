import pygame
import random
import csv
import os
import time

# --------------------------
# 초기 설정
# --------------------------
pygame.init()
CELL_SIZE = 50
COLS, ROWS = 17, 10
WIDTH, HEIGHT = CELL_SIZE * COLS, CELL_SIZE * ROWS
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT + 50))  # 타이머 공간 추가
pygame.display.set_caption("사과 10 게임")

FONT = pygame.font.SysFont(None, 30)
CLOCK = pygame.time.Clock()

# --------------------------
# 색상 및 이미지
# --------------------------
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# 사과 이미지 (간단히 빨간 사각형으로 대체)
def draw_apple(surface, x, y, number):
    pygame.draw.rect(surface, RED, (x, y, CELL_SIZE, CELL_SIZE))
    text = FONT.render(str(number), True, WHITE)
    surface.blit(text, (x + CELL_SIZE//3, y + CELL_SIZE//4))

# --------------------------
# 블록 생성 (항상 해답 존재하도록)
# --------------------------
def generate_blocks():
    blocks = [[0]*COLS for _ in range(ROWS)]
    numbers = []
    total_cells = ROWS*COLS
    while len(numbers) < total_cells:
        a = random.randint(1, 9)
        b = 10 - a
        numbers.extend([a, b])
    numbers = numbers[:total_cells]
    random.shuffle(numbers)
    idx = 0
    for r in range(ROWS):
        for c in range(COLS):
            blocks[r][c] = numbers[idx]
            idx += 1
    return blocks

# --------------------------
# 게임 상태 초기화
# --------------------------
blocks = generate_blocks()
selected = []
score = 0
start_time = time.time()

# --------------------------
# 기록 저장
# --------------------------
def save_record(score, elapsed):
    file_exists = os.path.isfile("records.csv")
    with open("records.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Score", "Time"])
        writer.writerow([score, round(elapsed, 2)])

# --------------------------
# 메인 루프
# --------------------------
running = True
while running:
    CLOCK.tick(30)
    SCREEN.fill(WHITE)

    # ----------------------
    # 이벤트 처리
    # ----------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            c, r = mx // CELL_SIZE, my // CELL_SIZE
            if 0 <= r < ROWS and 0 <= c < COLS:
                if (r, c) not in selected:
                    selected.append((r, c))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # 선택 확정
                total = sum(blocks[r][c] for r, c in selected)
                if total == 10:
                    for r, c in selected:
                        blocks[r][c] = 0
                    score += 10
                selected = []

            elif event.key == pygame.K_ESCAPE:  # 선택 취소
                selected = []

    # ----------------------
    # 블록 그리기
    # ----------------------
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c*CELL_SIZE, r*CELL_SIZE
            num = blocks[r][c]
            if num > 0:
                draw_apple(SCREEN, x, y, num)
            if (r, c) in selected:
                pygame.draw.rect(SCREEN, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 3)

    # ----------------------
    # 타이머 및 점수
    # ----------------------
    elapsed = time.time() - start_time
    timer_text = FONT.render(f"Time: {int(elapsed)}s  Score: {score}", True, BLACK)
    SCREEN.blit(timer_text, (10, HEIGHT + 10))

    # ----------------------
    # 화면 업데이트
    # ----------------------
    pygame.display.flip()

    # ----------------------
    # 게임 종료 조건 (모든 블록 제거)
    # ----------------------
    if all(blocks[r][c]==0 for r in range(ROWS) for c in range(COLS)):
        save_record(score, elapsed)
        print(f"Game Clear! Score: {score}, Time: {int(elapsed)}s")
        running = False

pygame.quit()

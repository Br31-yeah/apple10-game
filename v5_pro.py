import pygame
import random
import os
import time

pygame.init()

# 화면 크기 (17x10 보드, 셀 크기 50px)
CELL_SIZE = 50
COLS, ROWS = 17, 10
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE + 100  # 위쪽에 점수/타이머 영역
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("사과 10 게임 - 프로 버전")

# 색상
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 100)
BLUE = (100, 150, 250)

# 폰트
font = pygame.font.SysFont("malgungothic", 24, bold=True)

# 효과음 (없으면 기본 Pygame beep 대체)
try:
    select_sound = pygame.mixer.Sound("select.wav")
    clear_sound = pygame.mixer.Sound("clear.wav")
except:
    select_sound = None
    clear_sound = None

# 숫자별 이미지 (없으면 색 블록 대체)
icons = {}
for i in range(1, 10):
    path = f"icons/{i}.png"
    if os.path.exists(path):
        img = pygame.image.load(path)
        img = pygame.transform.scale(img, (CELL_SIZE - 6, CELL_SIZE - 6))
        icons[i] = img

# 블록 클래스
class Block:
    def __init__(self, x, y, value):
        self.x, self.y = x, y
        self.value = value
        self.removing = False
        self.remove_scale = 1.0

    def draw(self, surface):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE + 100, CELL_SIZE, CELL_SIZE)
        if self.removing:
            scale = int(CELL_SIZE * self.remove_scale)
            rect.inflate_ip(-(CELL_SIZE - scale), -(CELL_SIZE - scale))
        pygame.draw.rect(surface, GRAY, rect, border_radius=8)

        if self.value in icons:
            img = pygame.transform.scale(icons[self.value], (rect.width - 6, rect.height - 6))
            surface.blit(img, (rect.x + 3, rect.y + 3))
        else:
            text = font.render(str(self.value), True, BLACK)
            surface.blit(text, text.get_rect(center=rect.center))

# 보드 생성
board = [[Block(x, y, random.randint(1, 9)) for y in range(ROWS)] for x in range(COLS)]

# 선택 상태
selected = []
lines = []

# 점수 & 타이머
score = 0
combo = 1
start_time = time.time()
game_time = 180  # 3분 제한

# 점수 이펙트
floating_scores = []

def add_floating_score(x, y, value):
    floating_scores.append([x, y, str(value), 60])

# 결과 저장
def save_result(final_score):
    with open("results.txt", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} 점수: {final_score}\n")

running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)
    elapsed = int(time.time() - start_time)
    remaining = max(0, game_time - elapsed)

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_result(score)
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if my >= 100:
                gx, gy = mx // CELL_SIZE, (my - 100) // CELL_SIZE
                if 0 <= gx < COLS and 0 <= gy < ROWS:
                    block = board[gx][gy]
                    if block not in selected:
                        selected.append(block)
                        if select_sound: select_sound.play()
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if my >= 100:
                    gx, gy = mx // CELL_SIZE, (my - 100) // CELL_SIZE
                    if 0 <= gx < COLS and 0 <= gy < ROWS:
                        block = board[gx][gy]
                        if block not in selected:
                            selected.append(block)
                            if select_sound: select_sound.play()
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected:
                total = sum(b.value for b in selected)
                if total == 10:
                    gained = 10 * combo
                    score += gained
                    add_floating_score(selected[-1].x * CELL_SIZE, selected[-1].y * CELL_SIZE, f"+{gained}")
                    for b in selected:
                        b.removing = True
                    if clear_sound: clear_sound.play()
                    combo += 1
                else:
                    combo = 1
                selected = []

    # 블록 그리기
    for x in range(COLS):
        for y in range(ROWS):
            b = board[x][y]
            if b:
                if b.removing:
                    b.remove_scale -= 0.1
                    if b.remove_scale <= 0:
                        board[x][y] = Block(x, y, random.randint(1, 9))
                b.draw(screen)

    # 선택된 블록 강조 + 라인 연결
    for i, b in enumerate(selected):
        rect = pygame.Rect(b.x * CELL_SIZE, b.y * CELL_SIZE + 100, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, BLUE, rect, 3, border_radius=8)
        if i > 0:
            prev = selected[i - 1]
            pygame.draw.line(screen, RED,
                             (prev.x * CELL_SIZE + CELL_SIZE // 2, prev.y * CELL_SIZE + 100 + CELL_SIZE // 2),
                             (b.x * CELL_SIZE + CELL_SIZE // 2, b.y * CELL_SIZE + 100 + CELL_SIZE // 2), 4)

    # 점수/타이머 표시
    score_text = font.render(f"점수: {score}", True, BLACK)
    time_text = font.render(f"남은 시간: {remaining}", True, BLACK)
    combo_text = font.render(f"콤보: x{combo}", True, RED if combo > 1 else BLACK)
    screen.blit(score_text, (20, 20))
    screen.blit(time_text, (20, 60))
    screen.blit(combo_text, (200, 20))

    # 점수 이펙트
    for fs in floating_scores[:]:
        x, y, text, life = fs
        img = font.render(text, True, GREEN)
        screen.blit(img, (x, y - (60 - life)))
        fs[3] -= 1
        if fs[3] <= 0:
            floating_scores.remove(fs)

    pygame.display.flip()
    clock.tick(60)

    if remaining <= 0:
        save_result(score)
        running = False

pygame.quit()

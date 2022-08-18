import random
import sys
from typing import Tuple
import pygame
from pygame.locals import *
import time

# 定数扱い
SURFACE = Rect(0, 0, 660, 660) # 画面サイズ(X軸,Y軸,横,縦)
F_RATE  = 60                   # フレームレート
RGB_WHITE = (255, 255, 255)

class BasicSprite(pygame.sprite.Sprite):
    """基本スプライト
    """
    def __init__(self, filename, x, y, size):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load(filename).convert_alpha()

        self.image = pygame.transform.scale(img, size)
        self.rect = Rect(x - self.w * 0.5, y - self.h * 0.5, self.w, self.h)

    @property
    def w(self):
        return self.image.get_width()

    @property
    def h(self):
        return self.image.get_height()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def move(self, surface: pygame.Surface, pos):
        self.rect.x = pos[0] - self.w * 0.5
        self.rect.y = pos[1] - self.h * 0.5
    
    def collide_pos(self, pos) -> bool:
        return self.rect.collidepoint(pos)

class TargetSprite(pygame.sprite.Sprite):
    """ターゲットスプライト

    手掛かり刺激

    ディスプレイを9等分した大きさ
    手掛かり刺激の表示はその中心
    """
    def __init__(self, filename, size, display_size):
        pygame.sprite.Sprite.__init__(self)
        
        self.target_rect = Rect(0, 0, display_size[0] / 3, display_size[1] / 3)

        img = pygame.image.load(filename).convert_alpha()

        self.image = pygame.transform.scale(img, size)
        self.image_rect = Rect(0, 0, self.iw, self.ih)

        self.direct_dic = { 1: (0, 0), 2: (220, 0), 3: (440, 0),
                            4: (0, 220), 5: (440, 220),
                            6: (0, 440), 7: (220, 440), 8: (440, 440) }
        self.direction = 1

    @property
    def iw(self):
        return self.image.get_width()

    @property
    def ih(self):
        return self.image.get_height()

    def set_direction(self):
        self.direction = random.randint(1, 8)

    def random_draw(self, surface: pygame.Surface):
        self.target_rect.x = self.direct_dic[self.direction][0]
        self.target_rect.y = self.direct_dic[self.direction][1]
        self.image_rect.x = self.target_rect.centerx - self.iw * 0.5
        self.image_rect.y = self.target_rect.centery - self.ih * 0.5
        surface.blit(self.image, self.image_rect)

    def collide_pos(self, pos) -> bool:
        return self.target_rect.collidepoint(pos)

class GazeTask(object):
    def __init__(self) -> None:
        # 画面初期化
        pygame.init()
        self.surface = pygame.display.set_mode(SURFACE.size)
        pygame.display.set_caption("GAZE TASK")              # タイトルバーに表示する文字

        # スプライトを作成
        self.start_point = BasicSprite("blue.png", SURFACE.centerx, SURFACE.centery, (30, 30))
        self.gaze = BasicSprite("eye.png", 200, 200, (100, 50))
        self.target = TargetSprite("white.png", (20, 20), SURFACE.size)

        self.font = pygame.font.Font('IPAexfont00401\ipaexg.ttf', 20)               # フォントの設定

        # 時間オブジェクト生成
        self.clock = pygame.time.Clock()

        self.score = 0
        self.assist = False
        self._motion_init()

    def reset(self):
        self.game_start = False
        self.time_start = 0.0
        self.time_past = 0.0

    def _motion_init(self):
        self.obs_startp = 0
        self.obs_targetp = 0
        self.reward = 0
        self.done = False
        self.text = ""

    def draw(self):
        # フレームレート設定
        self.clock.tick(F_RATE)

        # 背景色設定
        self.surface.fill((0,0,0))

        if (not self.game_start):
            txt_start = self.font.render("視線（マウスカーソル）を注視点に合わせたらスタートです。", True, RGB_WHITE)
            self.surface.blit(txt_start, [SURFACE.centerx - txt_start.get_width() * 0.5, SURFACE.centery - 50])

        if (self.obs_startp > 0):
            self.start_point.draw(self.surface)

        if (self.obs_targetp > 0):
            self.target.random_draw(self.surface)

        if (self.done):
            txt_done = self.font.render(self.text, True, RGB_WHITE)
            self.surface.blit(txt_done, [SURFACE.centerx - txt_done.get_width() * 0.5, SURFACE.centery - 50])

        # スコア表示
        txt_score = self.font.render("SCORE: " + str(self.score), True, RGB_WHITE)
        self.surface.blit(txt_score, [440, 0])

        if (self.assist):
            txt_time = self.font.render("{:.1f}".format(self.time_past), True, RGB_WHITE)
            self.surface.blit(txt_time, [0, 0])

            pygame.draw.line(self.surface, RGB_WHITE, (0, 220), (660, 220), 1)
            pygame.draw.line(self.surface, RGB_WHITE, (0, 440), (660, 440), 1)
            pygame.draw.line(self.surface, RGB_WHITE, (220, 0), (220, 660), 1)
            pygame.draw.line(self.surface, RGB_WHITE, (440, 0), (440, 660), 1)

        # 視線表示
        self.gaze.draw(self.surface)

        # 画面更新
        pygame.display.update()

        if (self.done):
            time.sleep(0.5)

    def motion(self, action) -> Tuple[int, int, float, bool]:
        """
        Retuens:
            observation start point  [観察] 注視点表示 0 / 1 (0: 表示なし)
                ┏━━━┳━━━┳━━━┓
                ┃   ┃   ┃   ┃
                ┣━━━╋━━━╋━━━┫
                ┃   ┃0/1┃   ┃
                ┣━━━╋━━━╋━━━┫
                ┃   ┃   ┃   ┃
                ┗━━━┻━━━┻━━━┛
            observation target point [観察] 手掛かり刺激表示 0 ~ 8 (0: 表示なし)
                ┏━━━┳━━━┳━━━┓
                ┃ 1 ┃ 2 ┃ 3 ┃
                ┣━━━╋━━━╋━━━┫
                ┃ 4 ┃   ┃ 5 ┃
                ┣━━━╋━━━╋━━━┫
                ┃ 6 ┃ 7 ┃ 8 ┃
                ┗━━━┻━━━┻━━━┛
            reward                   報酬
            done                     終了フラグ
        """
        (x, y) = action
        self._motion_init()

        if (self.game_start):
            self.time_past = time.perf_counter() - self.time_start
        elif (self.start_point.collide_pos((x, y))):
            self.game_start = True
            self.time_start = time.perf_counter()
            self.target.set_direction()
            self.reward = 1

        # 注視期間 (0.0 ~ 1.0)

        # 手がかり刺激期間 (1.0 ~ 1.5)
        if (1.0 <= self.time_past and self.time_past <= 1.5):
            self.obs_targetp = self.target.direction

            if (self.target.collide_pos((x, y))):
                self.text = "手がかり刺激に目を逸らしました"
                self.reward = 1
                self.done = True

        # 遅延期間 (1.5 ~ 4.5)

        # 注視点表示 (~ 4.5)
        if (self.time_past < 4.5):
            self.obs_startp = 1

            if (self.game_start and not self.start_point.collide_pos((x, y)) and self.reward == 0):
                self.text = "目を逸らしました"
                self.reward = -1
                self.done = True
                
        # 終了
        elif (self.time_past > 5.0):
            self.text = "タイムオーバー"
            self.done = True

        # 反応期間 (4.5 ~ 5.0)
        else:
            if (self.target.collide_pos((x, y))):
                self.text = "報酬 +10"
                self.reward = 10
                self.done = True

        # 視線移動
        self.gaze.move(self.surface, (x, y))

        # スコア（報酬計）
        self.score += self.reward

        return [self.obs_startp, self.obs_targetp, self.reward, self.done]

    def exit(self):
        pygame.quit()
        sys.exit()


def main():
    gaze_task = GazeTask()
    gaze_task.reset()
    (x, y) = (0, 0)

    while True:
        [obs_s, obs_t, reward, done] = gaze_task.motion((x, y))

        gaze_task.draw()

        # 次のゲーム
        if (done):
            gaze_task.reset()
            (x, y) = (0, 0)

        # イベント処理
        for event in pygame.event.get():
            if (event.type == MOUSEMOTION):
                x, y = event.pos
            # 終了処理
            if event.type == QUIT:
                gaze_task.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gaze_task.exit()
                elif event.key == K_a:
                    if (gaze_task.assist):
                        gaze_task.assist = False
                    else:
                        gaze_task.assist = True

if __name__ == "__main__":
    main()

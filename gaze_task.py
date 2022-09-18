import random
import sys
from typing import Tuple
import pygame
from pygame.locals import *
import time

# 定数扱い
SURFACE = Rect(0, 0, 660, 660) # 画面サイズ(X軸,Y軸,横,縦)
F_RATE  = 20                   # フレームレート
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

    ディスプレイを9等分した中心以外に表示
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
        self.move()

    def move(self):
        self.target_rect.x = self.direct_dic[self.direction][0]
        self.target_rect.y = self.direct_dic[self.direction][1]
        self.image_rect.x = self.target_rect.centerx - self.iw * 0.5
        self.image_rect.y = self.target_rect.centery - self.ih * 0.5

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.image_rect)

    def collide_pos(self, pos) -> bool:
        return self.target_rect.collidepoint(pos)

class GazeTask(object):
    def __init__(self, human_senses = True) -> None:
        # 画面初期化
        pygame.init()
        self.surface = pygame.display.set_mode(SURFACE.size)
        pygame.display.set_caption("GAZE TASK")              # タイトルバーに表示する文字

        # スプライトを作成
        self.start_point = BasicSprite("blue.png", SURFACE.centerx, SURFACE.centery, (30, 30))
        self.gaze = BasicSprite("eye.png", 200, 200, (100, 50))
        self.target = TargetSprite("white.png", (20, 20), SURFACE.size)

        self.font = pygame.font.Font('IPAexfont00401/ipaexg.ttf', 20)               # フォントの設定

        self.total_score = 0
        self.assist = False
        self._motion_init()

        if (human_senses):
            self.clock = pygame.time.Clock()
            self.use_time = True
        else:
            self.clock = None
            self.use_time = False

    def reset(self):
        self.game_start = False
        self.time_start = 0
        self.time_past = 0

    def set_time_start(self):
        # if (self.use_time):
        #     self.time_start = pygame.time.get_ticks()
        # else:
        self.time_start = 0

    def set_time_past(self):
        # if (self.use_time):
        #     self.time_past = pygame.time.get_ticks() - self.time_start
        # else:
        self.time_past += int(1000 / F_RATE)

    def _motion_init(self):
        self.obs_startp = 0
        self.obs_targetp = 0
        self.score = 0
        self.done = False
        self.status = "playing"
        self.text = ""

    def draw(self):
        if (self.use_time):
            #self.clock.tick(F_RATE)
            self.clock.tick_busy_loop(F_RATE)

        # 背景色設定
        self.surface.fill((0,0,0))

        if (not self.game_start and not self.done):
            txt_start = self.font.render("視線（マウスカーソル）を注視点に合わせたらスタートです。", True, RGB_WHITE)
            self.surface.blit(txt_start, [SURFACE.centerx - txt_start.get_width() * 0.5, SURFACE.centery - 50])

        if (self.obs_startp > 0):
            self.start_point.draw(self.surface)

        if (self.obs_targetp > 0):
            self.target.draw(self.surface)

        if (self.done):
            txt_done = self.font.render(self.text, True, RGB_WHITE)
            self.surface.blit(txt_done, [SURFACE.centerx - txt_done.get_width() * 0.5, SURFACE.centery - 50])

        # スコア表示
        txt_total_score = self.font.render("SCORE: " + str(self.total_score), True, RGB_WHITE)
        self.surface.blit(txt_total_score, [440, 0])

        if (self.assist):
            txt_time = self.font.render(str(self.time_past), True, RGB_WHITE)
            self.surface.blit(txt_time, [0, 0])

            pygame.draw.line(self.surface, RGB_WHITE, (0, 220), (660, 220), 1)
            pygame.draw.line(self.surface, RGB_WHITE, (0, 440), (660, 440), 1)
            pygame.draw.line(self.surface, RGB_WHITE, (220, 0), (220, 660), 1)
            pygame.draw.line(self.surface, RGB_WHITE, (440, 0), (440, 660), 1)

        # 視線表示
        self.gaze.draw(self.surface)

        # 画面更新
        #pygame.display.flip()
        pygame.display.update()

        if (self.done):
            if (self.use_time):
                #pygame.time.wait(500)
                pygame.time.delay(500)

    def event_clear(self):
        # for event in pygame.event.get():
        #     pass
        pygame.event.clear()

    def motion(self, action) -> Tuple[int, int, float, bool, str]:
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
            score                    点数
            done                     終了フラグ
            status                   状態
        """
        (x, y) = action
        self._motion_init()

        if (self.game_start):
            self.set_time_past()
        elif (self.start_point.collide_pos((x, y))):
            self.game_start = True
            self.set_time_start()
            self.target.set_direction()
        else:
            self.status = "ready"

        # 注視期間 (0.0 ~ 1.0)

        # 手がかり刺激期間 (1.0 ~ 1.5)
        if (1000 <= self.time_past and self.time_past <= 1500):
            self.obs_targetp = self.target.direction

            if (self.target.collide_pos((x, y))):
                self.text = "手がかり刺激に目を逸らしました"
                self.score = 10
                self.status = "look_away"
                self.done = True

        # 遅延期間 (1.5 ~ 4.5)

        # 注視点表示 (~ 4.5)
        if (self.time_past < 4500):
            self.obs_startp = 1

            if (self.game_start and not self.done):
                if (self.start_point.collide_pos((x, y))):
                    self.status = "on_center"
                else:
                    self.text = "目を逸らしました"
                    self.status = "look_away"
                    self.done = True
                
        # 終了
        elif (self.time_past > 5000):
            self.text = "タイムオーバー"
            self.status = "time_over"
            self.done = True

        # 反応期間 (4.5 ~ 5.0)
        else:
            self.status = "reaction"
            
            if (self.target.collide_pos((x, y))):
                self.text = "クリアー！ 100 点"
                self.score = 100
                self.status = "clear"
                self.done = True

        # 視線移動
        self.gaze.move(self.surface, (x, y))

        # スコア計
        self.total_score += self.score

        return [self.obs_startp, self.obs_targetp, self.score, self.done, self.status]

    def exit(self):
        pygame.quit()
        sys.exit()


def main():
    gaze_task = GazeTask(True)
    gaze_task.reset()
    (x, y) = (0, 0)

    while True:
        [obs_s, obs_t, score, done, status] = gaze_task.motion((x, y))

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

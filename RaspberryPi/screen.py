import pygame
import pygame.gfxdraw
from recordclass import recordclass
from colors import *
from shapes import *
from fonts import *

XYPoint = recordclass("XYPoint", "x y")

class Screen:
    def __init__(self, screen, scoreTracker):
        self.__screen = screen
        self.__scoreTracker = scoreTracker
        self.__headerHeight = 160
        self.__margin = 10

        self.__lastTotalArea = 0, 0, 0, 0
        self.__lastPlayerCountAreas = [(0, 0, 0, 0), (0, 0, 0, 0)]
        self.__lastPlayerScoreAreas = [(0, 0, 0, 0), (0, 0, 0, 0)]
        self.__lastPlayerTotalScoreAreas = [(0, 0, 0, 0), (0, 0, 0, 0)]

        self._register_components()
        self._prerender()

    def _register_components(self):
        self.__logo = pygame.image.load("images/logo.png").convert_alpha()
        self.__headerLbl = HEADER_FONT.render("ENTS Plinko", 1, PRIMARY_HEADER_TEXT_COLOR)

    def _prerender(self):
        self.__screen.fill(BACKGROUND_COLOR)
        sr = self.__screen.get_rect()
        centerX = sr.width / 2

        x = self.__margin
        y = self.__margin
        w = 119
        h = 150
        self.__screen.blit(self.__logo, (x, y, w, h))
        self.__screen.blit(self.__headerLbl, (x + w + self.__margin, -self.__margin)) # negative because of the font
        headerBottom = h + y

        self._render_totals()

        # player area (ascii design, rough):
        # +---------+  +------+
        # | PLR 1  /  /   SCR |
        # | SCR   /  /  PLR 2 |
        # +------+  +---------+

        # player area 1 (left)
        points = [
            [self.__margin, headerBottom + self.__margin], # top left
            [self.__margin, sr.height - self.__margin], # bottom left
            [(centerX - 100) - self.__margin, sr.height - self.__margin], # bottom right
            [(centerX + 100) - self.__margin, headerBottom + self.__margin] # top right
        ]
        pygame.gfxdraw.aapolygon(self.__screen, points, WIDGET_BACKGROUND_COLOR1)
        pygame.gfxdraw.filled_polygon(self.__screen, points, WIDGET_BACKGROUND_COLOR1)

        # player area 2 (right)
        points = [
            [(centerX + 100) + self.__margin, headerBottom + self.__margin], # top left
            [(centerX - 100) + self.__margin, sr.height - self.__margin], # bottom left
            [sr.width - self.__margin, sr.height - self.__margin], # bottom right
            [sr.width - self.__margin, headerBottom + self.__margin] # top right
        ]
        pygame.gfxdraw.aapolygon(self.__screen, points, WIDGET_BACKGROUND_COLOR2)
        pygame.gfxdraw.filled_polygon(self.__screen, points, WIDGET_BACKGROUND_COLOR2)

        # draw "total points" for player areas
        lbl = LEADERBOARD_RANK_FONT.render("Total Points", 1, PRIMARY_TEXT_COLOR)
        self.__screen.blit(lbl, (self.__margin * 2, sr.height - 160)) # left side
        self.__screen.blit(lbl, (sr.width - (self.__margin * 2) - lbl.get_rect().width, self.__headerHeight + (self.__margin * 2) + 80)) # right side

        # draw "total players" for player areas
        lbl = LEADERBOARD_RANK_FONT.render("Total Players", 1, PRIMARY_TEXT_COLOR)
        self.__screen.blit(lbl, ((centerX - 100) - (self.__margin * 2) - lbl.get_rect().width, sr.height - 160)) # left side
        self.__screen.blit(lbl, ((centerX + 100) + self.__margin, self.__headerHeight + (self.__margin * 2) + 80)) # right side

        self._render_leaderboard()
        self._render_player(0, 0)
        self._render_player(1, 0)

        pygame.display.flip()

    def render(self, p1score, p2score):
        dirty = []

        d = self._render_player(0, p1score)
        for a in d: dirty.append(a)

        d = self._render_player(1, p2score)
        for a in d: dirty.append(a)

        d = self._render_totals()
        for a in d: dirty.append(a)

        d = self._render_leaderboard()
        for a in d: dirty.append(a)

        pygame.display.update(dirty)

    def _render_player(self, playerIndex, score):
        # prepare dirty
        dirty = []
        dirty.append(self.__lastPlayerScoreAreas[playerIndex])
        dirty.append(self.__lastPlayerTotalScoreAreas[playerIndex])
        dirty.append(self.__lastPlayerCountAreas[playerIndex])
        # clear area
        plColor = WIDGET_BACKGROUND_COLOR1
        if playerIndex == 1: plColor = WIDGET_BACKGROUND_COLOR2
        for rect in dirty:
            r = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
            pygame.draw.rect(self.__screen, plColor, r.inflate(0, r.height * -0.25)) # correct for font height
        # prepare labels
        scoreLbl = PLAYER_SCORE_FONT.render(str(score), 1, SCORE_TEXT_COLOR)
        pointsLbl = LEADERBOARD_SCORE_FONT.render(str(self.__scoreTracker.playerScores[playerIndex]), 1, PRIMARY_TEXT_COLOR)
        countLbl = LEADERBOARD_SCORE_FONT.render(str(self.__scoreTracker.gameCounts[playerIndex]), 1, PRIMARY_TEXT_COLOR)
        # calculate label positions
        sr = self.__screen.get_rect()
        scorePos = XYPoint(x=0, y=0)
        pointsPos = XYPoint(x=0, y=0)
        countPos = XYPoint(x=0, y=0)
        scoreRect = scoreLbl.get_rect()
        pointsRect = pointsLbl.get_rect()
        countRect = countLbl.get_rect()
        if playerIndex == 0: # left side
            scorePos.x = self.__margin * 6
            scorePos.y = self.__headerHeight + (self.__margin * 8) - 100
            pointsPos.x = self.__margin * 2
            pointsPos.y = sr.height - self.__margin - pointsRect.height
            countPos.x = (((sr.width / 2) - 100) - self.__margin) - countRect.width - self.__margin
            countPos.y = sr.height - self.__margin - countRect.height
        else: # right side
            scorePos.x = sr.width - (self.__margin * 6) - scoreRect.width
            scorePos.y = sr.height - (self.__margin * 8) - scoreRect.height + 100 + self.__margin
            pointsPos.x = sr.width - self.__margin - pointsRect.width - self.__margin
            pointsPos.y = self.__headerHeight + self.__margin
            countPos.x = (((sr.width / 2) + 100) - self.__margin) + self.__margin + self.__margin
            countPos.y = self.__headerHeight + self.__margin
        # render labels
        self.__screen.blit(scoreLbl, (scorePos.x, scorePos.y))
        self.__screen.blit(pointsLbl, (pointsPos.x, pointsPos.y))
        self.__screen.blit(countLbl, (countPos.x, countPos.y))
        # append dirty states
        self.__lastPlayerScoreAreas[playerIndex] = (scorePos.x, scorePos.y, scoreRect.width, scoreRect.height)
        self.__lastPlayerTotalScoreAreas[playerIndex] = (pointsPos.x, pointsPos.y, pointsRect.width, pointsRect.height)
        self.__lastPlayerCountAreas[playerIndex] = (countPos.x, countPos.y, countRect.width, countRect.height)
        dirty.append(self.__lastPlayerScoreAreas[playerIndex])
        dirty.append(self.__lastPlayerTotalScoreAreas[playerIndex])
        dirty.append(self.__lastPlayerCountAreas[playerIndex])
        return dirty

    def _render_totals(self):
        dirty = []
        dirty.append(self.__lastTotalArea)
        for r in dirty:
            pygame.draw.rect(self.__screen, BACKGROUND_COLOR, r)
        lbl = TOTALS_FONT.render("Total games played: " + str(self.__scoreTracker.totalGames), 1, MUTED_TEXT_COLOR)
        r = lbl.get_rect()
        sr = self.__screen.get_rect()
        pos = (sr.width - r.width - self.__margin, self.__margin)
        self.__lastTotalArea = (pos[0], pos[1], r.width, r.height)
        dirty.append(self.__lastTotalArea)
        self.__screen.blit(lbl, pos)
        return dirty

    def _render_leaderboard(self):
        dirty = []
        sr = self.__screen.get_rect()
        index = 1
        x = self.__margin
        y = self.__headerHeight + self.__margin
        h = 75
        w = (sr.width - self.__margin - self.__margin) / float(len(self.__scoreTracker.topScores))
        for score in self.__scoreTracker.topScores:
            rect = (x, y, w, h)
            aa_filled_rounded_rectangle(self.__screen, rect, WIDGET_BACKGROUND_COLOR1, 0.2)
            lbl = LEADERBOARD_RANK_FONT.render("#" + str(index), 1, MUTED_TEXT_COLOR)
            area = lbl.get_rect()
            lx = (x + w) - area.width - self.__margin - (self.__margin / 2)
            ly = (y + h) - area.height
            self.__screen.blit(lbl, (lx, ly))
            lbl = LEADERBOARD_SCORE_FONT.render(str(score[0]), 1, SCORE_TEXT_COLOR)
            lx = x + self.__margin + (self.__margin / 2)
            ly = y
            self.__screen.blit(lbl, (lx, ly))
            x = (index * w) + self.__margin
            index = index + 1
            dirty.append(rect)
        return dirty

import pygame
import sys
import threading
import time
from main import ConnectFourGame

# --- Layout & sizing ---
SQUARESIZE = 64  # smaller board
COL_COUNT = 7
ROW_COUNT = 6
RADIUS = int(SQUARESIZE / 2 - 4)

# toolbar and sidebar
# small gap at very top of the window (visual breathing room)
TOOLBAR_TOP_GAP = 8
# top indicator bar: make it large enough to show a full-size piece plus padding
TOOLBAR_PADDING_TOP = 8
TOOLBAR_PADDING_BOTTOM = 8
TOOLBAR_HEIGHT = RADIUS * 2 + TOOLBAR_PADDING_TOP + TOOLBAR_PADDING_BOTTOM
# make left and right outer gaps equal
RIGHT_MARGIN = 12
LEFT_MARGIN = RIGHT_MARGIN

# Layout: make board occupy 70% of content width and sidebar 30%.
# Compute an inner content width so the fixed board (COL_COUNT*SQUARESIZE)
# becomes 70% of that content; the remainder is the sidebar width.
CONTENT_WIDTH = int((COL_COUNT * SQUARESIZE) / 0.7)
SIDEBAR_WIDTH = CONTENT_WIDTH - (COL_COUNT * SQUARESIZE)

# compute window size
WIDTH = LEFT_MARGIN + CONTENT_WIDTH + RIGHT_MARGIN
HEIGHT = TOOLBAR_TOP_GAP + TOOLBAR_HEIGHT + ROW_COUNT * SQUARESIZE + TOOLBAR_TOP_GAP
SIZE = (WIDTH, HEIGHT)

FPS = 60

# small horizontal gap between board and sidebar
SIDEBAR_GAP = 18
# vertical gaps for sidebar (top and bottom) — match top/bottom to TOOLBAR_TOP_GAP
SIDEBAR_V_GAP = TOOLBAR_TOP_GAP
SIDEBAR_BOTTOM_GAP = TOOLBAR_TOP_GAP

# AI difficulty mapping: use get_ai_move(difficulty)
AI_DEPTH = 5

# animation settings
DROP_SPEED = 1200  # pixels per second (larger = faster)

# Reset / toolbar button settings
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 12
BUTTON_COLOR = (40, 57, 75)      # slate
BUTTON_HOVER = (59, 89, 115)     # slightly lighter slate
BUTTON_TEXT_COLOR = (240, 248, 255)  # off-white

# small control button (for +/-)
SMALL_BTN_SIZE = 28
SMALL_BTN_COLOR = (60, 80, 100)
SMALL_BTN_HOVER = (85, 110, 140)
SMALL_BTN_TEXT = (240, 248, 255)

# tokens used by fourConnectAI
PLAYER_TOKEN = 'X'
AI_TOKEN = 'O'


def difficulty_name(depth: int) -> str:
    if depth <= 0:
        return 'Easy'
    if depth <= 3:
        return 'Medium'
    return 'Hard'


def draw_board(screen, board):
    # Only redraw the board area so toolbar and sidebar aren't overwritten during animation
    board_bg = (30, 41, 59)  # deep slate background for the board area
    board_x = LEFT_MARGIN
    board_y = TOOLBAR_TOP_GAP + TOOLBAR_HEIGHT
    board_w = COL_COUNT * SQUARESIZE
    board_h = ROW_COUNT * SQUARESIZE
    board_rect = pygame.Rect(board_x, board_y, board_w, board_h)
    pygame.draw.rect(screen, board_bg, board_rect)

    for c in range(COL_COUNT):
        for r in range(ROW_COUNT):
            rect = pygame.Rect(board_x + c * SQUARESIZE, board_y + r * SQUARESIZE, SQUARESIZE, SQUARESIZE)
            pygame.draw.rect(screen, (21, 101, 192), rect, border_radius=6)
            val = board[r][c]
            center = (board_x + int(c * SQUARESIZE + SQUARESIZE / 2), board_y + int(r * SQUARESIZE + SQUARESIZE / 2))
            if val == ' ':
                pygame.draw.circle(screen, (18, 27, 38), center, RADIUS)
            elif val == PLAYER_TOKEN:
                pygame.draw.circle(screen, (220, 78, 65), center, RADIUS)
            else:
                pygame.draw.circle(screen, (255, 215, 84), center, RADIUS)


def animate_drop(screen, game, col, token):
    # compute target row after placing
    for r in range(ROW_COUNT - 1, -1, -1):
        if game.board[r][col] == ' ':
            target_row = r
            break
    else:
        return

    start_y = TOOLBAR_TOP_GAP + TOOLBAR_HEIGHT + int(SQUARESIZE / 2)
    end_y = TOOLBAR_TOP_GAP + TOOLBAR_HEIGHT + int(target_row * SQUARESIZE + SQUARESIZE / 2)
    distance = end_y - start_y
    if distance <= 0:
        game.drop_piece(col, token)
        return

    duration = max(0.04, distance / DROP_SPEED)
    steps = max(1, int(duration * FPS))
    board_x = LEFT_MARGIN
    for i in range(1, steps + 1):
        t = i / steps
        y = int(start_y + (end_y - start_y) * t)
        draw_board(screen, game.board)
        x = int(board_x + col * SQUARESIZE + SQUARESIZE / 2)
        color = (220, 78, 65) if token == PLAYER_TOKEN else (255, 215, 84)
        pygame.draw.circle(screen, color, (x, y), RADIUS)
        pygame.display.update()
        pygame.time.delay(int(1000 / FPS))

    game.drop_piece(col, token)


def draw_toolbar(screen, font):
    # Draw a narrow top indicator bar (only above the board area)
    toolbar_bg = (20, 28, 36)
    board_x = LEFT_MARGIN
    board_w = COL_COUNT * SQUARESIZE
    pygame.draw.rect(screen, toolbar_bg, (board_x, TOOLBAR_TOP_GAP, board_w, TOOLBAR_HEIGHT))
    # indicator drawing (hover circle and landing row) is handled by passing hover_col via global state
    # The actual drawing of the hover circle is performed in the main loop where hover_col is known


def draw_sidebar(screen, font, ai_thinking, winner, depth):
    sidebar_x = LEFT_MARGIN + COL_COUNT * SQUARESIZE + SIDEBAR_GAP
    total_h = TOOLBAR_HEIGHT + ROW_COUNT * SQUARESIZE
    w = SIDEBAR_WIDTH - 24
    # panel should span the toolbar + board area; top/bottom gaps are handled by SIDEBAR_V_GAP
    panel_rect = pygame.Rect(sidebar_x, SIDEBAR_V_GAP, w, total_h)
    pygame.draw.rect(screen, (22, 28, 36), panel_rect, border_radius=8)

    pad = 12
    content_left = panel_rect.left + pad
    content_w = panel_rect.width - pad * 2

    # Prepare control sizes
    btn_w = min(BUTTON_WIDTH, content_w)
    btn_h = BUTTON_HEIGHT
    level_btn_h = 34
    level_btn_w = content_w - 12
    labels = [('Easy', 0), ('Medium', 3), ('Hard', 5)]

    # Compute total height of controls (reset + gap + levels)
    controls_height = btn_h + 16 + len(labels) * (level_btn_h + 8)
    # center controls vertically inside the panel
    start_y = panel_rect.top + (panel_rect.height - controls_height) // 2

    # Reset button (centered horizontally)
    btn_x = content_left + (content_w - btn_w) // 2
    btn_y = start_y
    reset_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    mx, my = pygame.mouse.get_pos()
    color = BUTTON_HOVER if reset_rect.collidepoint(mx, my) else BUTTON_COLOR
    pygame.draw.rect(screen, color, reset_rect, border_radius=8)
    text_surf = font.render('Reset', True, BUTTON_TEXT_COLOR)
    screen.blit(text_surf, text_surf.get_rect(center=reset_rect.center))

    # Difficulty buttons stacked below reset
    base_y = btn_y + btn_h + 16
    level_rects = {}
    for i, (lbl, dval) in enumerate(labels):
        y = base_y + i * (level_btn_h + 8)
        r = pygame.Rect(content_left + 6, y, level_btn_w, level_btn_h)
        if dval == 0 and depth <= 0:
            colr = (70, 100, 130)
        elif dval == 3 and 1 <= depth <= 3:
            colr = (70, 100, 130)
        elif dval == 5 and depth > 3:
            colr = (70, 100, 130)
        else:
            colr = (48, 62, 78)
        hover = (85, 110, 140) if r.collidepoint(mx, my) else colr
        pygame.draw.rect(screen, hover, r, border_radius=6)
        lbl_s = font.render(lbl, True, BUTTON_TEXT_COLOR)
        screen.blit(lbl_s, lbl_s.get_rect(center=r.center))
        level_rects[lbl.lower()] = (r, dval)

    # Result label + message immediately after the Hard button and centered
    res_font = pygame.font.SysFont("monospace", 22)
    label = res_font.render('Result:', True, BUTTON_TEXT_COLOR)
    # determine message and color
    if winner is not None:
        if winner == 'You':
            msg = 'You win'
            msg_color = (88, 214, 141)
        elif winner == 'AI':
            msg = 'AI wins'
            msg_color = (240, 94, 94)
        else:
            msg = 'Draw'
            msg_color = BUTTON_TEXT_COLOR
    else:
        msg = '—'
        msg_color = BUTTON_TEXT_COLOR
    msg_surf = res_font.render(msg, True, msg_color)

    # Prefer placing the result directly after the Hard button
    gap_after = 12
    hard_rect = level_rects.get('hard', (None, None))[0] if 'hard' in level_rects else None
    center_x = panel_rect.left + panel_rect.width // 2
    if hard_rect is not None:
        label_top = hard_rect.bottom + gap_after
    else:
        # fallback: place near the center of the panel
        label_top = panel_rect.top + pad

    # compute centers for blit (pygame wants center coords for centered blits)
    label_center = (center_x, label_top + label.get_height() // 2)
    msg_top = label_top + label.get_height() + 6
    msg_center = (center_x, msg_top + msg_surf.get_height() // 2)
    screen.blit(label, label.get_rect(center=label_center))
    screen.blit(msg_surf, msg_surf.get_rect(center=msg_center))

    rects = {'reset': reset_rect}
    for k, (r, d) in level_rects.items():
        rects[k] = r
    return rects


def run_gui():
    pygame.init()
    global AI_DEPTH
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect Four - AI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 32)

    game = ConnectFourGame(rows=ROW_COUNT, cols=COL_COUNT)
    game_over = False
    turn = 0  # 0 player, 1 AI
    winner = None  # 'You', 'AI', 'Draw' or None
    draw_board(screen, game.board)

    ai_thinking = False
    ai_move_col = None
    animating = False
    hover_col = None
    while True:
        side_btns = draw_sidebar(screen, font, ai_thinking, winner, AI_DEPTH)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and winner is not None:
                    game.reset_board()
                    game_over = False
                    turn = 0
                    winner = None
                    draw_board(screen, game.board)
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                board_x = LEFT_MARGIN
                board_y = TOOLBAR_TOP_GAP + TOOLBAR_HEIGHT
                board_w = COL_COUNT * SQUARESIZE
                # update hover_col only when mouse is over the board horizontally
                if board_x <= mx <= board_x + board_w and board_y <= my <= board_y + ROW_COUNT * SQUARESIZE:
                    hover_col = (mx - board_x) // SQUARESIZE
                else:
                    hover_col = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # sidebar reset
                if side_btns['reset'].collidepoint(mx, my):
                    game.reset_board()
                    game_over = False
                    turn = 0
                    winner = None
                    draw_board(screen, game.board)
                    continue

                # sidebar difficulty
                if 'easy' in side_btns and side_btns['easy'].collidepoint(mx, my):
                    AI_DEPTH = 0
                    continue
                if 'medium' in side_btns and side_btns['medium'].collidepoint(mx, my):
                    AI_DEPTH = 3
                    continue
                if 'hard' in side_btns and side_btns['hard'].collidepoint(mx, my):
                    AI_DEPTH = 5
                    continue

                # prevent input when animating, when not player's turn, or when game over/winner
                if animating or turn != 0 or game_over or winner is not None:
                    continue

                # map click to board col
                board_x = LEFT_MARGIN
                board_y = TOOLBAR_TOP_GAP + TOOLBAR_HEIGHT
                if my < board_y or my > board_y + ROW_COUNT * SQUARESIZE:
                    continue
                col = (mx - board_x) // SQUARESIZE
                if col in game.get_valid_moves():
                    animating = True
                    turn = 1
                    animate_drop(screen, game, col, PLAYER_TOKEN)
                    animating = False
                    if game.check_winner(PLAYER_TOKEN):
                        winner = 'You'
                        game_over = True
                    draw_board(screen, game.board)

        # draw top indicator bar and landing info when hovering over a column
        draw_toolbar(screen, font)
        if hover_col is not None and not animating and not game_over:
            # compute landing row for this column
            valid_moves = game.get_valid_moves()
            if hover_col in valid_moves:
                # find target row (lowest empty)
                for rr in range(ROW_COUNT - 1, -1, -1):
                    if game.board[rr][hover_col] == ' ':
                        landing_row = rr
                        break
                else:
                    landing_row = None
                if landing_row is not None:
                    # draw preview circle in the toolbar area above the correct column
                    preview_x = LEFT_MARGIN + int(hover_col * SQUARESIZE + SQUARESIZE / 2)
                    preview_y = TOOLBAR_PADDING_TOP + RADIUS
                    # use the same radius as board pieces and add gentle outline
                    pygame.draw.circle(screen, (200, 80, 70), (preview_x, preview_y), RADIUS)
                    pygame.draw.circle(screen, (18, 27, 38), (preview_x, preview_y), RADIUS, 2)

        # If it's AI's turn, start background computation (only once)
        if turn == 1 and not game_over and not ai_thinking and ai_move_col is None and not animating:
            ai_thinking = True

            def ai_job():
                nonlocal ai_thinking, ai_move_col
                time.sleep(0.05)
                if AI_DEPTH <= 0:
                    difficulty = 'Easy'
                elif AI_DEPTH <= 3:
                    difficulty = 'Medium'
                else:
                    difficulty = 'Hard'
                col = game.get_ai_move(difficulty)
                ai_move_col = col
                ai_thinking = False

            threading.Thread(target=ai_job, daemon=True).start()

        # If AI computed a move, animate it on the main thread
        if ai_move_col is not None and not game_over and not animating:
            animating = True
            animate_drop(screen, game, ai_move_col, AI_TOKEN)
            animating = False
            if game.check_winner(AI_TOKEN):
                winner = 'AI'
                game_over = True
            ai_move_col = None
            turn = 0
            draw_board(screen, game.board)

        if game.is_draw() and not game_over:
            winner = 'Draw'
            game_over = True

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    run_gui()

import pygame
from tkinter import Tk, Toplevel, Label, Entry, Button as TkButton
from config import *


class Button:
    def __init__(self, rect, text, font, action=None, debounce_ms=250):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.action = action
        self.is_hovered = False
        self.disabled = False
        self.debounce_ms = debounce_ms
        self.last_click_time = 0

    def draw(self, screen):
        color = (
            DISABLED_BUTTON_COLOR
            if self.disabled
            else BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        )
        text_color = DISABLED_TEXT_COLOR if self.disabled else BUTTON_TEXT_COLOR
        
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        
        if self.is_hovered and not self.disabled:
            pygame.draw.rect(screen, ACCENT_COLOR, self.rect, 2, border_radius=6)
        
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if self.disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                current_time = pygame.time.get_ticks()
                if current_time - self.last_click_time > self.debounce_ms:
                    self.last_click_time = current_time
                    if self.action:
                        self.action()
                    return True
        return False


class Slider:
    def __init__(self, rect, min_val, max_val, initial_val, font):
        self.rect, self.min_val, self.max_val, self.val, self.font = (
            pygame.Rect(rect),
            min_val,
            max_val,
            initial_val,
            font,
        )
        self.dragging = False
        self.thumb_radius = self.rect.height // 2 + 2
        self._update_thumb_pos()

    def _update_thumb_pos(self):
        ratio = (
            (self.val - self.min_val) / (self.max_val - self.min_val)
            if (self.max_val - self.min_val) != 0
            else 0
        )
        self.thumb_x = self.rect.x + ratio * self.rect.width

    def draw(self, screen):
        pygame.draw.rect(
            screen, SLIDER_BAR_COLOR, self.rect, border_radius=self.rect.height // 2
        )
        color = ACCENT_COLOR_LIGHT if hasattr(self, 'dragging') and self.dragging else SLIDER_THUMB_COLOR
        pygame.draw.circle(
            screen,
            color,
            (int(self.thumb_x), self.rect.centery),
            self.thumb_radius,
        )
        highlight_color = tuple(min(255, c + 40) for c in color)
        pygame.draw.circle(
            screen,
            highlight_color,
            (int(self.thumb_x), self.rect.centery),
            max(2, self.thumb_radius - 3),
        )

    def handle_event(self, event, on_change_callback=None):
        if event.type not in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ):
            return False
        pos = event.pos
        thumb_hitbox = pygame.Rect(
            0, 0, self.thumb_radius * 2.5, self.rect.height * 2.5
        )
        thumb_hitbox.center = (self.thumb_x, self.rect.centery)
        is_over_thumb = thumb_hitbox.collidepoint(pos)
        is_over_bar = self.rect.collidepoint(pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_over_bar or is_over_thumb:
                self.dragging = True
                self._set_value_from_mouse(pos[0], on_change_callback)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                if on_change_callback:
                    on_change_callback(self.val)
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._set_value_from_mouse(pos[0], on_change_callback)
                return True
        return False

    def _set_value_from_mouse(self, mouse_x, on_change_callback=None):
        if self.rect.width == 0:
            return
        self.val = self.min_val + ((mouse_x - self.rect.x) / self.rect.width) * (
            self.max_val - self.min_val
        )
        self.val = max(self.min_val, min(self.max_val, self.val))
        self._update_thumb_pos()
        if on_change_callback:
            on_change_callback(self.val)


class MusicProgressBar(Slider):
    def __init__(self, rect, font):
        super().__init__(rect, 0.0, 1.0, 0.0, font)
        self.thumb_radius = self.rect.height + 2

    def handle_event(self, event, on_seek_callback=None):
        if event.type not in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ):
            return False
        pos = event.pos
        is_over_bar = self.rect.collidepoint(pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_over_bar:
                self.dragging = True
                self._set_value_from_mouse(pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                if on_seek_callback:
                    on_seek_callback(self.val)
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._set_value_from_mouse(pos[0])
                return True
        return False

    def draw(self, screen, current_time, duration):
        if not self.dragging:
            self.val = current_time / duration if duration > 0 else 0
            self._update_thumb_pos()
        
        pygame.draw.rect(
            screen, SLIDER_BAR_COLOR, self.rect, border_radius=self.rect.height // 2
        )
        
        fill_rect = self.rect.copy()
        fill_rect.width = max(0, self.thumb_x - self.rect.x)
        if fill_rect.width > 0:
            pygame.draw.rect(
                screen, ACCENT_COLOR, fill_rect, border_radius=self.rect.height // 2
            )
        
        pygame.draw.circle(
            screen, 
            ACCENT_COLOR_LIGHT if self.dragging else ACCENT_COLOR, 
            (int(self.thumb_x), self.rect.centery), 
            self.thumb_radius
        )
        
        highlight_color = ACCENT_COLOR_LIGHT if self.dragging else (180, 180, 255)
        pygame.draw.circle(
            screen,
            highlight_color,
            (int(self.thumb_x), self.rect.centery),
            self.thumb_radius - 3,
        )


class InputBox:
    def __init__(self, rect, font, initial_text="", placeholder_text=""):
        self.rect, self.font, self.placeholder_text = (
            pygame.Rect(rect),
            font,
            placeholder_text,
        )
        (
            self.text,
            self.text_surface,
            self.is_scrolling,
            self.scroll_x,
            self.scroll_delay_start,
        ) = ("", None, False, 0, 0)
        self.SCROLL_DELAY_DURATION, self.SCROLL_SPEED = 2000, 30
        self.set_text(initial_text)

    def set_text(self, new_text):
        self.text, self.scroll_x, self.is_scrolling = new_text, 0, False
        display_text, text_color = (
            (self.text, INPUT_BOX_TEXT_COLOR)
            if self.text
            else (self.placeholder_text, (150, 150, 150))
        )
        text_width = self.font.size(display_text)[0]
        if text_width > self.rect.width - 20:
            self.is_scrolling, self.scroll_delay_start = True, pygame.time.get_ticks()
            self.text_surface = self.font.render(
                display_text + " " * 10 + display_text, True, text_color
            )
        else:
            self.text_surface = self.font.render(display_text, True, text_color)

    def update(self, dt):
        if (
            self.is_scrolling
            and pygame.time.get_ticks() - self.scroll_delay_start
            > self.SCROLL_DELAY_DURATION
        ):
            self.scroll_x += self.SCROLL_SPEED * dt
            if self.scroll_x > self.text_surface.get_width() / 2:
                self.scroll_x, self.scroll_delay_start = 0, pygame.time.get_ticks()

    def draw(self, screen):
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.rect, border_radius=5)
        pygame.draw.rect(screen, INPUT_BOX_BORDER_COLOR, self.rect, 2, border_radius=5)
        if not self.text_surface:
            return
        clip_rect = self.rect.inflate(-20, -10)
        if self.is_scrolling:
            screen.blit(
                self.text_surface,
                clip_rect.topleft,
                area=pygame.Rect(self.scroll_x, 0, clip_rect.width, clip_rect.height),
            )
        else:
            screen.blit(
                self.text_surface, self.text_surface.get_rect(center=self.rect.center)
            )


def ask_phone_path():
    root = Tk()
    root.withdraw()
    
    dialog = Toplevel(root)
    dialog.title("输入手机路径")
    dialog.geometry("700x150")
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - 350
    y = (dialog.winfo_screenheight() // 2) - 75
    dialog.geometry(f"700x150+{x}+{y}")
    
    result = {"path": None}
    
    Label(
        dialog,
        text="请输入或粘贴手机音乐文件夹的完整路径",
        font=("微软雅黑", 11),
        pady=20
    ).pack()
    
    entry = Entry(dialog, font=("Consolas", 10), width=80)
    entry.pack(padx=20, pady=5)
    entry.focus_set()
    
    def ok_clicked():
        result["path"] = entry.get()
        dialog.quit()
        dialog.destroy()
    
    def cancel_clicked():
        result["path"] = None
        dialog.quit()
        dialog.destroy()
    
    button_frame = Label(dialog)
    button_frame.pack(pady=15)
    
    TkButton(button_frame, text="确定", command=ok_clicked, width=10, font=("微软雅黑", 10)).pack(side="left", padx=10)
    TkButton(button_frame, text="取消", command=cancel_clicked, width=10, font=("微软雅黑", 10)).pack(side="left", padx=10)
    
    entry.bind('<Return>', lambda e: ok_clicked())
    entry.bind('<Escape>', lambda e: cancel_clicked())
    
    dialog.protocol("WM_DELETE_WINDOW", cancel_clicked)
    dialog.mainloop()
    
    root.destroy()
    return result["path"]


class Settings:
    APP_NAME = "Moonal Udhyog PVT. LTD. - IMS"
    COMPANY_NAME = "Moonal Udhyog PVT. LTD."
    COMPANY_ADDRESS = "Golbazar-4, Siraha, Nepal"
    COMPANY_PAN = "610338108"
    APP_DIR_NAME = "MoonalInvoiceApp"

    # ── Warm Light-Mode Golden Palette ──────────────────────────────
    COLORS = {
        # Primary Warm Gold
        "primary": "#C8963E",
        "primary_hover": "#D4A94E",
        "primary_pressed": "#B07D2F",
        "primary_light": "#FFF8E7",
        "gold_accent": "#92400E",

        # Sidebar & Navbar (LIGHT)
        "sidebar": "#FFFFFF",
        "sidebar_hover": "#FFF8E7",
        "sidebar_active": "#FFF3CD",
        "sidebar_border": "#F3E8D0",
        "sidebar_text": "#374151",
        "sidebar_text_active": "#92400E",
        "navbar": "#FFFFFF",
        "navbar_border": "#E5E7EB",

        # Content Area
        "bg": "#F9FAFB",
        "card": "#FFFFFF",
        "border": "#E5E7EB",

        # Text
        "text": "#1F2937",
        "text_light": "#FFFFFF",
        "secondary": "#6B7280",
        "muted": "#9CA3AF",

        # Functional
        "accent": "#C8963E",
        "danger": "#DC2626",
        "danger_hover": "#B91C1C",
        "success": "#16A34A",
        "success_bg": "#F0FDF4",
        "warning": "#F59E0B",
        "info": "#3B82F6",

        # Input
        "input_bg": "#F9FAFB",
        "input_border": "#D1D5DB",
        "input_focus": "#C8963E",

        # Misc
        "light_gray": "#F3F4F6",
        "divider": "#E5E7EB",
    }

    # ── Typography ────────────────────────────────────────────────────
    FONTS = {
        "h1": ("Segoe UI", 22, "bold"),
        "h2": ("Segoe UI", 17, "bold"),
        "h3": ("Segoe UI", 13, "bold"),
        "body": ("Segoe UI", 11),
        "body_bold": ("Segoe UI", 11, "bold"),
        "small": ("Segoe UI", 9),
        "small_bold": ("Segoe UI", 9, "bold"),
        "button": ("Segoe UI", 11, "bold"),
        "sidebar": ("Segoe UI", 10),
        "sidebar_bold": ("Segoe UI", 10, "bold"),
        "mono": ("Consolas", 10),
    }

    # ── Spacing ─────────────────────────────────────────────────────
    PADDINGS = {
        "xs": 4, "sm": 8, "md": 16,
        "lg": 24, "xl": 32, "xxl": 48,
    }

    # ── Dimensions ──────────────────────────────────────────────────
    SIDEBAR_WIDTH = 220
    NAVBAR_HEIGHT = 52
    CARD_RADIUS = 10
    INPUT_HEIGHT = 40
    BUTTON_RADIUS = 8
    DEFAULT_VAT_RATE = 13

    @classmethod
    def scale_for_screen(cls, screen_width):
        """Return (sidebar_width, font_scale) based on screen resolution."""
        if screen_width <= 1366:      # 12"-13" laptops
            return 190, 0
        elif screen_width <= 1600:     # 14"-15"
            return 220, 0
        elif screen_width <= 1920:     # 15"-16" FHD
            return 240, 1
        else:                          # 17"-18"+ QHD/4K
            return 260, 2

    @classmethod
    def get_fonts(cls, screen_width=1920):
        """Return font dict scaled for the screen."""
        _, bump = cls.scale_for_screen(screen_width)
        base = dict(cls.FONTS)
        if bump:
            for key in base:
                name, size, *style = base[key]
                base[key] = (name, size + bump, *style)
        return base

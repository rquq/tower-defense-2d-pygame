from core.constants import C

class InventoryItem:
    """Mô tả một vật phẩm cụ thể đang nằm trong kho đồ của người chơi."""

    def __init__(self, item_type, data):
        """Thiết lập các thông tin cơ bản cho vật phẩm."""
        self.item_type = item_type
        self.data = data
        self.name = ''
        self.color = (200, 200, 200)
        self.description = []
        if item_type == C.ItemType.GEM:
            self.name = data
            colors = {'FIRE': (255, 69, 0), 'ICE': (0, 191, 255), 'OVERCLOCK': (255, 215, 0)}
            self.color = colors.get(data, (200, 200, 200))
            self.description = [f'{data} GEM', 'Slots into turrets']
        elif item_type == C.ItemType.BEACON:
            self.name = data
            stats = C.BEACON_STATS[data]
            self.color = stats['color']
            self.description = [data.replace('_', ' '), stats['desc'], 'Place on grid']
        elif item_type == C.ItemType.STAT_CARD:
            self.name = data['name']
            card_colors = {'STRENGTH CARD': (255, 80, 80), 'AGILITY CARD': (80, 255, 80), 'VISION CARD': (80, 150, 255), 'PRECISION CARD': (255, 220, 80)}
            self.color = card_colors.get(self.name, (200, 100, 255))
            self.description = [self.name, data['desc'], 'Fits Powerup Slot']

    def get_tooltip_data(self, t):
        """Chuẩn bị các dòng văn bản mô tả để hiển thị thông tin vật phẩm."""
        lines = [f'--- {t(self.name).upper()} ---']
        if self.item_type == C.ItemType.BEACON:
            stats = C.BEACON_STATS[self.data]
            lines += [f"{t('DESCRIPTION')}: {t(stats['desc']).upper()}.", f"{t('USAGE')}: {t('BEACON_USAGE')}"]
        elif self.item_type == C.ItemType.GEM:
            gem_descs = {'FIRE': 'INFUSES BULLETS WITH SCORCHING ENERGY, ADDING +2 RAW ATK AND BURNING ENEMIES.', 'ICE': 'CHILLS ENEMIES ON HIT, REDUCING THEIR MOVEMENT SPEED BY 40%.', 'OVERCLOCK': 'FRANTICALLY OVERCLOCKS TURRET GEARS, INCREASING SPD BY 30%.'}
            desc = gem_descs.get(self.data, 'A MYSTERIOUS ELEMENTAL GEM.')
            lines += [f"{t('DESCRIPTION')}: {t(desc)}", f"{t('USAGE')}: {t('BUFF_USAGE')}"]
        elif self.item_type == C.ItemType.STAT_CARD:
            lines += [f"{t('DESCRIPTION')}: {t(self.data['desc']).upper()}.", f"{t('USAGE')}: {t('BLESSING_USAGE')}"]
        return lines
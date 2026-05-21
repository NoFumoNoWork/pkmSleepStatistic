"""界面文案（简体中文）。"""

APP_NAME = "宝可梦睡眠 · 技能触发记录"
APP_STARTED_HINT = (
    "应用已启动。主窗口应已显示；关闭窗口后会缩到托盘，"
    "按 Ctrl+Alt+P 可再次打开。"
)

# 托盘
TRAY_OPEN = "打开主窗口"
TRAY_EXIT = "退出"
TRAY_STARTED = "已在系统托盘运行。按 Ctrl+Alt+P 可显示窗口。"

# 主窗口
MAIN_TITLE = "宝可梦睡眠 · 技能触发记录"
BTN_ADD_RECORD = "添加触发记录"
BTN_VIEW_RECORDS = "查看触发记录"
BTN_CANCEL_RECORD = "取消记录"
BTN_CONFIRM_TEAM = "就是它们！"
BTN_CREATE_POKEMON = "添加宝可梦"

MSG_TEAM_LIMIT_TITLE = "队伍上限"
MSG_TEAM_LIMIT = "一支队伍最多只能有 5 只宝可梦。"
MSG_TEAM_LIMIT_OK = "我知道了"

MSG_NO_SELECTION_TITLE = "未选择"
MSG_NO_SELECTION = "请至少选择一只触发次数大于 0 的宝可梦。"
MSG_ERROR_TITLE = "错误"

# 创建宝可梦
CREATE_TITLE = "添加宝可梦"
LABEL_SPECIES = "种族"
LABEL_NICKNAME = "昵称"
LABEL_SKILL_TYPE = "技能型宝可梦"
LABEL_DAILY_TRIGGERS = "预期每日触发次数"
PLACEHOLDER_SPECIES = "宝可梦种族"
PLACEHOLDER_NICKNAME = "宝可梦昵称"
HINT_DAILY_TRIGGERS = "请从 Pokémon Sleep Assistant 获取该信息！"
BTN_SAVE = "保存"
BTN_CANCEL = "取消"
MSG_VALIDATION_TITLE = "校验失败"

# 详情
DETAIL_TITLE = "宝可梦 — {nickname}"
LABEL_SKILL_TYPE_SHORT = "技能型"
BTN_SAVE_CHANGES = "保存修改"
BTN_DELETE_POKEMON = "删除宝可梦"
DETAIL_RECORDS_TITLE = "该宝可梦的触发记录"
DETAIL_NO_RECORDS = "暂无触发记录。"
DETAIL_RECORD_LINE = "{time} — 触发次数：{count}"
MSG_SAVED_TITLE = "已保存"
MSG_SAVED = "宝可梦信息已更新。"
MSG_DELETE_POKEMON_TITLE = "确认删除"
MSG_DELETE_POKEMON = "确定删除宝可梦「{nickname}」吗？此操作无法撤销。"

# 触发时间
TRIGGER_TIME_TITLE = "触发时间"
BTN_USE_NOW = "填入当前时间"
BTN_CONFIRM = "确认"
BTN_OK = "确定"

# 首次提示
TIP_TITLE = "提示"
TIP_FIRST_RECORD = (
    "之后可在主界面「查看触发记录」页面中，"
    "在记录按钮旁修改已添加的记录。"
)
TIP_DONT_SHOW = "不再显示"

# 查看记录
VIEW_RECORDS_TITLE = "查看触发记录"
TAB_HISTORY = "添加历史"
TAB_STATISTICS = "触发统计"
TAB_DISTRIBUTION = "触发时间分布"
COL_ADDED_TIME = "添加时间"
COL_TRIGGERS = "宝可梦触发"
COL_ACTIONS = "操作"
COL_NICKNAME = "昵称"
COL_SPECIES = "种族"
COL_SKILL = "技能型"
COL_TOTAL = "总触发次数"
COL_AVG_DAILY = "平均每日触发次数"
POKEMON_PICKER_LABEL = "{nickname} ({species})"
LABEL_CHART_POKEMON = "宝可梦："
LABEL_TIME_SPAN = "时间范围："
DAY_1 = "1 天"
DAY_N = "{n} 天"
TIP_EDIT_TIME = "修改触发时间"
TIP_EDIT_TEAM = "修改宝可梦队伍"
TIP_DELETE_RECORD = "删除记录"
MSG_DELETE_RECORD_TITLE = "确认删除"
MSG_DELETE_RECORD = "确定删除这条触发记录吗？"
CHART_NO_DATA = "暂无数据"
CHART_Y_LABEL = "触发次数"
CHART_Y_TRIGGERED = "是否发动"
CHART_Y_CUMULATIVE = "累计发动次数"
CHART_MODE_TRIGGERED = "是否发动"
CHART_MODE_CUMULATIVE = "累计发动"
LABEL_CHART_MODE = "曲线类型："
PERIOD_MORNING = "早晨"
PERIOD_AFTERNOON = "下午"
PERIOD_NIGHT = "夜晚"

# 校验（services）
ERR_EMPTY = "不能为空。"
ERR_WIDTH = "超过最大显示宽度（相当于 6 个汉字）。"
ERR_SPECIES = "物种：{msg}"
ERR_NICKNAME = "昵称：{msg}"
ERR_NO_TRIGGERS = "请至少选择一只触发次数大于 0 的宝可梦。"

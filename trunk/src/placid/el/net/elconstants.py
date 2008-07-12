# Copyright 2008 Alex Collins
#
# This file is part of Pyela.
# 
# Pyela is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Pyela is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Pyela.  If not, see <http://www.gnu.org/licenses/>.
import logging as log

class ReflectiveConstants(object):
	"""Denotes that this class has functionality to reflect upon its properties"""
	def to_identifier(instance, val):
		"""Iterates through instance attributes and returns the identifier for val"""
		for att in dir(instance):
			if not att.startswith("__") and getattr(instance, att) == int(val):
				return att

class ELConstants(ReflectiveConstants):
# Actor types
	HUMAN_FEMALE = 0
	HUMAN_MALE = 1
	ELF_FEMALE = 2
	ELF_MALE = 3
	DWARF_FEMALE = 4
	DWARF_MALE = 5
	WRAITH = 6
	CYCLOPS = 7
	BEAVER = 8
	RAT = 9
	GOBLIN_MALE_2 = 10
	GOBLIN_FEMALE_1 = 11
	TOWN_FOLK4 = 12
	TOWN_FOLK5 = 13
	SHOP_GIRL3 = 14
	DEER = 15
	BEAR = 16
	WOLF = 17
	WHITE_RABBIT = 18
	BROWN_RABBIT = 19
	BOAR = 20
	BEAR2 = 21
	SNAKE1 = 22
	SNAKE2 = 23
	SNAKE3 = 24
	FOX = 25
	PUMA = 26
	OGRE_MALE_1 = 27
	GOBLIN_MALE_1 = 28
	ORC_MALE_1 = 29
	ORC_FEMALE_1 = 30
	SKELETON = 31
	GARGOYLE1 = 32
	GARGOYLE2 = 33
	GARGOYLE3 = 34
	TROLL = 35
	CHIMERAN_WOLF_MOUNTAIN = 36
	GNOME_FEMALE = 37
	GNOME_MALE = 38
	ORCHAN_FEMALE = 39
	ORCHAN_MALE = 40
	DRAEGONI_FEMALE = 41
	DRAEGONI_MALE = 42
	SKUNK_1 = 43
	RACOON_1 = 44
	UNICORN_1 = 45
	CHIMERAN_WOLF_DESERT = 46
	CHIMERAN_WOLF_FOREST = 47
	BEAR_3 = 48
	BEAR_4 = 49
	PANTHER = 50
	FERAN = 51
	LEOPARD_1 = 52
	LEOPARD_2 = 53
	CHIMERAN_WOLF_ARCTIC = 54
	TIGER_1 = 55
	TIGER_2 = 56
	ARMED_FEMALE_ORC = 57
	ARMED_MALE_ORC = 58
	ARMED_SKELETON = 59
	PHANTOM_WARRIOR = 60
	IMP = 61
	BROWNIE = 62
	LEPRECHAUN = 63
	SPIDER_S_1 = 64
	SPIDER_S_2 = 65
	SPIDER_S_3 = 66
	SPIDER_L_1 = 67
	SPIDER_L_2 = 68
	SPIDER_L_3 = 69
	WOOD_SPRITE = 70
	SPIDER_L_4 = 71
	SPIDER_S_4 = 72
	GIANT_1 = 73
	HOBGOBLIN = 74
	YETI = 75
	SNAKE4 = 76
	FEROS = 77
	DRAGON1 = 78
# Skin colors
	SKIN_BROWN = 0
	SKIN_NORMAL = 1
	SKIN_PALE = 2
	SKIN_TAN = 3
	SKIN_DARK_BLUE = 4
	SKIN_WHITE = 5
# Shirt colors
	SHIRT_BLACK = 0
	SHIRT_BLUE = 1
	SHIRT_BROWN = 2
	SHIRT_GREY = 3
	SHIRT_GREEN = 4
	SHIRT_LIGHTBROWN = 5
	SHIRT_ORANGE = 6
	SHIRT_PINK = 7
	SHIRT_PURPLE = 8
	SHIRT_RED = 9
	SHIRT_WHITE = 10
	SHIRT_YELLOW = 11
	SHIRT_LEATHER_ARMOR = 12
	SHIRT_CHAIN_ARMOR = 13
	SHIRT_STEEL_CHAIN_ARMOR = 14
	SHIRT_TITANIUM_CHAIN_ARMOR = 15
	SHIRT_IRON_PLATE_ARMOR = 16
	SHIRT_AUGMENTED_LEATHER_ARMOR = 17
	SHIRT_FUR = 18
	SHIRT_STEEL_PLATE_ARMOR = 19
	SHIRT_TITANIUM_PLATE_ARMOR = 20
	SHIRT_BRONZE_PLATE_ARMOR = 21
# No armor flags
	NO_BODY_ARMOR = 0
	NO_PANTS_ARMOR = 0
	NO_BOOTS_ARMOR = 0
# Hair colors
	HAIR_BLACK = 0
	HAIR_BLOND = 1
	HAIR_BROWN = 2
	HAIR_GRAY = 3
	HAIR_RED = 4
	HAIR_WHITE = 5
	HAIR_BLUE = 6
	HAIR_GREEN = 7
	HAIR_PURPLE = 8
	HAIR_DARK_BROWN = 9
	HAIR_STRAWBERRY = 10
	HAIR_LIGHT_BLOND = 11
	HAIR_DIRTY_BLOND = 12
	HAIR_BROWN_GRAY = 13
	HAIR_DARK_GRAY = 14
	HAIR_DARK_RED = 15
# Boots colors
	BOOTS_BLACK = 0
	BOOTS_BROWN = 1
	BOOTS_DARKBROWN = 2
	BOOTS_DULLBROWN = 3
	BOOTS_LIGHTBROWN = 4
	BOOTS_ORANGE = 5
	BOOTS_LEATHER = 6
	BOOTS_FUR = 7
	BOOTS_IRON_GREAVE = 8
	BOOTS_STEEL_GREAVE = 9
	BOOTS_TITANIUM_GREAVE = 10
	BOOTS_BRONZE_GREAVE = 11
	BOOTS_AUGMENTED_LEATHER_GREAVE = 12
# Pants colors
	PANTS_BLACK = 0
	PANTS_BLUE = 1
	PANTS_BROWN = 2
	PANTS_DARKBROWN = 3
	PANTS_GREY = 4
	PANTS_GREEN = 5
	PANTS_LIGHTBROWN = 6
	PANTS_RED = 7
	PANTS_WHITE = 8
	PANTS_LEATHER = 9
	PANTS_IRON_CUISSES = 10
	PANTS_FUR = 11
	PANTS_STEEL_CUISSES = 12
	PANTS_TITANIUM_CUISSES = 13
	PANTS_BRONZE_CUISSES = 14
	PANTS_AUGMENTED_LEATHER_CUISSES = 15
# Capes
	CAPE_BLACK = 0
	CAPE_BLUE = 1
	CAPE_BLUEGRAY = 2
	CAPE_BROWN = 3
	CAPE_BROWNGRAY = 4
	CAPE_GRAY = 5
	CAPE_GREEN = 6
	CAPE_GREENGRAY = 7
	CAPE_PURPLE = 8
	CAPE_WHITE = 9
	CAPE_FUR = 10
	CAPE_GOLD = 11
	CAPE_RED = 12
	CAPE_ORANGE = 13
	CAPE_MOD = 14
	CAPE_DERIN = 15
	CAPE_RAVENOD = 16
	CAPE_PLACID = 17
	CAPE_LORD_VERMOR = 18
	CAPE_AISLINN = 19
	CAPE_SOLDUS = 20
	CAPE_LOTHARION = 21
	CAPE_LEARNER = 22
	CAPE_NONE = 30
# Heads
	HEAD_1 = 0
	HEAD_2 = 1
	HEAD_3 = 2
	HEAD_4 = 3
	HEAD_5 = 4
# Types of wearable items
	KIND_OF_WEAPON = 0
	KIND_OF_SHIELD = 1
	KIND_OF_CAPE = 2
	KIND_OF_HELMET = 3
	KIND_OF_LEG_ARMOR = 4
	KIND_OF_BODY_ARMOR = 5
	KIND_OF_BOOT_ARMOR = 6
# Helmets
	HELMET_IRON = 0
	HELMET_FUR = 1
	HELMET_LEATHER = 2
	HELMET_RACOON = 3
	HELMET_SKUNK = 4
	HELMET_CROWN_OF_MANA = 5
	HELMET_CROWN_OF_LIFE = 6
	HELMET_STEEL = 7
	HELMET_TITANIUM = 8
	HELMET_BRONZE = 9
	HELMET_NONE = 100
# Shields
	SHIELD_WOOD = 0
	SHIELD_WOOD_ENHANCED = 1
	SHIELD_IRON = 2
	SHIELD_STEEL = 3
	SHIELD_TITANIUM = 4
	SHIELD_BRONZE = 5
	SHIELD_NONE = 11
# Weapons
	WEAPON_NONE = 0
	SWORD_1 = 1
	SWORD_2 = 2
	SWORD_3 = 3
	SWORD_4 = 4
	SWORD_5 = 5
	SWORD_6 = 6
	SWORD_7 = 7
	STAFF_1 = 8
	STAFF_2 = 9
	STAFF_3 = 10
	STAFF_4 = 11
	HAMMER_1 = 12
	HAMMER_2 = 13
	PICKAX = 14
	SWORD_1_FIRE = 15
	SWORD_2_FIRE = 16
	SWORD_2_COLD = 17
	SWORD_3_FIRE = 18
	SWORD_3_COLD = 19
	SWORD_3_MAGIC = 20
	SWORD_4_FIRE = 21
	SWORD_4_COLD = 22
	SWORD_4_MAGIC = 23
	SWORD_4_THERMAL = 24
	SWORD_5_FIRE = 25
	SWORD_5_COLD = 26
	SWORD_5_MAGIC = 27
	SWORD_5_THERMAL = 28
	SWORD_6_FIRE = 29
	SWORD_6_COLD = 30
	SWORD_6_MAGIC = 31
	SWORD_6_THERMAL = 32
	SWORD_7_FIRE = 33
	SWORD_7_COLD = 34
	SWORD_7_MAGIC = 35
	SWORD_7_THERMAL = 36
	PICKAX_MAGIC = 37
	BATTLEAXE_IRON = 38
	BATTLEAXE_STEEL = 39
	BATTLEAXE_TITANIUM = 40
	BATTLEAXE_IRON_FIRE = 41
	BATTLEAXE_STEEL_COLD = 42
	BATTLEAXE_STEEL_FIRE = 43
	BATTLEAXE_TITANIUM_COLD = 44
	BATTLEAXE_TITANIUM_FIRE = 45
	BATTLEAXE_TITANIUM_MAGIC = 46
	GLOVE_FUR = 47
	GLOVE_LEATHER = 48
	BONE_1 = 49
	STICK_1 = 50
	SWORD_EMERALD_CLAYMORE = 51
	SWORD_CUTLASS = 52
	SWORD_SUNBREAKER = 53
	SWORD_ORC_SLAYER = 54
	SWORD_EAGLE_WING = 55
	SWORD_RAPIER = 56
	SWORD_JAGGED_SABER = 57
	SWORD_BRONZE = 58
# Frames
	FRAME_WALK = 0
	FRAME_RUN = 1
	FRAME_DIE1 = 2
	FRAME_DIE2 = 3
	FRAME_PAIN1 = 4
	FRAME_PAIN2 = 11
	FRAME_PICK = 5
	FRAME_DROP = 6
	FRAME_IDLE = 7
	FRAME_HARVEST = 8
	FRAME_CAST = 9
	FRAME_RANGED = 10
	FRAME_SIT = 12
	FRAME_STAND = 13
	FRAME_SIT_IDLE = 14
	FRAME_COMBAT_IDLE = 15
	FRAME_IN_COMBAT = 16
	FRAME_OUT_COMBAT = 17
	FRAME_ATTACK_UP_1 = 18
	FRAME_ATTACK_UP_2 = 19
	FRAME_ATTACK_UP_3 = 20
	FRAME_ATTACK_UP_4 = 21
	FRAME_ATTACK_DOWN_1 = 22
	FRAME_ATTACK_DOWN_2 = 23
	FRAME_ATTACK_DOWN_3 = 24
	FRAME_ATTACK_DOWN_4 = 25
	FRAME_ATTACK_DOWN_5 = 26
	FRAME_ATTACK_DOWN_6 = 27
	FRAME_ATTACK_DOWN_7 = 28
	FRAME_ATTACK_DOWN_8 = 29
	FRAME_ATTACK_DOWN_9 = 30
	FRAME_ATTACK_DOWN_10 = 31
	FRAME_ATTACK_UP_5 = 32
	FRAME_ATTACK_UP_6 = 33
	FRAME_ATTACK_UP_7 = 34
	FRAME_ATTACK_UP_8 = 35
	FRAME_ATTACK_UP_9 = 36
	FRAME_ATTACK_UP_10 = 37
# Colors
	C_LBOUND = 0
	C_RED1 = 0
	C_RED2 = 7
	C_RED3 = 14
	C_RED4 = 21
	C_ORANGE1 = 1
	C_ORANGE2 = 8
	C_ORANGE3 = 15
	C_ORANGE4 = 22
	C_YELLOW1 = 2
	C_YELLOW2 = 9
	C_YELLOW3 = 16
	C_YELLOW4 = 23
	C_GREEN1 = 3
	C_GREEN2 = 10
	C_GREEN3 = 17
	C_GREEN4 = 24
	C_BLUE1 = 4
	C_BLUE2 = 11
	C_BLUE3 = 18
	C_BLUE4 = 25
	C_PURPLE1 = 5
	C_PURPLE2 = 12
	C_PURPLE3 = 19
	C_PURPLE4 = 26
	C_GREY1 = 6
	C_GREY2 = 13
	C_GREY3 = 20
	C_GREY4 = 27
	C_UBOUND = 27
# Foreign chars
	SPECIALCHAR_LBOUND = 180
	EACUTE = 181
	ACIRC = 182
	AGRAVE = 183
	CCEDIL = 184
	ECIRC = 185
	EUML = 186
	EGRAVE = 187
	IUML = 188
	OCIRC = 189
	UGRAVE = 190
	AUMLAUT = 191
	OUMLAUT = 192
	UUMLAUT = 193
	AUMLAUT = 194
	OUMLAUT = 195
	UUMLAUT = 196
	DOUBLES = 197
	AELIG = 198
	OSLASH = 199
	ARING = 200
	AELIG = 201
	OSLASH = 202
	ARING = 203
	ENYE = 204
	ENYE = 205
	AACCENT = 206
	AACCENT = 207
	EACCENT = 208
	IACCENT = 209
	IACCENT = 210
	OACCENT = 211
	OACCENT = 212
	UACCENT = 213
	UACCENT = 214
	SPECIALCHAR_UBOUND = 214
# Windows
	RULE_WIN = 1
	RULE_INTERFACE = 2
	NEW_CHAR_INTERFACE = 3
# Actor commands
	NOTHING = 0
	KILL_ME = 1
	DIE1 = 3
	DIE2 = 4
	PAIN1 = 5
	PAIN2 = 17
	PICK = 6
	DROP = 7
	IDLE = 8
	HARVEST = 9
	CAST = 10
	RANGED = 11
	MEELE = 12
	SIT_DOWN = 13
	STAND_UP = 14
	TURN_LEFT = 15
	TURN_RIGHT = 16
	ENTER_COMBAT = 18
	LEAVE_COMBAT = 19
	MOVE_N = 20
	MOVE_NE = 21
	MOVE_E = 22
	MOVE_SE = 23
	MOVE_S = 24
	MOVE_SW = 25
	MOVE_W = 26
	MOVE_NW = 27
	RUN_N = 30
	RUN_NE = 31
	RUN_E = 32
	RUN_SE = 33
	RUN_S = 34
	RUN_SW = 35
	RUN_W = 36
	RUN_NW = 37
	TURN_N = 38
	TURN_NE = 39
	TURN_E = 40
	TURN_SE = 41
	TURN_S = 42
	TURN_SW = 43
	TURN_W = 44
	TURN_NW = 45
	ATTACK_UP_1 = 46
	ATTACK_UP_2 = 47
	ATTACK_UP_3 = 48
	ATTACK_UP_4 = 49
	ATTACK_DOWN_1 = 50
	ATTACK_DOWN_2 = 51
# Weather types
	WEATHER_EFFECT_RAIN = 1
	WEATHER_EFFECT_SNOW = 2
	WEATHER_EFFECT_HAIL = 3
	WEATHER_EFFECT_SAND = 4
	WEATHER_EFFECT_DUST = 5
	WEATHER_EFFECT_LAVA = 6
	WEATHER_EFFECT_WIND = 20
	WEATHER_EFFECT_LEAVES = 21
# Stats
	PHY_CUR = 0
	PHY_BASE = 1
	COO_CUR = 2
	COO_BASE = 3
	REAS_CUR = 4
	REAS_BASE = 5
	WILL_CUR = 6
	WILL_BASE = 7
	INST_CUR = 8
	INST_BASE = 9
	VIT_CUR = 10
	VIT_BASE = 11
	HUMAN_CUR = 12
	HUMAN_BASE = 13
	ANIMAL_CUR = 14
	ANIMAL_BASE = 15
	VEGETAL_CUR = 16
	VEGETAL_BASE = 17
	INORG_CUR = 18
	INORG_BASE = 19
	ARTIF_CUR = 20
	ARTIF_BASE = 21
	MAGIC_CUR = 22
	MAGIC_BASE = 23
	MAN_S_CUR = 24
	MAN_S_BASE = 25
	HARV_S_CUR = 26
	HARV_S_BASE = 27
	ALCH_S_CUR = 28
	ALCH_S_BASE = 29
	OVRL_S_CUR = 30
	OVRL_S_BASE = 31
	DEF_S_CUR = 32
	DEF_S_BASE = 33
	ATT_S_CUR = 34
	ATT_S_BASE = 35
	MAG_S_CUR = 36
	MAG_S_BASE = 37
	POT_S_CUR = 38
	POT_S_BASE = 39
	CARRY_WGHT_CUR = 40
	CARRY_WGHT_BASE = 41
	MAT_POINT_CUR = 42
	MAT_POINT_BASE = 43
	ETH_POINT_CUR = 44
	ETH_POINT_BASE = 45
	FOOD_LEV = 46
	RESEARCHING = 47
	MAG_RES = 48
	MAN_EXP = 49
	MAN_EXP_NEXT = 50
	HARV_EXP = 51
	HARV_EXP_NEXT = 52
	ALCH_EXP = 53
	ALCH_EXP_NEXT = 54
	OVRL_EXP = 55
	OVRL_EXP_NEXT = 56
	DEF_EXP = 57
	DEF_EXP_NEXT = 58
	ATT_EXP = 59
	ATT_EXP_NEXT = 60
	MAG_EXP = 61
	MAG_EXP_NEXT = 62
	POT_EXP = 63
	POT_EXP_NEXT = 64
	RESEARCH_COMPLETED = 65
	RESEARCH_TOTAL = 66
	SUM_EXP = 67
	SUM_EXP_NEXT = 68
	SUM_S_CUR = 69
	SUM_S_BASE = 70
	CRA_EXP = 71
	CRA_EXP_NEXT = 72
	CRA_S_CUR = 73
	CRA_S_BASE = 74
	ENG_EXP = 75
	ENG_EXP_NEXT = 76
	ENG_S_CUR = 77
	ENG_S_BASE = 78
# Sound
	SND_RAIN = 0
	SND_TELE_IN = 1
	SND_TELE_OUT = 2
	SND_TELEPRTR = 3
	SND_THNDR_1 = 4
	SND_THNDR_2 = 5
	SND_THNDR_3 = 6
	SND_THNDR_4 = 7
	SND_THNDR_5 = 8
	SND_FIRE = 9
# Text channels
	CHAT_LOCAL = 0
	CHAT_PERSONAL = 1
	CHAT_GM = 2
	CHAT_SERVER = 3
	CHAT_MOD = 4
	CHAT_CHANNEL1 = 5
	CHAT_CHANNEL2 = 6
	CHAT_CHANNEL3 = 7
	CHAT_MODPM = 8
	CHAT_POPUP = 0xFF
# Actor scaling constants
	ACTOR_SCALE_BASE = 0x4000
	ACTOR_SCALE_MAX = 0x7FFF
# Actor buffs constants
	BUFF_INVISIBILITY = 1
# Special spell effects
	SPECIAL_EFFECT_POISON = 0
	SPECIAL_EFFECT_REMOTE_HEAL = 1
	SPECIAL_EFFECT_HARM = 2
	SPECIAL_EFFECT_SHIELD = 3
	SPECIAL_EFFECT_RESTORATION = 4
	SPECIAL_EFFECT_SMITE_SUMMONINGS = 5
	SPECIAL_EFFECT_CLOAK = 6
	SPECIAL_EFFECT_DECLOAK = 7
	SPECIAL_EFFECT_INVASION_BEAMING = 8
	SPECIAL_EFFECT_HEAL_SUMMONED = 9
	SPECIAL_EFFECT_MANA_DRAIN = 10
	SPECIAL_EFFECT_TELEPORT_TO_RANGE = 11
	SPECIAL_EFFECT_HEAL = 12
	SPECIAL_EFFECT_HARVEST_RARE_STONE = 13
	SPECIAL_EFFECT_HARVEST_MN_EXP_BLESSING = 14
	SPECIAL_EFFECT_HARVEST_MN_MONEY_BLESSING = 15
	SPECIAL_EFFECT_HARVEST_WALL_COLLAPSE = 16
	SPECIAL_EFFECT_HARVEST_BEES = 17
	SPECIAL_EFFECT_HARVEST_RADON = 18
	SPECIAL_EFFECT_HARVEST_TOOL_BREAKS = 19
	SPECIAL_EFFECT_HARVEST_TELEPORT_NEXUS = 20
	SPECIAL_EFFECT_HARVEST_MOTHER_NATURE_PISSED = 21
	SPECIAL_EFFECT_MANUFACTURE_TOOL_BREAKS = 22
	SPECIAL_EFFECT_MANUFACTURE_RARE_ITEM = 23
	SPECIAL_EFFECT_MAKE_PLAYER_GLOW = 24
	SPECIAL_EFFECT_SUMMON_RABBIT = 25
	SPECIAL_EFFECT_SUMMON_RAT = 26
	SPECIAL_EFFECT_SUMMON_BEAVER = 27
	SPECIAL_EFFECT_SUMMON_SKUNK = 28
	SPECIAL_EFFECT_SUMMON_RACOON = 29
	SPECIAL_EFFECT_SUMMON_DEER = 30
	SPECIAL_EFFECT_SUMMON_GREEN_SNAKE = 31
	SPECIAL_EFFECT_SUMMON_RED_SNAKE = 32
	SPECIAL_EFFECT_SUMMON_BROWN_SNAKE = 33
	SPECIAL_EFFECT_SUMMON_FOX = 34
	SPECIAL_EFFECT_SUMMON_BOAR = 35
	SPECIAL_EFFECT_SUMMON_WOLF = 36
	SPECIAL_EFFECT_SUMMON_SKELETON = 37
	SPECIAL_EFFECT_SUMMON_SMAL_GARG = 38
	SPECIAL_EFFECT_SUMMON_MEDIUM_GARG = 39
	SPECIAL_EFFECT_SUMMON_BIG_GARG = 40
	SPECIAL_EFFECT_SUMMON_PUMA = 41
	SPECIAL_EFFECT_SUMMON_FEM_GOBLIN = 42
	SPECIAL_EFFECT_SUMMON_POLAR_BEAR = 43
	SPECIAL_EFFECT_SUMMON_BEAR = 44
	SPECIAL_EFFECT_SUMMON_ARMED_MALE_GOB = 45
	SPECIAL_EFFECT_SUMMON_ARMED_SKELETON = 46
	SPECIAL_EFFECT_SUMMON_FEMALE_ORC = 47
	SPECIAL_EFFECT_SUMMON_MALE_ORC = 48
	SPECIAL_EFFECT_SUMMON_ARMED_FEM_ORC = 49
	SPECIAL_EFFECT_SUMMON_ARMED_MALE_ORC = 50
	SPECIAL_EFFECT_SUMMON_CYCLOP = 51
	SPECIAL_EFFECT_SUMMON_FLUFFY_RABBIT = 52
	SPECIAL_EFFECT_SUMMON_PHANTOM_WARRIOR = 53
	SPECIAL_EFFECT_SUMMON_MOUNTAIN_CHIM = 54
	SPECIAL_EFFECT_SUMMON_YETI = 55
	SPECIAL_EFFECT_SUMMON_ARCTIC_CHIM = 56
	SPECIAL_EFFECT_SUMMON_GIANT = 57
	SPECIAL_EFFECT_SUMMON_GIANT_SNAKE = 58
	SPECIAL_EFFECT_SUMMON_SPIDER = 59
	SPECIAL_EFFECT_SUMMON_TIGER = 60
# Mine types
	MINE_TYPE_SMALL_MINE = 0
	MINE_TYPE_MEDIUM_MINE = 1
	MINE_TYPE_HIGH_EXPLOSIVE_MINE = 2
	MINE_TYPE_TRAP = 3
	MINE_TYPE_CALTROP = 4
	MINE_TYPE_POISONED_CALTROP = 5
	MINE_TYPE_BARRICADE = 6
	MINE_TYPE_MANA_DRAINER = 7
	MINE_TYPE_MANA_BURNER = 8
	MINE_TYPE_UNINVIZIBILIZER = 9
	MINE_TYPE_MAGIC_IMMUNITY_REMOVAL = 10
#Item flags
	ITEM_RESOURCE = 2
	ITEM_REAGENT = 1
	ITEM_INVENTORY_USABLE = 8
	ITEM_STACKABLE = 4
	SIGILS = ('Change', 'Restore', 'Space', 'Increase', 'Decrease', 'Temporary', 'Permanent', 'Move', 'Local', 'Global', 'Fire', 'Water', 'Air', 'Earth', 'Spirit', 'Matter', 'Energy', 'Magic', 'Destroy', 'Create', 'Knowledge', 'Protection', 'Remove', 'Health', 'Life', 'Death')

class ELNetFromServer(ReflectiveConstants):
	"""Holds message types that are sent TO the client, from the server"""
# To client commands
	RAW_TEXT = 0
	ADD_NEW_ACTOR = 1
	ADD_ACTOR_COMMAND = 2
	YOU_ARE = 3
	SYNC_CLOCK = 4
	NEW_MINUTE = 5
	REMOVE_ACTOR = 6
	CHANGE_MAP = 7
	COMBAT_MODE = 8
	KILL_ALL_ACTORS = 9
	GET_TELEPORTERS_LIST = 10
	PONG = 11
	TELEPORT_IN = 12
	TELEPORT_OUT = 13
	PLAY_SOUND = 14
	START_RAIN = 15
	STOP_RAIN = 16
	THUNDER = 17
	HERE_YOUR_STATS = 18
	HERE_YOUR_INVENTORY = 19
	INVENTORY_ITEM_TEXT = 20
	GET_NEW_INVENTORY_ITEM = 21
	REMOVE_ITEM_FROM_INVENTORY = 22
	HERE_YOUR_GROUND_ITEMS = 23
	GET_NEW_GROUND_ITEM = 24
	REMOVE_ITEM_FROM_GROUND = 25
	CLOSE_BAG = 26
	GET_NEW_BAG = 27
	GET_BAGS_LIST = 28
	DESTROY_BAG = 29
	NPC_TEXT = 30
	NPC_OPTIONS_LIST = 31
	CLOSE_NPC_MENU = 32
	SEND_NPC_INFO = 33
	GET_TRADE_INFO = 34
	GET_TRADE_OBJECT = 35
	GET_TRADE_ACCEPT = 36
	GET_TRADE_REJECT = 37
	GET_TRADE_EXIT = 38
	REMOVE_TRADE_OBJECT = 39
	GET_YOUR_TRADEOBJECTS = 40
	GET_TRADE_PARTNER_NAME = 41
	GET_YOUR_SIGILS = 42
	SPELL_ITEM_TEXT = 43
	GET_ACTIVE_SPELL = 44
	GET_ACTIVE_SPELL_LIST = 45
	REMOVE_ACTIVE_SPELL = 46
	GET_ACTOR_DAMAGE = 47
	GET_ACTOR_HEAL = 48
	SEND_PARTIAL_STAT = 49
	SPAWN_BAG_PARTICLES = 50
	ADD_NEW_ENHANCED_ACTOR = 51
	ACTOR_WEAR_ITEM = 52
	ACTOR_UNWEAR_ITEM = 53
	PLAY_MUSIC = 54
	GET_KNOWLEDGE_LIST = 55
	GET_NEW_KNOWLEDGE = 56
	GET_KNOWLEDGE_TEXT = 57
	BUDDY_EVENT = 59
	PING_REQUEST = 60
	FIRE_PARTICLES = 61
	REMOVE_FIRE_AT = 62
	DISPLAY_CLIENT_WINDOW = 63
	OPEN_BOOK = 64
	READ_BOOK = 65
	CLOSE_BOOK = 66
	STORAGE_LIST = 67
	STORAGE_ITEMS = 68
	STORAGE_TEXT = 69
	SPELL_CAST = 70
	GET_ACTIVE_CHANNELS = 71
	MAP_FLAGS = 72
	GET_ACTOR_HEALTH = 73
	GET_3D_OBJ_LIST = 74
	GET_3D_OBJ = 75
	REMOVE_3D_OBJ = 76
	GET_ITEMS_COOLDOWN = 77
	SEND_BUFFS = 78
	SEND_SPECIAL_EFFECT = 79
	REMOVE_MINE = 80
	GET_NEW_MINE = 81
	GET_MINES_LIST = 82
	SEND_WEATHER = 100
	MAP_SET_OBJECTS = 220
	MAP_STATE_OBJECTS = 221
	UPGRADE_NEW_VERSION = 240
	UPGRADE_TOO_OLD = 241
	REDEFINE_YOUR_COLORS = 248
	YOU_DONT_EXIST = 249
	LOG_IN_OK = 250
	LOG_IN_NOT_OK = 251
	CREATE_CHAR_OK = 252
	CREATE_CHAR_NOT_OK = 253

class ELNetToServer(ReflectiveConstants):
	"""Holds message types that are sent from the client"""
# To server commands
	MOVE_TO = 1
	SEND_PM = 2
	GET_PLAYER_INFO = 5
	RUN_TO = 6
	SIT_DOWN = 7
	SEND_ME_MY_ACTORS = 8
	SEND_OPENING_SCREEN = 9
	SEND_VERSION = 10
	TURN_LEFT = 11
	TURN_RIGHT = 12
	PING = 13
	HEART_BEAT = 14
	LOCATE_ME = 15
	USE_MAP_OBJECT = 16
	SEND_MY_STATS = 17
	SEND_MY_INVENTORY = 18
	LOOK_AT_INVENTORY_ITEM = 19
	MOVE_INVENTORY_ITEM = 20
	HARVEST = 21
	DROP_ITEM = 22
	PICK_UP_ITEM = 23
	LOOK_AT_GROUND_ITEM = 24
	INSPECT_BAG = 25
	S_CLOSE_BAG = 26
	LOOK_AT_MAP_OBJECT = 27
	TOUCH_PLAYER = 28
	RESPOND_TO_NPC = 29
	MANUFACTURE_THIS = 30
	USE_INVENTORY_ITEM = 31
	TRADE_WITH = 32
	ACCEPT_TRADE = 33
	REJECT_TRADE = 34
	EXIT_TRADE = 35
	PUT_OBJECT_ON_TRADE = 36
	REMOVE_OBJECT_FROM_TRADE = 37
	LOOK_AT_TRADE_ITEM = 38
	CAST_SPELL = 39
	ATTACK_SOMEONE = 40
	GET_KNOWLEDGE_INFO = 41
	ITEM_ON_ITEM = 42
	SEND_BOOK = 43
	GET_STORAGE_CATEGORY = 44
	DEPOSITE_ITEM = 45
	WITHDRAW_ITEM = 46
	LOOK_AT_STORAGE_ITEM = 47
	SPELL_NAME = 48
	SEND_VIDEO_INFO = 49
	PING_RESPONSE = 60
	SET_ACTIVE_CHANNEL = 61
	LOG_IN = 140
	CREATE_CHAR = 141
	GET_DATE = 230
	GET_TIME = 231
	SERVER_STATS = 232
	ORIGINAL_IP = 233

# Common (both to the server and client) commands
	RAW_TEXT = 0
	BYE = 255
# Protocol places
	PROTOCOL = 0



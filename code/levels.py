from utils import import_level

tile_size = 64
level_1 = import_level("../level_data/1")
level_2 = import_level("../level_data/2")
level_3 = import_level("../level_data/3")

levels = {
	1: {"level_data": level_1, "strokes": 2},
	2: {"level_data": level_2, "strokes": 3},
	3: {"level_data": level_3, "strokes": 6}
}

screen_height = len(levels[1]["level_data"]["background"]) * tile_size
screen_width = len(levels[1]["level_data"]["background"][0]) * tile_size
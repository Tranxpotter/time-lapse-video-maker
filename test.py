import math

zoom_ratio_per_level = 0.02
def calc_zoom_value(zoom:int, val:int|float):
    # zoom_ratio = 1 - (zoom-1) * self.zoom_ratio_per_level
    zoom_ratio = math.exp(-math.log(zoom_ratio_per_level) / 49) * math.exp(math.log(zoom_ratio_per_level) / 49 * zoom)
    return int(val * zoom_ratio)

last = 0
for i in range(1, 51):
    print(i, calc_zoom_value(i, 1000), end=" ")
    if last != 0:
        print("Ratio: ", last / calc_zoom_value(i, 1000))
    else:
        print()
    last = calc_zoom_value(i, 1000)
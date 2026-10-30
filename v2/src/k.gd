class_name K
## Константы мира «Без лица» 2.0 (вид сбоку).

const T := 16                 # тайл, пикселей
const FH := 5                 # высота этажа в тайлах (перекрытие + 4 ряда)
const SEC := 10               # этажей в секции мегакорпуса; этажи 0, 10, 20… — узлы (холл, экспресс)
const SHADE_F := 18           # ниже этого этажа солнца не бывает: тень соседних башен
const GY := 320               # ряд земли (верх тротуара = GY * T): над ним до 60 этажей
const ROWS := GY + 34
const M := 26.0               # пикселей в метре (для перевода чисел из 3D-версии)

const VIEW_W := 640           # низкое разрешение мира
const VIEW_H := 360
const SCALE := 3
const PX := 2                 # пикселей картинки на пиксель мира (графика в двойной плотности)
const TT := T * PX            # тайл в атласе

# слои столкновений
const L_COMMON := 1           # земля, крыши, площадки снаружи
const L_INTERIOR := 2         # стены и перекрытия внутри зданий
const L_GRATE := 4            # решётки и лазы: человек не проходит, дух проходит
const L_DOOR := 8             # закрытые двери
const L_PLATFORM := 16        # полупроходные площадки (балконы, пожарные лестницы)

# слои видимости (canvas cull mask)
const V_INNER := 1
const V_OUTER := 2
const V_LIN := 4
const V_LOUT := 8
const V_FAR := 16
const V_ALL := 0xFFFF

# z-порядок внутри слоёв
const Z_BACK := -20
const Z_FURN := -10
const Z_SOLID := 0
const Z_PEOPLE := 10
const Z_FACADE := 20
const Z_FACADE_PROPS := 25
const Z_OUT_PEOPLE := 30
const Z_FRONT := 40
const Z_FX := 50

const GOLD := Color(0.851, 0.714, 0.251)
const INK := Color(0.067, 0.071, 0.078)
const PAPER := Color(0.88, 0.85, 0.77)


static func floor_y(f: int) -> float:
	## Пиксель Y пола этажа f (0 — первый этаж, -1 — подвал).
	if f >= 0:
		return float((GY - FH * f) * T)
	return float((GY + 6) * T)


static func sec_of(f: int) -> int:
	return maxi(0, f) / SEC


static func cls_of_floor(f: int) -> int:
	## Классы по высоте: 0 — низ (рабочие, старики), 1 — середина (служащие), 2 — верх (начальство).
	if f >= 40:
		return 2
	if f >= 20:
		return 1
	return 0


static func fmt_time(h: float) -> String:
	var total := int(floor(h * 60.0 + 0.001))
	return "%d:%02d" % [(total / 60) % 24, total % 60]

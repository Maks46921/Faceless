# Каталог моделей «Без лица»

Блендер: `D:\Cosmoteer\blender.exe` (5.2.3 LTS), запуск `blender -b -P <скрипт>`. Скрипты в `models/src/`. Метры, в glTF Y вверх, перёд +Z, начало у пола по центру. Godot 4.3: все glb импортируются (проверено).

## Оригиналы (не менять)
| Файл | Треугольники | Габариты, м |
|---|---|---|
| human_noir.glb | 516 | 0,70×0,31×1,78 |
| chair_noir.glb | 108 | 0,46×0,46×1,00 |
| lamp_noir.glb | 100 | 0,40×0,42×1,72 |
| table_noir.glb | 84 | 1,30×0,75×0,76 |

## Новые версии
| Файл | Треугольники | Габариты, м | Материалы | Скрипт | Анимации |
|---|---|---|---|---|---|
| human_noir_v2.glb | 6524 | 0,78×0,35×1,73 | 7 | (разовый) | нет |
| human_noir_v3.glb | 13 676 | 0,82×0,45×1,78 | coat, coat_dark, gold_accent, hair, pants, shirt, shoes, skin | src/build_human_v3.py | нет |
| human_noir_v4.glb | 17 240 | 0,82×0,45×1,78 | те же + iris, lips | src/build_human_v4.py (+ _head, _rig) | 25, скелет 40 костей, 10 морф-целей |
| chair_noir_v2.glb | 1384 | 0,46×0,46×0,99 | wood, wood_dark | src/build_furniture_v2.py | нет |
| table_noir_v2.glb | 1280 | 1,30×0,75×0,76 | wood, wood_dark | src/build_furniture_v2.py | нет |
| lamp_noir_v2.glb | 1700 | 0,42×0,42×1,73 | metal, lamp_shade | src/build_furniture_v2.py | нет |

## human_noir_v4: скелет (40 костей)
root, pelvis, spine, spine2, neck, head, jaw, lids (пустая, веки через морф blink); на каждую сторону (.L = персонаж слева): shoulder, upper_arm, forearm, hand, index_1, index_2, fingers_1, fingers_2 (средний, безымянный, мизинец), thumb_1, thumb_2, prop (предмет), thigh, shin, foot, toe; phone и ember под prop.R.

### Соответствие скелету игры (BodyBuilder, 19 костей)
| Кость игры | Наша кость |
|---|---|
| root | root |
| pelvis | pelvis |
| spine | spine (верх: spine2) |
| hip_l / hip_r | thigh.L / thigh.R |
| knee_l / knee_r | shin.L / shin.R |
| head | head |
| jaw | jaw |
| lids | lids (+ морф blink) |
| sh_l / sh_r | upper_arm.L / upper_arm.R (плечо в игре = наша upper_arm; shoulder.L/R наш плечевой пояс) |
| el_l / el_r | forearm.L / forearm.R |
| hand_l / hand_r | hand.L / hand.R |
| item | prop.R |
| phone | phone |
| ember | ember |

Сторона: `.L` = левая рука персонажа (в Blender +X, в glTF −X, потому что перёд +Z).

## Морф-цели
blink, mouth_open, smile, frown, brow_up, brow_down, look_l, look_r, look_up, look_down (веса задаёт игра).

## Анимации человека v4 (24 fps)
В Godot суффикс `_loop` отрезается и включается зацикливание (проверено в 4.3: `walk_loop` → `walk`, loop=1).

| Имя в glb | Имя в Godot | Тип | Кадры | Заметки |
|---|---|---|---|---|
| idle_loop | idle | цикл | 96 | |
| idle_look_loop | idle_look | цикл | 120 | |
| idle_cold_loop | idle_cold | цикл | 48 | замёрз, руки обхватывают, дрожь |
| walk_loop | walk | цикл | 24 | на месте, ≈1,3 м/с |
| walk_old_loop | walk_old | цикл | 36 | шаркающая, сутулая |
| run_loop | run | цикл | 16 | на месте, ≈3,6 м/с |
| talk_loop | talk | цикл | 96 | |
| phone_loop | phone | цикл | 96 | |
| smoke_loop | smoke | цикл | 144 | |
| confused_loop | confused | цикл | 72 | |
| startled | startled | разовая | 36 | |
| shove | shove | разовая | 30 | |
| point | point | разовая | 36 | указательный вытянут |
| knock | knock | разовая | 48 | стучит правой рукой |
| pick_up | pick_up | разовая | 48 | поднимает с земли (ладонь в точке y=−0,32, z=0,12) |
| open_door | open_door | разовая | 48 | ручка двери (y=−0,42, z=1,0) |
| fall | fall | разовая | 48 | лицом вниз, остаётся лёжа |
| down_loop | down | цикл | 96 | лежит |
| carried_loop | carried | цикл | 60 | тело горизонтально, корень на высоте ≈1,1 м |
| climb_ladder_loop | climb_ladder | цикл | 32 | перекладины шаг 0,30 м, плоскость y=−0,30; корень поднимается на 0,6 м за цикл |
| jump | jump | разовая | 36 | |
| vault | vault | разовая | 48 | уступ верх z=1,2, край y=−0,30; кончается стоя на уступе (корень y=−0,6, z=1,2) |
| sit_down | sit_down | разовая | 36 | сиденье на высоте ≈0,46 м |
| sit_idle_loop | sit_idle | цикл | 96 | |
| stand_up | stand_up | разовая | 36 | |

Тест-геометрия для climb/vault собирается в `src/anim_scene.py`.

## Известные недостатки human_noir_v4
- 17 240 треугольников: лицо ≈3 тыс., остальное тело/одежда. Ниже 12 тыс. планируется в пресетах (скрытая геометрия убирается).
- Пальто, лацканы, воротник перекрываются с телом, а не сшиты общей сеткой. Подол пальто при беге местами задевает ноги.
- Лицо читается как лицо, но упрощённое (нос, губы, веки, радужка простые формы).
- UV-развёрток нет.

---
# Этап 7: модели для механик (игра грузит `res://models/<имя>.glb`)
Соглашения: метры, Y вверх (в glTF), перёд +Z, начало на полу по центру. Коллизия: узлы `*-col` и `*-convcol` (упрощённые, без материала, Godot превращает в коллайдеры). Пустышки верхнего уровня: `ip_use` (где стоять игроку), `ip_hit` (куда падает/бьёт), `ip_hand` (точка в руку), `ip_spark` (искры). Состояния: узлы верхнего уровня `state_ok`, `state_loose`, `state_broken` (игра переключает visible). Библиотека и скрипты: `src/lib_props.py`, `src/build_*.py`.

## P1
| Файл | Треугольники | Содержимое | Анимации |
|---|---|---|---|
| spirit_gold.glb | 4768 | skin: spirit_gold (gold_glow), spirit_double (gold_glow_pale, двойник), spirit_halo, thread_ribbon (UV вдоль длины); скелет 16 костей (root, body, chest, head, tail_1..6, arm_l1/2, arm_r1/2, wisp_l/r); ip_head, ip_enter | descend (145 кадров, 6 с, спираль 2,5 оборота с 24 м, замедление у земли), enter (37 кадра, 1,5 с: 1,2 м вперёд и вверх на 1,55 м, ужимается до 5%), idle (97 кадров, парение, цикл) |
| spirit_thread.glb | 864 | thread_short (1 м), thread_mid (3 м), thread_long (8 м), thread_curve, thread_curve_arc; материал thread_glow; UV u вдоль ленты 0..1, v поперёк | нет |
| mannequin_male.glb | 6776 | безликий серый манекен 1,80 м, материал mannequin_gray, скелет и 25 анимаций как у human_noir_v4 | да (все анимации человека) |
| mannequin_female.glb | 7064 | 1,68 м, у́же в плечах | да |
| mannequin_child.glb | 7064 | 1,22 м | да |
| item_knife_hand / _ground.glb | 244 / 256 | кухонный нож; ground: лежит на полу, `-convcol`, ip_hand у рукояти | нет |
| item_syringe_hand / _ground.glb | 336 / 348 | шприц | нет |
| item_crowbar_hand / _ground.glb | 1396 / 1408 | лом 0,63 м | нет |
| item_pistol_hand / _ground.glb | 884 / 896 | табельный пистолет типа ПМ | нет |
| item_holster.glb | 412 | кобура с рукоятью, ip_hand у рукояти | нет |
| rock_throw.glb / rock_throw_ground.glb | 80 / 92 | камень | нет |
| manhole.glb | 3124 | manhole_frame, shaft, street_patch, state_ok (cover_ok), state_loose (cover_off), cover_anim (отдельная крышка), manhole-col; ip_use, ip_hand, ip_hit | open, close (30 кадров) |
| canopy.glb | 2744 | wall_stub (+wall_stub-col), state_ok, state_loose (провис, трещины, оборвана тяга), state_broken (плита а висит под ≈35°, плита b лежит), debris (куски бетона и арматура), canopy_fall (подвижные плиты), canopy-convcol; ip_hit, ip_use | collapse (36 кадров: плита b падает, плита a провисает, обломки появляются масштабом) |
| panel_electric.glb | 4868 | wall_section, шкаф с 24 автоматами, state_ok (дверца закрыта), state_loose (дверца открыта, оборванные красный и чёрный провода, ip_spark, ip_spark_2, ip_spark_box), door_anim (отдельная дверца), panel-col, wall-col; ip_use, ip_hand | open, close (18 кадров) |
| decal_blood / decal_blood2 / decal_oil / decal_oil2 / decal_puddle / decal_puddle2.glb | 28–70 | плоские пятна на z=0,003, UV по габариту, материалы decal_blood, decal_oil, decal_puddle (игра ставит шейдер/прозрачность), ip_hit | нет |

Тест-сцена кастсцены духа: `src/cutscene_spirit.py` (только Blender, небо, облака, прохожий v4, 6 кадров).
Скелет манекена тот же, что у human_noir_v4 (40 костей, см. таблицу выше).

Примечания: анимированные узлы (debris, cover_anim, door_anim, canopy_fall) в покое стоят в конечном состоянии, играются через AnimationPlayer. Расхождение с ТЗ: размеры люка и щитка в треугольниках выше целевых 2 тыс. (люк 3124, щиток 4868), потому что включены дубликаты крышки и дверцы для анимации и 24 автомата.

## P2 / охрана / VFX (этап 7)
Все файлы импортируются в Godot 4.3 (проверка в копии `C:\tmp_t\gdtest2`: узлы state_*, ip_*, *-col, анимации на месте).
| Файл | Треугольники | Содержимое / анимации |
|---|---|---|
| stepladder_open.glb | 1092 | стремянка раскрытая 1,55 м (state_ok), ip_use, ip_hand, -convcol |
| stepladder_folded.glb | 732 | сложенная, 1,65 м |
| turnstile.glb | 828 | трёхлучевой турникет; state_ok (зелёная лампа), state_loose (заклинил: красная лампа, погнутая лапа, жёлтая лента); арматура `arms` с анимациями pass (поворот 120°, 18 кадров) и idle_jam (дрожь) |
| cctv_wall.glb | 812 | настенная камера на кронштейне; state_ok (красный индикатор, анимация sweep_loop ±40°, 96 кадров) и state_broken (индикатор погас, голова свисает, трещина) |
| cctv_dome.glb | 536 | купольная камера; sweep_loop (внутренняя камера ±57°), state_ok / state_broken (индикатор) |
| desk_security.glb | 2696 | пульт охраны: стол, ящики, 4 монитора ЭЛТ (state_ok: экраны светятся, state_loose: выключены), видеомагнитофон, клавиатура, телефон, переговорное |
| barrel_stripe.glb | 788 | бак с жёлтой полосой 0,6×0,9 м |
| mop_wet_sign.glb | 708 | знак «скользко» + ведро + швабра (отдельные узлы sign, bucket, mop) |
| railing_stairs.glb / railing_balcony.glb | 1884 / 1884 | перила лестничного пролёта 2,0 м / балкона 1,5 м, state_ok и state_broken (оторванный поручень, выбитые и погнутые балясины) |
| parapet.glb | 948 | парапет крыши 3,0 м + плита крыши, state_ok / state_broken (выбит кусок, арматура, обломки), ip_use, ip_hit (внизу −3 м) |
| barrier_gate.glb | 872 | шлагбаум (стрела 4 м), анимации open, close (30 кадров), лампы state_ok/state_loose |
| door_lockable.glb | 1452 | дверь в раме: state_ok (закрыта), state_loose (открыта), state_broken (выбита/взломана), отдельная дверь `door_anim` с анимациями open, close, kick |
| item_*_hand / _ground | 80–560 | pass_card, id_booklet, folder_docs, keys_ring, notebook, radio, briefcase, videotape (по два варианта) |
| vfx_circle_0_5 / 1_0 / 2_0 / 4_0.glb | 288 | плоские кольца и диски (мягкая кромка, UV: u радиально 0..1, v по углу), материалы vfx_ring, vfx_disc |
| vfx_camera_cone.glb | 24 | конус луча, вершина в начале, вперёд +Z, 8 м, радиус 2,4 м, UV v вдоль луча |
| vfx_marker_sphere.glb | 288 | сфера-метка r=0,12 (vfx_marker) |
| vfx_shockwave.glb | 256 | кольцо ударной волны r=1 (масштабируется в игре) |
| vfx_smoke_plume_1/2/3.glb | 6 | перекрёстные карточки дыма 1,6 / 2,4 / 3,4 м (vfx_smoke) |
| vfx_smoke_puffs.glb | 720 | объёмные клубы дыма |
| vfx_spark_flash.glb | 20 | вспышка искр (vfx_spark эмиссия) |
| vfx_rain_plane.glb | 2 | плоскость дождя 6×6 м, UV 4×4 |

---
# Города: люди, транспорт, уличные объекты
Файлы в `models/city/people/`, `models/city/vehicles/`, `models/city/props/`. Скрипты: `src/build_human_preset.py` (+ `build_human_v4_rig.py`), `src/build_vehicles.py`, `src/build_props_a.py`, `src/build_props_b.py`. Импорт всех 93 glb проверен в Godot 4.3 (копия `C:\tmp_t\gdtest3`, ошибок нет).

## Люди-пресеты (общий скелет 40 костей и 25 анимаций как у human_noir_v4)
Каждый пресет в двух версиях: `<имя>.glb` (≈12–13 тыс. треугольников, лицо, 10 морф-целей, пальцы) и `<имя>_far.glb` (≈2,5–3 тыс., упрощённая голова, без морф-целей, с теми же костями и анимациями).
| Файл | Роль | Одежда / головной убор | Рост, м |
|---|---|---|---|
| militia_patrol | патрульный милиционер | форма, фуражка, погоны, портупея | 1,84 |
| militia_inspector | инспектор | пальто, кепка | 1,78 |
| guard_black | охранник | чёрная куртка, кепка, тёмные очки | 1,86 |
| electrician | электрик | спецовка, каска, пояс с инструментом | 1,76 |
| courier | курьер | худи, шапка, рюкзак | 1,74 |
| barista_f | бариста (ж) | свитер, фартук, пучок | 1,66 |
| medic_f / medic_m | медик | белый халат, берет (ж), стетоскоп, красный крест | 1,68 / 1,82 |
| resident_old_m | пожилой жилец | куртка, кепка, седой | 1,70 |
| resident_old_f | пожилая жилица | кардиган, платок | 1,58 |
| resident_young_f | молодая жилица | пуховик, берет, длинные волосы | 1,68 |
| resident_man | жилец | кожаная куртка | 1,79 |
| bodyguard | телохранитель | чёрный костюм, очки | 1,92 |
| janitor | дворник | пуховик, шапка | 1,72 |
| cleaner_f | уборщица (ж) | спецовка, платок, фартук | 1,62 |
| kiosk_seller_f | продавец ларька (ж) | пуховик, шапка | 1,64 |
| schoolchild | школьник | худи, рюкзак | 1,30 |
Главный герой в пальто и шляпе: `human_noir_v4.glb` (корневая папка models).

## Транспорт (перёд +Z, ось Y вверх, начало на земле по центру; колёса отдельными узлами wheel_fl/fr/rl/rr (+ _rl2/_rr2 у грузовых) с осью в ступице, анимация drive_loop; фары, поворотники и стоп-сигналы с эмиссией: lamp_head, lamp_amber, lamp_tail, lamp_white; мигалки lamp_beacon_blue/red с анимацией beacon_loop; ip_use у водительской двери (слева), ip_hit спереди, ip_hand у ручки; коллизия `<имя>-convcol`)
| Файл | Треугольники | Габариты, м |
|---|---|---|
| car_sedan, car_sedan_green | 4232 | 1,9×4,3×1,42 («Жигули»-подобный седан) |
| car_wagon | 4232 | 1,9×4,27×1,42 |
| car_moskvich | 4220 | 1,82×4,22×1,54 |
| car_sedan_roofrack | 4592 | с багажником на крыше |
| car_militia | 4484 | с полосами и мигалкой |
| van_gazelle | 2708 | 2,4×5,8×2,05 |
| ambulance | 2984 | скорая, красная полоса, крест, мигалки |
| truck_zil | 3508 | бортовой, 2,4×6,9×2,7 |
| bus_city | 4392 | 2,7×11,2×3,05, двери справа, 6 колёс |
| trolleybus | 4012 | штанги pole_a/pole_b (анимация pole_sway), табло маршрута |
| tow_truck | 2628 | эвакуатор со стрелой (boom_lift) и маячком |
Недостатки: кузова угловатые (в духе 90-х, без лепки), салон показан упрощённо, стёкла непрозрачные тёмные.

## Уличные объекты (props)
street_lamp (ok/broken), bench (ok/broken), urn_street, dumpster (анимации open/close крышки), bus_stop, billboard, ad_column, phone_booth, traffic_light_car, traffic_light_ped, power_pole, sign_stop, sign_yield, sign_noentry, sign_crossing, sign_speed, sign_street, tree_birch, tree_poplar, tree_maple, tree_bare, bush_a, bush_b, fence_mesh, fence_concrete, fence_picket, garage_gate, garage_row, transformer_booth (door_anim open/close, ip_spark), kiosk, sandbox, slide, swing (swing_loop), pullup_bar, carpet_beater, standpipe, tower_crane (slew_loop), antenna_tower, satellite_dish, vent_shaft, roof_hatch (open/close), fire_escape, downpipe, plank_bridge, crate_stack, laundry_line, shop_sign. 100–1700 треугольников каждый. Деревья из объёмных групп листвы (не шары-примитивы), 560–900 треугольников.

## Здания (models/city/buildings, скрипт src/build_buildings.py)
Высота этажа 2,8 м (офис 3,6, школа 3,8). Фасады с утопленными окнами (проём, откос, рама), окна отдельным материалом `building_window` (для ночного свечения), рамы `window_frame`. Перёд на +Z (в Blender −Y), начало у центра основания, коллизия `<имя>-col`, ip_use у главного входа.
| Файл | Треугольники | Габариты, м | Заметки |
|---|---|---|---|
| panel9_a | 6324 | 36×11,5×25 | 9 этажей, 3 подъезда с козырьками, технический этаж, антенны |
| panel9_b | 9204 | 36×11,5×25 | с остеклёнными лоджиями |
| panel5_khrushchev | 4132 | 30×10×14 | 5 этажей, открытые балконы, 3 подъезда |
| brick5 | 2532 | 24×11×14 | кирпичный |
| stalin_house | 8400 | 48×14×≈48 | колонны, ярусы башни, шпиль со звездой |
| office_glass | 10544 | 30×20×36 | остеклённая сетка, козырёк |
| residential_tower | 10484 | 18×18×56 | 20 этажей, лоджии |
| school | 3788 | 54×15×11 | 3 этажа, портик, вывеска |
| shop_pavilion, cafe_vstrecha, lobby_granit, metro_entrance | 212 / 234 / 400 / 302 | 12×8, 10×8, 14×9, 10×8 | павильоны; у метро буква «М» (эмиссия), козырёк |
| market | 4184 | 22×14 | 10 прилавков с навесами |
| factory | 896 | 36×20×9 + труба 38 м | пилообразная крыша |
| chp_plant | 1160 | 44×24×16 + труба 70 м | ТЭЦ |
| warehouse | 396 | 26×14×6,5 | склад |
| substation | 208 | 10×6×4,2 | подстанция, ip_spark |
| module_wall_row, module_entrance_bay, module_corner, module_roof_cap | — | модуль шириной 3,0 м, 3 этажа | из них собираются дома любой длины |
Недостатки: форма простая (коробки с рельефом окон и балконов), нет складок швов панелей и кондиционеров, торцы почти слепые, крыши плоские, текстур нет.

## Животные (models/city/animals, скрипт src/build_animals.py)
Скелет у собак и кошки 24 кости (root, pelvis, spine, chest, neck, head, jaw, tail_1..3, передние и задние ноги), у птиц 14 костей (root, body, neck, head, beak, tail, wing_a/b, leg, foot). Анимации (24 fps; `_loop` отрезается Godot и включает цикл).
| Файл | Треугольники | Анимации |
|---|---|---|
| dog_shepherd | 1584 | idle_loop, walk_loop, run_loop, sit, sit_idle_loop, bark |
| dog_mutt | 1644 | то же |
| dog_dachshund | 2024 | то же |
| cat | 2152 | idle_loop, walk_loop, run_loop, sit, sit_idle_loop, sleep_loop, lie_loop |
| pigeon, crow | 660 | idle_loop, peck, walk_loop, fly_loop, take_off, land |
Недостатки: упрощённая форма (трубчатое тело, ухо-коробка), птицы схематичные, походка собак без стоп, посадка собак приблизительная.

---
# Этап 8: перемещение по городу (models/movement/<тема>/, скрипты src/build_move_a.py ...)
Соглашения те же: метры, перёд +Z, начало на основании, state_ok/state_loose/state_broken, ip_use/ip_hit/ip_hand/ip_spark, `*-col` / `*-convcol`, циклические анимации с `_loop`.

## Группа A
| Тема | Файлы | Заметки |
|---|---|---|
| steps | bin_step_s (0,95 м), bin_step_m (1,2 м), bin_step_l (1,45 м), crate_step_50 / 80 / 110, crate_stair (1+2+3 ящика) | бак: state_ok (крышка закрыта), state_loose (продавленная крышка), `lid_anim` (отдельная крышка, анимации lid_clang, lid_open), жёлтая полоса, ip_use на крышке, ip_hand на бортике |
| fences | fence_low_picket (1,1 м), fence_low_concrete (1,2), fence_mid_profnastil (1,8), fence_mid_chainlink (1,8), fence_high_barbed (2,4+колючка; state_loose: на колючке тряпка, ip_spark), fence_bars (2,0, прутья через 0,12), fence_park_iron (копья, шары на столбах), fence_loose_board (state_loose: отогнутая доска), fence_post, fence_corner, gate_picket_closed (анимация open) / gate_picket_open | секция 2,5 м, ip_hand по верху |
| doors | door_emergency | запасной выход: дверь без ручки снаружи, push bar внутри; state_ok/state_loose, door_anim (open наружу, close), push_bar_anim (push_bar_press), красная лампа `beacon` (beacon_loop), зелёная плашка «ЗАПАСНОЙ ВЫХОД» (эмиссия, без текста: пиктограмма), звонок |
| roofs | roof_tile_bitumen / slate / gravel / wet / planks (state_ok / state_loose: просевшая доска), roof_parapet | плитка 4×4 м, материалы roof_bitumen, roof_slate, roof_gravel, roof_wet, roof_planks |
| passage | arch_passage_brick / arch_passage_panel (проезд 3,3×3,2 м, камера sweep_loop над аркой), gate_yard_closed (анимация open) / open / code (панель с цифрами) / welded / chain (цепь и замок), item_padlock_{closed,open,broken}_{hand,ground}, intercom_panel (12 клавиш, state_ok: табло горит, state_loose: погасло, анимация press) | |
| vehicles_extras | decal_footprint, car_dent_overlays | и в самих легковых (пересобраны): `alarm_lamps` (анимация alarm_loop мигает масштабом), `state_dent_hood`, `state_dent_roof` (игра включает видимость), ip_hand_hood. Просвет под van_gazelle ≈0,5 м, под truck_zil ≈0,5 м: мосты, карданный вал, баки, рессоры читаются |

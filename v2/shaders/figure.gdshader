shader_type canvas_item;
// Палитра фигуры: R = материал * 16 + 8 (0 — пусто), G = яркость. Материалы см. tools/art/common.py.
// Листы людей хранятся в RG8, поэтому прозрачность берётся из R.
uniform vec4 pal[12];
uniform vec4 tint : source_color = vec4(1.0);
uniform float flash = 0.0;      // подсветка (наведение)
uniform vec4 flash_col : source_color = vec4(0.85, 0.71, 0.25, 1.0);
uniform int pattern = 0;        // узор верхней одежды: 1 полоска, 2 поперечная, 3 клетка, 4 твид, 5 ёлочка

void fragment() {
	vec4 t = texture(TEXTURE, UV);
	float a = step(0.01, t.r);
	int m = int(floor(t.r * 255.0 / 16.0));
	m = clamp(m, 0, 11);
	float s = t.g * 1.25;
	vec3 base = pal[m].rgb;
	if (m == 2 && pattern > 0) {
		vec2 tp = floor(UV / TEXTURE_PIXEL_SIZE);
		float k = 0.0;
		if (pattern == 1) {
			k = step(mod(tp.x, 4.0), 0.5);
		} else if (pattern == 2) {
			k = step(mod(tp.y, 4.0), 0.5);
		} else if (pattern == 3) {
			k = max(step(mod(tp.x, 6.0), 0.5), step(mod(tp.y, 6.0), 0.5));
		} else if (pattern == 4) {
			k = step(0.72, fract(sin(dot(tp, vec2(12.9898, 78.233))) * 43758.5453));
		} else {
			k = step(mod(tp.x + tp.y, 5.0), 0.5);
		}
		base = mix(base, pal[10].rgb, k * 0.6);
	}
	vec3 c = base * s;
	c *= tint.rgb;
	c = mix(c, flash_col.rgb, flash * 0.55);
	COLOR = vec4(c, a * tint.a * COLOR.a);
}

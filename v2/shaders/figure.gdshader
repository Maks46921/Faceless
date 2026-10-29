shader_type canvas_item;
// Палитра фигуры: R = материал * 16 + 8, G = яркость. Материалы см. tools/art/common.py.
uniform vec4 pal[12];
uniform vec4 tint : source_color = vec4(1.0);
uniform float flash = 0.0;      // подсветка (наведение)
uniform vec4 flash_col : source_color = vec4(0.85, 0.71, 0.25, 1.0);

void fragment() {
	vec4 t = texture(TEXTURE, UV);
	int m = int(floor(t.r * 255.0 / 16.0));
	m = clamp(m, 0, 11);
	float s = t.g * 1.25;
	vec3 c = pal[m].rgb * s;
	c *= tint.rgb;
	c = mix(c, flash_col.rgb, flash * 0.55);
	COLOR = vec4(c, t.a * tint.a * COLOR.a);
}

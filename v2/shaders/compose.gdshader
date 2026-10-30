shader_type canvas_item;
// Сборка кадра мира: дальний план, интерьеры со своим светом, улица со своим светом.
uniform sampler2D far_tex : filter_nearest;
uniform sampler2D in_tex : filter_nearest;
uniform sampler2D out_tex : filter_nearest;
uniform sampler2D lin_tex : filter_linear;
uniform sampler2D lout_tex : filter_linear;
uniform vec3 amb_in = vec3(0.0);
uniform vec3 amb_out = vec3(0.0);
uniform float sat = 0.62;          // «чужие глаза»: мир серее
uniform float spirit = 0.0;        // вне тела
uniform float hurt = 0.0;          // плотность падает
uniform float fade = 0.0;          // помехи памяти
uniform float time_s = 0.0;
uniform vec2 sub_off = vec2(0.0);  // дробный сдвиг камеры в текселях мира
uniform vec2 tex_size = vec2(1288.0, 728.0);
uniform float margin = 4.0;        // запас по краям буфера, текселей

vec3 grade(vec3 c) {
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	// золото и красный сохраняют цвет
	float gold = smoothstep(0.25, 0.05, distance(normalize(c + 0.001), normalize(vec3(0.85, 0.71, 0.25)))) * step(0.3, l);
	float s = mix(sat, 1.0, gold);
	return mix(vec3(l), c, s);
}

void fragment() {
	vec2 uv = UV;
	vec2 px = 1.0 / tex_size;
	uv = (uv * (tex_size - 2.0 * margin) + margin + sub_off) * px;
	if (spirit > 0.0) {
		uv.x += sin(uv.y * 60.0 + time_s * 2.0) * 0.0009 * spirit;
	}
	vec4 far = texture(far_tex, uv);
	vec4 inn = texture(in_tex, uv);
	vec4 outr = texture(out_tex, uv);
	vec3 li = amb_in + texture(lin_tex, uv).rgb * 2.0;
	vec3 lo = amb_out + texture(lout_tex, uv).rgb * 2.0;
	vec3 c = far.rgb;
	c = mix(c, inn.rgb * li, inn.a);
	c = mix(c, outr.rgb * lo, outr.a);
	c = grade(c);
	// дух: холодно, темнее по краям
	vec2 q = UV - 0.5;
	float vig = smoothstep(0.85, 0.25, length(q * vec2(1.0, 1.25)));
	vec3 cold = vec3(dot(c, vec3(0.3, 0.55, 0.15))) * vec3(0.78, 0.86, 1.05);
	c = mix(c, cold, spirit * 0.55);
	c *= mix(1.0, vig, 0.35 + spirit * 0.35);
	// боль: красноватая пульсация по краям
	c = mix(c, c * vec3(1.15, 0.6, 0.6), hurt * (1.0 - vig) * (0.6 + 0.4 * sin(time_s * 9.0)));
	// помехи памяти
	if (fade > 0.0) {
		float n = fract(sin(dot(floor(UV * vec2(160.0, 90.0)) + floor(time_s * 12.0), vec2(12.9898, 78.233))) * 43758.5453);
		c += (n - 0.5) * 0.12 * fade;
	}
	COLOR = vec4(c, 1.0);
}

<?php
/**
 * Plugin Name:       Door Intro
 * Description:       Cinematic "opening doors" entrance that reveals a founder photo, then fades into the existing site. Theme-safe: adds one deferred script and never modifies page content.
 * Version:           1.0.0
 * Requires at least: 6.3
 * Requires PHP:      7.4
 * License:           MIT
 * Text Domain:       door-intro
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'DOOR_INTRO_VERSION', '1.0.0' );
define( 'DOOR_INTRO_OPTION', 'door_intro_options' );

/**
 * Settings with their defaults. Keys map 1:1 to the JavaScript options.
 */
function door_intro_defaults() {
	return array(
		'enabled'      => 1,
		'prepaint'     => 1,
		'preset'       => 'opendoors',
		'brandName'    => '',
		'logoUrl'      => '',
		'imageUrl'     => '',
		'imageAlt'     => '',
		'welcomeText'  => '',
		'revealText'   => '',
		'primaryColor' => '',
		'accentColor'  => '',
		'accentColor2' => '',
		'doorStyle'    => 'classic',
		'duration'     => 4500,
		'playMode'     => 'session',
		'replayButton' => 'floating',
		'frontOnly'    => 0,
	);
}

function door_intro_options() {
	$saved = get_option( DOOR_INTRO_OPTION, array() );
	return wp_parse_args( is_array( $saved ) ? $saved : array(), door_intro_defaults() );
}

/**
 * Only on real front-end page views.
 */
function door_intro_should_load( $opts ) {
	if ( empty( $opts['enabled'] ) || is_admin() || is_feed() || is_embed() || is_customize_preview() || wp_doing_ajax() ) {
		return false;
	}
	if ( defined( 'REST_REQUEST' ) && REST_REQUEST ) {
		return false;
	}
	if ( ! empty( $opts['frontOnly'] ) && ! is_front_page() ) {
		return false;
	}
	return (bool) apply_filters( 'door_intro_enabled', true );
}

/**
 * Builds the JS config. Empty strings are dropped so preset values apply.
 */
function door_intro_js_config( $opts ) {
	$config = array();
	foreach ( $opts as $key => $value ) {
		if ( in_array( $key, array( 'enabled', 'prepaint', 'frontOnly' ), true ) || '' === $value ) {
			continue;
		}
		$config[ $key ] = $value;
	}
	$config['duration'] = (int) $opts['duration'];
	return apply_filters( 'door_intro_config', $config );
}

add_action(
	'wp_enqueue_scripts',
	function () {
		$opts = door_intro_options();
		if ( ! door_intro_should_load( $opts ) ) {
			return;
		}
		wp_register_script(
			'door-intro',
			plugins_url( 'assets/door-intro.js', __FILE__ ),
			array(),
			DOOR_INTRO_VERSION,
			array(
				'in_footer' => false,
				'strategy'  => 'defer',
			)
		);
		wp_add_inline_script( 'door-intro', 'window.DoorIntroConfig = ' . wp_json_encode( door_intro_js_config( $opts ) ) . ';', 'before' );
		wp_enqueue_script( 'door-intro' );
	}
);

/**
 * Pre-paint guard: paints the intro background before the deferred script
 * runs so there is no flash of the page. Removes itself after 3 seconds even
 * if the script never loads. Skipped for returning visitors in this session.
 */
add_action(
	'wp_head',
	function () {
		$opts = door_intro_options();
		if ( empty( $opts['prepaint'] ) || ! door_intro_should_load( $opts ) || 'manual' === $opts['playMode'] ) {
			return;
		}
		$color   = $opts['primaryColor'] ? $opts['primaryColor'] : ( 'opendoors' === $opts['preset'] ? '#080808' : '#0e0f12' );
		$color   = sanitize_hex_color( $color ) ? sanitize_hex_color( $color ) : '#080808';
		$storage = 'once' === $opts['playMode'] ? 'localStorage' : 'sessionStorage';
		$always  = 'always' === $opts['playMode'] ? 'true' : 'false';
		$img     = $opts['imageUrl'] ? esc_url_raw( $opts['imageUrl'] ) : '';

		echo '<style id="door-intro-prepaint">html.door-intro-pending::before{content:"";position:fixed;inset:0;z-index:2147483000;background:' . esc_html( $color ) . ';animation:door-intro-failsafe 0s linear 3s forwards}@keyframes door-intro-failsafe{to{visibility:hidden}}</style>' . "\n";
		$js = '(function(){var img=' . wp_json_encode( $img ) . ';try{var q=location.search,f=/[?&]doorintro=([^&]*)/i.exec(q);if(f){if(/^(0|off|false|no)$/i.test(f[1]))return}else if(/bot\\b|crawler|spider|slurp|bingpreview|facebookexternalhit/i.test(navigator.userAgent)||(!' . $always . '&&' . $storage . '.getItem("door-intro:seen")))return;document.documentElement.className+=" door-intro-pending";if(img){var l=document.createElement("link");l.rel="preload";l.as="image";l.href=img;l.setAttribute("fetchpriority","high");document.head.appendChild(l)}}catch(e){}})();';
		wp_print_inline_script_tag( $js, array( 'id' => 'door-intro-prepaint-js' ) );
	},
	1
);

/* ------------------------------------------------------------- settings */

add_action(
	'admin_menu',
	function () {
		add_options_page( __( 'Door Intro', 'door-intro' ), __( 'Door Intro', 'door-intro' ), 'manage_options', 'door-intro', 'door_intro_settings_page' );
	}
);

add_action(
	'admin_init',
	function () {
		register_setting(
			'door_intro',
			DOOR_INTRO_OPTION,
			array(
				'type'              => 'array',
				'sanitize_callback' => 'door_intro_sanitize',
				'default'           => door_intro_defaults(),
			)
		);
	}
);

function door_intro_sanitize( $input ) {
	$d   = door_intro_defaults();
	$in  = is_array( $input ) ? $input : array();
	$out = array();

	foreach ( array( 'enabled', 'prepaint', 'frontOnly' ) as $k ) {
		$out[ $k ] = empty( $in[ $k ] ) ? 0 : 1;
	}
	foreach ( array( 'logoUrl', 'imageUrl' ) as $k ) {
		$out[ $k ] = isset( $in[ $k ] ) ? esc_url_raw( trim( $in[ $k ] ) ) : '';
	}
	foreach ( array( 'brandName', 'imageAlt', 'welcomeText', 'revealText' ) as $k ) {
		$out[ $k ] = isset( $in[ $k ] ) ? sanitize_text_field( $in[ $k ] ) : '';
	}
	foreach ( array( 'primaryColor', 'accentColor', 'accentColor2' ) as $k ) {
		$out[ $k ] = isset( $in[ $k ] ) && sanitize_hex_color( $in[ $k ] ) ? sanitize_hex_color( $in[ $k ] ) : '';
	}
	$choices = array(
		'preset'       => array( 'opendoors', 'neutral' ),
		'doorStyle'    => array( 'classic', 'modern', 'glass' ),
		'playMode'     => array( 'session', 'once', 'always', 'manual' ),
		'replayButton' => array( 'floating', 'none' ),
	);
	foreach ( $choices as $k => $allowed ) {
		$out[ $k ] = isset( $in[ $k ] ) && in_array( $in[ $k ], $allowed, true ) ? $in[ $k ] : $d[ $k ];
	}
	$out['duration'] = isset( $in['duration'] ) ? max( 2500, min( 8000, (int) $in['duration'] ) ) : $d['duration'];
	return $out;
}

function door_intro_settings_page() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$o    = door_intro_options();
	$name = DOOR_INTRO_OPTION;
	$text = array(
		'brandName'    => __( 'Brand name (blank = preset)', 'door-intro' ),
		'logoUrl'      => __( 'Logo URL (SVG or transparent PNG)', 'door-intro' ),
		'imageUrl'     => __( 'Founder / hero image URL (copy from Media Library)', 'door-intro' ),
		'imageAlt'     => __( 'Image alt text', 'door-intro' ),
		'welcomeText'  => __( 'Welcome text (blank = preset)', 'door-intro' ),
		'revealText'   => __( 'Reveal text (blank = preset)', 'door-intro' ),
		'primaryColor' => __( 'Primary color (#hex, blank = preset)', 'door-intro' ),
		'accentColor'  => __( 'Accent color (#hex)', 'door-intro' ),
		'accentColor2' => __( 'Secondary accent (#hex)', 'door-intro' ),
	);
	$selects = array(
		'preset'       => array( __( 'Preset', 'door-intro' ), array( 'opendoors', 'neutral' ) ),
		'doorStyle'    => array( __( 'Door style', 'door-intro' ), array( 'classic', 'modern', 'glass' ) ),
		'playMode'     => array( __( 'Play', 'door-intro' ), array( 'session', 'once', 'always', 'manual' ) ),
		'replayButton' => array( __( 'Replay button', 'door-intro' ), array( 'floating', 'none' ) ),
	);
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Door Intro', 'door-intro' ); ?></h1>
		<p><?php esc_html_e( 'Preview any page with ?doorintro=1 to force the intro, or ?doorintro=0 to disable it.', 'door-intro' ); ?></p>
		<form method="post" action="options.php">
			<?php settings_fields( 'door_intro' ); ?>
			<table class="form-table" role="presentation">
				<?php foreach ( array( 'enabled' => __( 'Enable intro', 'door-intro' ), 'prepaint' => __( 'Pre-paint guard (prevents a flash of the page)', 'door-intro' ), 'frontOnly' => __( 'Home page only', 'door-intro' ) ) as $k => $label ) : ?>
					<tr><th scope="row"><?php echo esc_html( $label ); ?></th>
						<td><input type="checkbox" name="<?php echo esc_attr( "{$name}[{$k}]" ); ?>" value="1" <?php checked( 1, (int) $o[ $k ] ); ?> /></td></tr>
				<?php endforeach; ?>
				<?php foreach ( $selects as $k => $sel ) : ?>
					<tr><th scope="row"><label for="di-<?php echo esc_attr( $k ); ?>"><?php echo esc_html( $sel[0] ); ?></label></th>
						<td><select id="di-<?php echo esc_attr( $k ); ?>" name="<?php echo esc_attr( "{$name}[{$k}]" ); ?>">
							<?php foreach ( $sel[1] as $v ) : ?>
								<option value="<?php echo esc_attr( $v ); ?>" <?php selected( $o[ $k ], $v ); ?>><?php echo esc_html( $v ); ?></option>
							<?php endforeach; ?>
						</select></td></tr>
				<?php endforeach; ?>
				<?php foreach ( $text as $k => $label ) : ?>
					<tr><th scope="row"><label for="di-<?php echo esc_attr( $k ); ?>"><?php echo esc_html( $label ); ?></label></th>
						<td><input class="regular-text" type="text" id="di-<?php echo esc_attr( $k ); ?>" name="<?php echo esc_attr( "{$name}[{$k}]" ); ?>" value="<?php echo esc_attr( $o[ $k ] ); ?>" /></td></tr>
				<?php endforeach; ?>
				<tr><th scope="row"><label for="di-duration"><?php esc_html_e( 'Duration (ms, 2500–8000)', 'door-intro' ); ?></label></th>
					<td><input type="number" min="2500" max="8000" step="100" id="di-duration" name="<?php echo esc_attr( "{$name}[duration]" ); ?>" value="<?php echo esc_attr( $o['duration'] ); ?>" /></td></tr>
			</table>
			<?php submit_button(); ?>
		</form>
	</div>
	<?php
}
